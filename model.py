"""Modèles IA Yélé : détection d'anomalies + prédiction de qualité.

Trois niveaux complémentaires :
 1. Statistique (IQR par opérateur)      -> marche dès ~30 mesures
 2. Isolation Forest multivarié          -> anomalies de combinaison (dl/ping/…)
 3. Régression (gradient boosting)       -> qualité attendue par contexte ;
    l'écart mesuré-prédit (résidu) donne l'anomalie *contextuelle*
    et le modèle sert aussi à la prévision (forecast).
"""

import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import HistGradientBoostingRegressor, IsolationForest

# TabPFN : modèle de fondation tabulaire, déjà pré-entraîné, pensé pour les
# PETITS jeux de données (< 1000 lignes) — donc idéal ici. On le préfère au
# gradient boosting quand il est installé ; sinon on retombe sur sklearn.
try:
    from tabpfn import TabPFNRegressor
    _HAS_TABPFN = True
except ImportError:
    _HAS_TABPFN = False


def _make_regressor():
    """Régresseur de prédiction du débit : TabPFN si dispo, sinon sklearn."""
    if _HAS_TABPFN:
        # ignore_pretraining_limits : autorise nos features même si le contexte
        # est petit ; TabPFN reste déterministe (pas de random_state requis).
        return TabPFNRegressor(ignore_pretraining_limits=True)
    return HistGradientBoostingRegressor(random_state=42)


# ECOD : détecteur d'anomalies sans paramètre, déterministe et EXPLICABLE
# (il dit quelle variable rend une mesure anormale). Préféré à Isolation Forest
# quand PyOD est installé ; sinon on retombe sur Isolation Forest.
try:
    from pyod.models.ecod import ECOD
    _HAS_ECOD = True
except ImportError:
    _HAS_ECOD = False


def _make_detector():
    """Détecteur d'anomalies + son nom : ECOD si dispo, sinon Isolation Forest."""
    if _HAS_ECOD:
        return ECOD(contamination=CONTAMINATION), "ECOD"
    return IsolationForest(n_estimators=200, contamination=CONTAMINATION,
                           random_state=42), "Isolation Forest"

KPI = ["dl", "ul", "ping", "jitter"]
FEATURES = ["hour", "dayofweek", "is_weekend", "op_code", "net_code"]
MIN_SAMPLES_ML = 50          # en dessous : méthodes statistiques uniquement
CONTAMINATION = 0.03         # part d'anomalies attendue (Isolation Forest)

# Champs personnels : jamais extraits.
PII_PROJECTION = {
    "_id": 0, "ip_address": 0, "isp_info": 0, "log": 0,
    "extra_raw": 0, "user_agent": 0, "language": 0,
}

# Fusion des libellés d'opérateur en doublon (mêmes règles que prepare_data.py).
# Sans cela, "ONATEL (…" et "ONATEL (…, PTT)" sont traités comme deux opérateurs.
# Libellés canoniques = référentiel ARCEP, comme partout dans le projet
# (décision du 13/11 — le dashboard n'a plus à normaliser à l'affichage).
OPERATOR_ALIASES = [
    ("office national des telecommunications", "Moov Africa SA"),
    ("onatel", "Moov Africa SA"),
    ("telmob", "Moov Africa SA"),
    ("moov", "Moov Africa SA"),
    ("orange burkina", "Orange BF SA"),
    ("orange", "Orange BF SA"),
    ("telecel", "Telecel Faso SA"),
    ("anptic", "ANPTIC"),
    ("agence nationale de promotion des tic", "ANPTIC"),
    ("autorite de regulation des communications", "ARCEP Burkina"),
]


def _canon_operator(name: str) -> str:
    """Ramène chaque variante d'écriture au libellé canonique."""
    if not isinstance(name, str) or not name:
        return name
    low = name.lower()
    for motif, canonique in OPERATOR_ALIASES:
        if motif in low:
            return canonique
    return name.strip()


def _fetch_from_api(base_url: str = "http://localhost:8989") -> list[dict]:
    """Fallback : récupère les résultats via l'API du backend Go."""
    import urllib.request, json
    page, all_docs = 1, []
    while True:
        url = f"{base_url}/api/dashboard/results?page={page}&limit=200"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except Exception:
            break
        rows = data.get("data", [])
        if not rows:
            break
        all_docs.extend(rows)
        if len(all_docs) >= data.get("total", 0):
            break
        page += 1
    return all_docs


