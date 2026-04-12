"""
Predictions Router — Coruja Monitor v3.5 Enterprise
GET /api/v1/predictions — predições proativas de falha (horizonte 24h)

Persistência: amostras salvas em prediction_samples (TimescaleDB).
Backfill: ao iniciar, carrega histórico do banco para o predictor.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, text
from database import get_db
from models import Metric, Sensor, Server, PredictionSample
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/predictions", tags=["Failure Predictions"])

# ── Predictor singleton ───────────────────────────────────────────────────────
_predictor = None
_backfill_done = False

def _get_predictor():
    global _predictor
    if _predictor is None:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ai-agent"))
        from failure_predictor import FailurePredictor
        _predictor = FailurePredictor()
    return _predictor


def backfill_predictor(db: Session):
    """
    Carrega histórico de prediction_samples no predictor.
    Chamado no lifespan do FastAPI para garantir predições logo após restart.
    """
    global _backfill_done
    if _backfill_done:
        return
    try:
        predictor = _get_predictor()
        rows = db.execute(text("""
            SELECT ps.sensor_id, ps.timestamp, ps.value,
                   s.sensor_type,
                   COALESCE(srv.hostname, s.name) as hostname
            FROM prediction_samples ps
            JOIN sensors s ON s.id = ps.sensor_id
            LEFT JOIN servers srv ON srv.id = s.server_id
            ORDER BY ps.sensor_id, ps.timestamp
        """)).fetchall()

        count = 0
        for row in rows:
            host = row.hostname or f"server-{row.sensor_id}"
            predictor.add_sample(host, row.sensor_type, row.value,
                                 row.timestamp.timestamp())
            count += 1

        logger.info("Backfill predictor: %d amostras carregadas do banco", count)
        _backfill_done = True
    except Exception as e:
        logger.warning("Backfill predictor falhou (não crítico): %s", e)


def _persist_samples(db: Session, sensor_id: int, samples: list):
    """Persiste amostras novas em prediction_samples (evita duplicatas por timestamp)."""
    try:
        for ts, value in samples:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            exists = db.execute(text(
                "SELECT 1 FROM prediction_samples WHERE sensor_id=:sid AND timestamp=:ts LIMIT 1"
            ), {"sid": sensor_id, "ts": dt}).fetchone()
            if not exists:
                db.execute(text(
                    "INSERT INTO prediction_samples (sensor_id, timestamp, value) VALUES (:sid, :ts, :val)"
                ), {"sid": sensor_id, "ts": dt, "val": value})
        db.commit()
    except Exception as e:
        db.rollback()
        logger.debug("Erro ao persistir amostras sensor %d: %s", sensor_id, e)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("")
def get_predictions(
    hours: int = Query(24, le=24, description="Horizonte de predição em horas"),
    severity: str = Query(None, description="Filtrar por severidade: critical, warning, info"),
    db: Session = Depends(get_db),
):
    """
    Retorna predições proativas de falha para as próximas N horas.
    Alimenta o predictor com métricas recentes e persiste amostras no banco.
    """
    try:
        predictor = _get_predictor()
    except Exception as e:
        logger.warning("FailurePredictor não disponível: %s", e)
        return {
            "predictions": [],
            "total": 0,
            "horizon_hours": hours,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "predictor_unavailable",
            "message": str(e),
        }

    try:
        # Buscar últimas 100 métricas por sensor em uma única query batch
        # Inclui sensores standalone (sem servidor) via LEFT JOIN
        rows = db.execute(text("""
            SELECT m.sensor_id, m.value, m.timestamp,
                   s.sensor_type,
                   COALESCE(srv.hostname, s.name) as hostname,
                   COALESCE(srv.id, 0) as server_id
            FROM (
                SELECT sensor_id, value, timestamp,
                       ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY timestamp DESC) as rn
                FROM metrics
                WHERE timestamp >= NOW() - INTERVAL '6 hours'
            ) m
            JOIN sensors s ON s.id = m.sensor_id AND s.is_active = true
            LEFT JOIN servers srv ON srv.id = s.server_id
            WHERE m.rn <= 100
            ORDER BY m.sensor_id, m.timestamp
        """)).fetchall()

        # Agrupar amostras por sensor para persistência em batch
        samples_by_sensor = {}
        for row in rows:
            if row.value is None:
                continue
            host = row.hostname or f"server-{row.server_id}"
            ts = row.timestamp.timestamp() if row.timestamp else time.time()
            predictor.add_sample(host, row.sensor_type, row.value, ts)
            sid = row.sensor_id
            if sid not in samples_by_sensor:
                samples_by_sensor[sid] = []
            samples_by_sensor[sid].append((ts, row.value))

        # Persistir amostras novas em batch
        for sensor_id, samples in samples_by_sensor.items():
            _persist_samples(db, sensor_id, samples)

        # Obter predições
        all_preds = predictor.predict_all()

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

    except Exception as e:
        logger.error("Erro ao gerar predições: %s", e, exc_info=True)
        return {
            "predictions": [],
            "total": 0,
            "horizon_hours": hours,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "error",
            "message": str(e),
        }


@router.post("/ingest")
def ingest_samples(
    samples: list,
    db: Session = Depends(get_db),
):
    """
    Recebe amostras do MetricsProcessor (pipeline da sonda).
    Alimenta o predictor e persiste no banco.
    Endpoint interno — sem autenticação obrigatória (chamado pelo worker).
    """
    predictor = _get_predictor()
    ingested = 0
    for s in samples:
        try:
            sensor_id = s.get("sensor_id")
            sensor_type = s.get("sensor_type", "unknown")
            value = s.get("value")
            ts = s.get("timestamp", time.time())
            if value is None or sensor_id is None:
                continue

            # Buscar hostname do servidor
            sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
            if not sensor:
                continue
            server = db.query(Server).filter(Server.id == sensor.server_id).first()
            host = server.hostname if server else f"server-{sensor_id}"

            predictor.add_sample(host, sensor_type, float(value), float(ts))
            _persist_samples(db, sensor_id, [(float(ts), float(value))])
            ingested += 1
        except Exception as e:
            logger.debug("Erro ao ingerir amostra: %s", e)

    return {"ingested": ingested}
