"""
Predictions Router — Coruja Monitor v3.5 Enterprise
GET /api/v1/predictions — predições proativas de falha (horizonte 24h)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Metric, Sensor, Server
import time

router = APIRouter(prefix="/api/v1/predictions", tags=["Failure Predictions"])

# Importar predictor (lazy para não quebrar se numpy não estiver disponível)
_predictor = None

def _get_predictor():
    global _predictor
    if _predictor is None:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ai-agent"))
        from failure_predictor import FailurePredictor
        _predictor = FailurePredictor()
    return _predictor


@router.get("")
def get_predictions(
    hours: int = Query(24, le=24, description="Horizonte de predição em horas"),
    severity: str = Query(None, description="Filtrar por severidade: critical, warning, info"),
    db: Session = Depends(get_db),
):
    """
    Retorna predições proativas de falha para as próximas N horas.
    Alimenta o predictor com métricas recentes do banco.
    """
    predictor = _get_predictor()

    # Alimentar predictor com métricas recentes (últimas 6h)
    cutoff = time.time() - (6 * 3600)
    sensors = db.query(Sensor).filter(Sensor.is_active == True).all()

    for sensor in sensors:
        server = db.query(Server).filter(Server.id == sensor.server_id).first()
        if not server:
            continue
        host = server.hostname or f"server-{server.id}"
        metric_key = sensor.sensor_type

        recent = db.query(Metric).filter(
            Metric.sensor_id == sensor.id,
        ).order_by(desc(Metric.timestamp)).limit(100).all()

        for m in recent:
            if m.value is not None:
                ts = m.timestamp.timestamp() if m.timestamp else time.time()
                predictor.add_sample(host, metric_key, m.value, ts)

    # Obter predições
    all_preds = predictor.predict_all()

    # Filtrar por horizonte e severidade
    horizon_secs = hours * 3600
    filtered = [
        p for p in all_preds
        if p["hours_until_breach"] <= hours
        and (severity is None or p["severity"] == severity)
    ]

    return {
        "predictions": filtered,
        "total": len(filtered),
        "horizon_hours": hours,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