def load_dataframe() -> pd.DataFrame:
    """Extraction MongoDB (sans PII) + nettoyage, comme prepare_data.py."""
    docs = []
    # Essai MongoDB direct d'abord
    uri = os.environ.get("SPEEDTEST_DATABASE_CONNECTION_STRING")
    if uri:
        try:
            db = os.environ.get("SPEEDTEST_DATABASE_NAME", "yele_speedtest")
            client = MongoClient(uri, serverSelectionTimeoutMS=15000)
            client.admin.command("ping")
            docs = list(client[db]["speedtest_results"].find({}, PII_PROJECTION))
            client.close()
        except Exception as e:
            print(f"[AI] MongoDB direct indisponible ({e}), fallback via API Go")
    # Fallback via l'API du backend Go si MongoDB direct échoue
    if not docs:
        try:
            docs = _fetch_from_api()
        except Exception as e:
            print(f"[AI] API Go inaccessible : {e}")
    df = pd.DataFrame(_normalize_docs(docs))
    if df.empty:
        return df

    for col in KPI:
        df[col] = pd.to_numeric(df.get(col), errors="coerce")
    df["timestamp"] = pd.to_datetime(df.get("timestamp"), errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp", "dl"])
    # Débit 0 = speedtest absent/échoué (souvent une session streaming seule) : exclu.
    df = df[(df["dl"] > 0) & (df["dl"] < 2000)]

    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
    for col in ["operator", "network_type"]:
        df[col] = df.get(col, "").fillna("Inconnu").replace("", "Inconnu")
    # Fusion des opérateurs en doublon (ONATEL ×2, ANPTIC/ARCEP en toutes lettres…).
    df["operator"] = df["operator"].map(_canon_operator)

    # Analyse MOBILE STRICTEMENT (Option B, décision du 13/11) : le service IA
    # ne retient que les tests cellulaires 2G/3G/4G/5G (les tests WiFi/fixe
    # sortent du périmètre — la prévision et le niveau multivarié restent
    # donc hors service tant que le mobile n'atteint pas MIN_SAMPLES_ML).
    df = df[df["network_type"].str.match(r"^(2G|3G|4G|5G|mobile)\+?$", case=False, na=False)]

    # Colonnes descriptives pour le tableau des anomalies (dashboard) : elles
    # ne servent PAS aux modèles, on les porte juste jusqu'à la sortie JSON.
    df["tech"] = df.get("cellular_tech", "").fillna("")
    df.loc[~df["tech"].str.match(r"^[2-5]G\+?$", case=False, na=False), "tech"] = df["network_type"]
    df["device"] = df.get("device_model", "").fillna("")
    df["location"] = df.get("location", "").fillna("")
    for c in ["latitude", "longitude"]:
        df[c] = pd.to_numeric(df.get(c), errors="coerce")
    # Signal consolidé, mêmes règles que le backend (ISS-01) : RSRP 4G puis
    # repli NR (5G SA) puis signal_dbm historique ; RSRQ 4G puis repli NR.
    for src, dst in [("signal_rsrp", "rsrp"), ("signal_rsrq", "rsrq")]:
        s = pd.to_numeric(df.get(src), errors="coerce")
        nr = pd.to_numeric(df.get("signal_nr_" + src.split("_")[1]), errors="coerce")
        s = s.fillna(nr)
        if dst == "rsrp":
            s = s.fillna(pd.to_numeric(df.get("signal_dbm"), errors="coerce")
                         .where(df["network_type"].str.match(r"^[2-5]G", case=False, na=False)))
        df[dst] = s
    return df.reset_index(drop=True)


# L'API Go renvoie du camelCase (json), Mongo du snake_case (bson) : on ramène
# tout à un schéma commun avant de construire le DataFrame.
_DOC_KEY_ALIASES = {
    "download": "dl", "upload": "ul",
    "networkType": "network_type", "cellularTech": "cellular_tech",
    "deviceModel": "device_model", "simOperator": "sim_operator",
    "signalRsrp": "signal_rsrp", "signalNrRsrp": "signal_nr_rsrp",
    "signalRsrq": "signal_rsrq", "signalNrRsrq": "signal_nr_rsrq",
}


def _normalize_docs(docs: list[dict]) -> list[dict]:
    for d in docs:
        for src, dst in _DOC_KEY_ALIASES.items():
            if src in d and dst not in d:
                d[dst] = d[src]
    return docs


class YeleAI:
    """Entraîne et applique les trois niveaux de détection + la prévision."""

    def __init__(self) -> None:
        self.n_samples = 0
        self.ml_ready = False
        self.operators: list[str] = []
        self.networks: list[str] = []
        self.group_stats: dict = {}
        self.detector = None            # ECOD ou Isolation Forest
        self.detector_name = ""
        self.det_threshold = 0.0        # seuil de score au-dessus duquel = anomalie
        self.det_scoremax = 1.0         # score max observé (pour normaliser la sévérité)
        self.kpi_train = None           # valeurs KPI d'entraînement (CDF empirique)
        self.reg: HistGradientBoostingRegressor | None = None
        self.resid_std = 0.0

    # ── Entraînement ─────────────────────────────────────────────────────────

    def train(self, df: pd.DataFrame) -> None:
        self.n_samples = len(df)
        if df.empty:
            return

        # Encodage catégoriel stable (index dans la liste)
        self.operators = sorted(df["operator"].unique().tolist())
        self.networks = sorted(df["network_type"].unique().tolist())

        # 1) Stats par opérateur (médiane / IQR) — repli et explications
        for op, g in df.groupby("operator"):
            self.group_stats[op] = {
                "count": int(len(g)),
                "dl_median": float(g["dl"].median()),
                "dl_q1": float(g["dl"].quantile(0.25)),
                "dl_q3": float(g["dl"].quantile(0.75)),
                # Percentile 5 : seuil bas robuste. Contrairement à Q1−1,5·IQR
                # (qui suppose une distribution symétrique et devenait négatif
                # ici), le P05 reste toujours une valeur de débit plausible.
                "dl_q05": float(g["dl"].quantile(0.05)),
                "ping_median": float(g["ping"].median()) if g["ping"].notna().any() else None,
            }

        if len(df) < MIN_SAMPLES_ML:
            return  # trop peu de données pour le ML : stats uniquement

        # 2) Détecteur multivarié sur les KPI (ECOD, sinon Isolation Forest)
        x_kpi = df[KPI].fillna(df[KPI].median())
        self.detector, self.detector_name = _make_detector()
        self.detector.fit(x_kpi)
        self.kpi_train = x_kpi.to_numpy()               # pour l'explicabilité ECOD
        train_scores = self._detector_scores(x_kpi)     # scores d'anomalie
        # Seuil = quantile (1 - contamination) ; sert aussi à normaliser la sévérité.
        self.det_threshold = float(np.quantile(train_scores, 1 - CONTAMINATION))
        self.det_scoremax = float(max(train_scores.max(), self.det_threshold + 1e-6))

        # 3) Régression : débit attendu selon le contexte
        x = self._features(df)
        y = df["dl"]
        self.reg = _make_regressor().fit(x, y)
        resid = y - self.reg.predict(x)
        self.resid_std = float(max(resid.std(), 1e-6))
        self.ml_ready = True

    def _features(self, df: pd.DataFrame) -> np.ndarray:
        op = df["operator"].map(lambda v: self.operators.index(v)
                                if v in self.operators else -1)
        net = df["network_type"].map(lambda v: self.networks.index(v)
                                     if v in self.networks else -1)
        return np.column_stack([
            df["hour"], df["dayofweek"], df["is_weekend"], op, net,
        ]).astype(float)

    def _detector_scores(self, x_kpi: pd.DataFrame) -> np.ndarray:
        """Score d'anomalie unifié (grand = anormal), quel que soit le détecteur."""
        if self.detector_name == "Isolation Forest":
            return -self.detector.decision_function(x_kpi)  # sklearn : grand = normal
        return self.detector.decision_function(x_kpi)       # ECOD/PyOD : grand = anormal

    def _kpi_contributions(self, values: np.ndarray) -> np.ndarray:
        """Part de chaque KPI dans l'anomalie (façon ECOD : queues empiriques).

        Pour chaque variable, on mesure à quel point la valeur est extrême dans
        la distribution d'entraînement (queue basse OU haute), en -log(proba).
        Sert à dire « c'est le ping qui est aberrant » — l'atout d'ECOD.
        """
        n = len(self.kpi_train)
        contrib = np.zeros(len(KPI))
        for j in range(len(KPI)):
            col = self.kpi_train[:, j]
            v = values[j]
            left = (col <= v).sum() / n          # proba d'être aussi bas
            right = (col >= v).sum() / n         # proba d'être aussi haut
            tail = max(min(left, right), 1.0 / n)
            contrib[j] = -np.log(tail)
        return contrib

    # ── Détection ────────────────────────────────────────────────────────────

    def detect(self, df: pd.DataFrame, limit: int = 50) -> list[dict]:
        """Score les mesures et retourne les anomalies (les pires d'abord)."""
        if df.empty:
            return []
        df = df.copy()

        # Niveau 1 : statistique par opérateur (percentile bas)
        reasons: list[list[str]] = [[] for _ in range(len(df))]
        severity = np.zeros(len(df))
        for i, row in enumerate(df.itertuples()):
            st = self.group_stats.get(row.operator)
            if not st or st["count"] < 5:
                continue
            # Seuil bas = percentile 5 de l'opérateur (robuste à l'asymétrie).
            low = st.get("dl_q05", st["dl_q1"] - 1.5 * (st["dl_q3"] - st["dl_q1"]))
            if row.dl < low:
                severity[i] += 40
                reasons[i].append(
                    f"Débit {row.dl:.1f} Mb/s très en dessous de la normale "
                    f"de {row.operator} (médiane {st['dl_median']:.1f} Mb/s)")
            if st["ping_median"] and row.ping and row.ping > 4 * st["ping_median"]:
                severity[i] += 20
                reasons[i].append(
                    f"Latence {row.ping:.0f} ms ≈ {row.ping / st['ping_median']:.0f}× "
                    f"la médiane de {row.operator}")

        # Niveau 2 : détecteur multivarié (profil global aberrant)
        if self.detector is not None:
            x_kpi = df[KPI].fillna(df[KPI].median())
            scores = self._detector_scores(x_kpi)          # grand = anormal
            span = self.det_scoremax - self.det_threshold
            x_vals = x_kpi.to_numpy()
            for i in range(len(df)):
                if scores[i] >= self.det_threshold:
                    norm = min(max((scores[i] - self.det_threshold) / span, 0), 1)
                    severity[i] += 30 + 30 * norm
                    # Explicabilité ECOD : la ou les variables qui dominent.
                    if self.detector_name == "ECOD" and self.kpi_train is not None:
                        c = self._kpi_contributions(x_vals[i])
                        total = c.sum()
                        if total > 0:
                            top = c.argsort()[::-1]
                            parts = [f"{KPI[j]} {100 * c[j] / total:.0f} %"
                                     for j in top[:2] if c[j] / total >= 0.15]
                            reasons[i].append(
                                "Combinaison atypique (ECOD) — dominé par "
                                + ", ".join(parts) if parts else
                                "Combinaison de mesures atypique (ECOD)")
                    else:
                        reasons[i].append(
                            f"Combinaison de mesures atypique ({self.detector_name})")

        # Niveau 3 : anomalie contextuelle (écart au débit prédit)
        if self.ml_ready:
            pred = self.reg.predict(self._features(df))
            resid = df["dl"].to_numpy() - pred
            for i in range(len(df)):
                # −1,5σ : un débit nettement sous la prédiction du contexte.
                # (−3σ exigeait un écart irréaliste vu la dispersion des données.)
                if resid[i] < -1.5 * self.resid_std:
                    severity[i] += 30
                    reasons[i].append(
                        f"Débit {df['dl'].iat[i]:.1f} Mb/s alors que "
                        f"{pred[i]:.1f} Mb/s était attendu pour ce contexte")

        out = []
        for i, row in enumerate(df.itertuples()):
            if severity[i] <= 0:
                continue
            out.append({
                "timestamp": row.timestamp.isoformat(),
                "operator": row.operator,
                "networkType": row.network_type,
                "tech": getattr(row, "tech", "") or row.network_type,
                "download": round(float(row.dl), 2),
                "upload": round(float(row.ul), 2) if pd.notna(getattr(row, "ul", None)) else None,
                "ping": round(float(row.ping), 1) if pd.notna(row.ping) else None,
                "jitter": round(float(row.jitter), 1) if pd.notna(getattr(row, "jitter", None)) else None,
                "rsrp": int(row.rsrp) if pd.notna(getattr(row, "rsrp", None)) else None,
                "rsrq": int(row.rsrq) if pd.notna(getattr(row, "rsrq", None)) else None,
                "device": getattr(row, "device", "") or None,
                "location": getattr(row, "location", "") or None,
                "lat": float(row.latitude) if pd.notna(getattr(row, "latitude", None)) else None,
                "lng": float(row.longitude) if pd.notna(getattr(row, "longitude", None)) else None,
                "severity": int(min(severity[i], 100)),
                "reasons": reasons[i],
            })
        out.sort(key=lambda a: a["severity"], reverse=True)
        return out[:limit]

    # ── Prévision ────────────────────────────────────────────────────────────

    def forecast(self, operator: str, hours: int = 48,
                 network_type: str | None = None) -> list[dict]:
        """Débit prédit heure par heure pour un opérateur (contexte futur)."""
        if not self.ml_ready or operator not in self.operators:
            return []
        # Technologie demandée (filtre du dashboard) sinon la plus courante
        # pour cet opérateur (contexte type).
        net = (network_type or "").upper()
        if not net or net not in self.networks:
            net = self.networks[0] if self.networks else "Inconnu"
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        rows = []
        for h in range(hours):
            t = now + timedelta(hours=h)
            rows.append({"hour": t.hour, "dayofweek": t.weekday(),
                         "is_weekend": int(t.weekday() >= 5),
                         "operator": operator, "network_type": net,
                         "timestamp": t})
        fdf = pd.DataFrame(rows)
        pred = self.reg.predict(self._features(fdf))
        return [
            {"time": r["timestamp"].isoformat(),
             "predictedDownload": round(float(max(p, 0)), 2)}
            for r, p in zip(rows, pred)
        ]
