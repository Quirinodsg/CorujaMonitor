"""
FASE 10 — Meta Observability: /internal/health/deep
Auto-monitoramento do Coruja Monitor v3.0.
"""
import time
import os
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from database import get_db
from auth import get_current_active_user
from models import User

router = APIRouter()
logger = logging.getLogger(__name__)


def _check_postgres(db: Session) -> Dict[str, Any]:
    start = time.monotonic()
    try:
        db.execute(text("SELECT 1"))
        latency_ms = (time.monotonic() - start) * 1000
        return {"status": "ok", "latency_ms": round(latency_ms, 2)}
    except Exception as e:
        return {"status": "critical", "error": str(e), "latency_ms": -1}


def _check_redis() -> Dict[str, Any]:
    start = time.monotonic()
    try:
        import redis
        r = redis.from_url(
            f"redis://{os.getenv('REDIS_HOST', 'redis')}:{os.getenv('REDIS_PORT', 6379)}",
            socket_timeout=2
        )
        r.ping()
        latency_ms = (time.monotonic() - start) * 1000

        # Stream backlog
        try:
            stream_len = r.xlen("metrics:raw")
            events_len = r.xlen("events_stream")
        except Exception:
            stream_len = -1
            events_len = -1

        return {
            "status": "ok",
            "latency_ms": round(latency_ms, 2),
            "metrics_stream_backlog": stream_len,
            "events_stream_backlog": events_len,
        }
    except Exception as e:
        return {"status": "critical", "error": str(e), "latency_ms": -1}


def _check_ollama() -> Dict[str, Any]:
    start = time.monotonic()
    try:
        import httpx
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{ollama_url}/api/tags")
        latency_ms = (time.monotonic() - start) * 1000
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            return {
                "status": "ok",
                "latency_ms": round(latency_ms, 2),
                "models_loaded": len(models),
                "models": [m.get("name") for m in models],
            }
        return {"status": "warning", "latency_ms": round(latency_ms, 2), "http_status": resp.status_code}
    except Exception as e:
        return {"status": "offline", "error": str(e), "latency_ms": -1}


def _check_pipeline_stats(db: Session) -> Dict[str, Any]:
    try:
        from models import Metric, Incident
        from sqlalchemy import func
        from datetime import datetime, timedelta

        since = datetime.utcnow() - timedelta(hours=1)
        metrics_1h = db.query(func.count(Metric.id)).filter(Metric.timestamp >= since).scalar() or 0
        incidents_open = db.query(func.count(Incident.id)).filter(Incident.status == "open").scalar() or 0

        return {
            "status": "ok",
            "metrics_last_1h": metrics_1h,
            "open_incidents": incidents_open,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/internal/health/deep")
async def deep_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Deep health check — auto-monitoramento completo.
    Verifica: PostgreSQL, Redis, Ollama, pipeline stats.
    """
    start = time.monotonic()

    checks = {
        "postgres": _check_postgres(db),
        "redis": _check_redis(),
        "ollama": _check_ollama(),
        "pipeline": _check_pipeline_stats(db),
    }

    total_ms = (time.monotonic() - start) * 1000

    # Overall status
    statuses = [c.get("status", "unknown") for c in checks.values()]
    if "critical" in statuses:
        overall = "critical"
    elif "warning" in statuses or "offline" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "status": overall,
        "version": "3.0.0",
        "total_check_ms": round(total_ms, 2),
        "checks": checks,
    }


@router.get("/internal/health/deep/public")
async def deep_health_public():
    """Health check público (sem autenticação) — apenas status geral."""
    redis_ok = _check_redis().get("status") == "ok"
    return {
        "status": "ok" if redis_ok else "degraded",
        "version": "3.0.0",
    }


@router.get("/api/v1/system/health")
async def system_health_public(db: Session = Depends(get_db)):
    """
    Endpoint público de health check enterprise — sem autenticação.
    Valida: PostgreSQL, Redis, TimescaleDB, AI Agents, Predictor.
    """
    start = time.monotonic()

    # PostgreSQL
    pg = _check_postgres(db)

    # Redis
    redis = _check_redis()

    # TimescaleDB (hypertable check)
    ts_status = "unknown"
    try:
        result = db.execute(text(
            "SELECT count(*) FROM timescaledb_information.hypertables"
        )).scalar()
        ts_status = "ok" if result is not None else "warning"
    except Exception:
        ts_status = "unavailable"

    # AI Agents (predictor importável)
    ai_status = "unknown"
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ai-agent"))
        from failure_predictor import FailurePredictor  # noqa
        ai_status = "ok"
    except Exception as e:
        ai_status = f"error: {type(e).__name__}"

    # Pipeline stats
    pipeline = _check_pipeline_stats(db)

    components = {
        "postgres": pg,
        "redis": redis,
        "timescaledb": {"status": ts_status},
        "ai_agents": {"status": ai_status},
        "pipeline": pipeline,
    }

    statuses = [c.get("status", "unknown") for c in components.values()]
    if "critical" in statuses:
        overall = "critical"
    elif any(s not in ("ok", "unavailable") for s in statuses):
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "status": overall,
        "version": "3.5.0",
        "total_check_ms": round((time.monotonic() - start) * 1000, 2),
        "components": components,
    }
