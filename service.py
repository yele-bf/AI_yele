"""Service IA Yélé (FastAPI).

Endpoints (appelés par le backend Go via le proxy /api/ai/*) :
  GET  /ai/health     -> état du service et des modèles
  GET  /ai/anomalies  -> anomalies détectées sur les mesures récentes
  GET  /ai/forecast   -> débit prédit heure par heure pour un opérateur
  POST /ai/retrain    -> ré-entraîne les modèles sur les données actuelles

Lancement local :
    uvicorn service:app --reload --port 8000
"""

import threading
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Query

from model import MIN_SAMPLES_ML, YeleAI, load_dataframe

load_dotenv()

_state: dict = {"ai": None, "df": None, "trained_at": None, "error": None}
_lock = threading.Lock()


def _retrain() -> None:
    try:
        df = load_dataframe()
        ai = YeleAI()
        ai.train(df)
        with _lock:
            _state.update(ai=ai, df=df, trained_at=time.time(), error=None)
    except Exception as exc:  # service utilisable même si Mongo est down
        with _lock:
            _state["error"] = str(exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Entraînement initial en arrière-plan (ne bloque pas le démarrage).
    threading.Thread(target=_retrain, daemon=True).start()
    yield


app = FastAPI(title="Yélé AI", lifespan=lifespan)


@app.get("/ai/health")
def health():
    with _lock:
        ai: YeleAI | None = _state["ai"]
        return {
            "status": "ok" if ai else ("error" if _state["error"] else "training"),
            "error": _state["error"],
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
        return {"anomalies": [], "analyzed": 0, "mlReady": False}
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
    _retrain()
    return health()
