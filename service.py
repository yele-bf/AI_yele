"""Service IA Yélé (FastAPI).

Endpoints (appelés par le backend Go via le proxy /api/ai/*) :
  GET  /ai/health     -> état du service et des modèles
  GET  /ai/anomalies  -> anomalies détectées sur les mesures récentes
  GET  /ai/forecast   -> débit prédit heure par heure pour un opérateur
  POST /ai/retrain    -> relance l'entraînement (immédiat, en tâche de fond)

Démarrage à froid :
  1. si un modèle entraîné existe (yele_ai.joblib, fichier produit par
     train.py ou par POST /ai/retrain), il est chargé tel quel : le service
     est prêt en quelques secondes ;
  2. sinon (première mise en ligne, ou fichier absent/corrompu), les modèles
     sont entraînés sur les données MongoDB, comme avant, et sauvegardés
     pour les prochains démarrages.
  Dans les deux cas l'entraînement n'est plus lancé à chaque démarrage.

Lancement local :
    uvicorn service:app --reload --port 8000
"""

import os
import threading
import time
from contextlib import asynccontextmanager

import joblib
from dotenv import load_dotenv
from fastapi import FastAPI, Query

from model import MIN_SAMPLES_ML, YeleAI, load_dataframe

load_dotenv()

# Chemin du modèle persistant, surchargeable sans toucher au code.
MODEL_FILE = os.environ.get("SPEEDTEST_AI_MODEL_FILE", "yele_ai.joblib")

_state: dict = {
    "ai": None, "df": None, "trained_at": None, "error": None,
    # d'où vient le modèle chargé : "saved" (fichier), "train" (entraîné
    # à la volée) ou None tant que rien n'est prêt
    "source": None,
}
_lock = threading.Lock()


def _apply(ai: YeleAI, df, source: str) -> None:
    with _lock:
        _state.update(ai=ai, df=df, trained_at=time.time(),
                      error=None, source=source)


def _fail(message: str) -> None:
    with _lock:
        _state["error"] = str(message)


def _load_saved_model():
    """Charge le modèle persistant. Retourne (ai, erreur) ; ai=None si absent
    ou inexploitable (contenu inattendu, fichier corrompu…)."""
    if not os.path.exists(MODEL_FILE):
        return None, "fichier absent"
    try:
        ai = joblib.load(MODEL_FILE)
        if not isinstance(ai, YeleAI):
            return None, "contenu inattendu dans " + MODEL_FILE
        return ai, None
    except Exception as exc:  # fichier corrompu : on retombera sur l'entraînement
        return None, f"chargement impossible ({exc})"


def _startup() -> None:
    """Routine de démarrage (tâche de fond : ne bloque jamais le boot).

    1) modèle persistant présent et valide : on le charge, puis on charge
       les données (indispensables à /ai/anomalies) ;
    2) sinon : entraînement complet + sauvegarde du modèle pour les
       prochains démarrages.
    """
    ai, load_err = _load_saved_model()
    if ai is not None:
        try:
            df = load_dataframe()
        except Exception as exc:  # Mongo down : modèle prêt, données absentes
            _apply(ai, None, "saved")
            _fail(f"données indisponibles ({exc})")
            return
        _apply(ai, df, "saved")
        return
    # Modèle absent/corrompu : on note pourquoi, puis on entraîne.
    if load_err != "fichier absent":
        _fail(f"modèle persistant inutilisable : {load_err} — entraînement")
    _retrain()


def _retrain() -> None:
    """Entraîne sur les données actuelles puis sauvegarde le modèle.

    Toute erreur est enregistrée dans _state (le service reste joignable
    et répond « error » à /ai/health tant que rien n'est prêt).
    """
    try:
        df = load_dataframe()
        ai = YeleAI()
        ai.train(df)
        joblib.dump(ai, MODEL_FILE)
        _apply(ai, df, "train")
    except Exception as exc:
        _fail(exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Démarrage en tâche de fond (ne bloque pas le démarrage d'uvicorn).
    threading.Thread(target=_startup, daemon=True).start()
    yield


app = FastAPI(title="Yélé AI", lifespan=lifespan)


@app.get("/ai/health")
def health():
    with _lock:
        ai: YeleAI | None = _state["ai"]
        return {
            "status": "ok" if ai else ("error" if _state["error"] else "training"),
            "error": _state["error"],
            "source": _state["source"],
            "modelFile": MODEL_FILE,
            "samples": ai.n_samples if ai else 0,
            "mlReady": ai.ml_ready if ai else False,
            "minSamplesForMl": MIN_SAMPLES_ML,
            "trainedAt": _state["trained_at"],
            "operators": ai.operators if ai else [],
        }


@app.get("/ai/anomalies")
def anomalies(limit: int = Query(50, ge=1, le=200),
              days: int = Query(30, ge=1, le=365)):
    with _lock:
        ai, df = _state["ai"], _state["df"]
    if ai is None or df is None or df.empty:
        return {"anomalies": [], "analyzed": 0, "mlReady": bool(ai and ai.ml_ready)}
    cutoff = df["timestamp"].max() - __import__("pandas").Timedelta(days=days)
    recent = df[df["timestamp"] >= cutoff]
    return {
        "anomalies": ai.detect(recent, limit=limit),
        "analyzed": int(len(recent)),
        "mlReady": ai.ml_ready,
    }


@app.get("/ai/forecast")
def forecast(operator: str, hours: int = Query(48, ge=1, le=168),
             network_type: str = Query("", max_length=8)):
    with _lock:
        ai = _state["ai"]
    if ai is None:
        return {"forecast": [], "mlReady": False}
    return {
        "operator": operator,
        "forecast": ai.forecast(operator, hours=hours,
                                network_type=network_type or None),
        "mlReady": ai.ml_ready,
    }


@app.post("/ai/retrain")
def retrain():
    """Relance l'entraînement EN TÂCHE DE FOND (ne bloque plus la requête
    HTTP le temps de l'entraînement : la réponse part immédiatement, le
    résultat est suivi via /ai/health)."""
    threading.Thread(target=_retrain, daemon=True).start()
    resp = health()
    resp["status"] = "retraining"
    return resp
