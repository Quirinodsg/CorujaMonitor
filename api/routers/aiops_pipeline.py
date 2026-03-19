"""
AIOps Pipeline Router — Coruja Monitor v3.0

Endpoints:
  POST /api/v1/aiops-pipeline/run          — executa pipeline com eventos recentes
  POST /api/v1/aiops-pipeline/simulate     — simula cenário de teste (CPU 95%)
  GET  /api/v1/aiops-pipeline/logs         — histórico de execuções (ai_agent_logs)
  GET  /api/v1/aiops-pipeline/runs         — resumo de runs agrupados por run_id
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/aiops-pipeline", tags=["AIOps Pipeline v3"])


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_orchestrator(db):
    """Instancia o orquestrador com conexão psycopg2 raw (para INSERT direto)."""
    try:
        from ai_agents.pipeline_orchestrator import PipelineOrchestrator
        # Usar a conexão SQLAlchemy diretamente
        return PipelineOrchestrator(db_conn=db)
    except Exception as e:
        logger.error("Erro ao instanciar PipelineOrchestrator: %s", e)
        return None


def _build_events_from_db(db, minutes: int = 30):
    """Busca eventos recentes do banco e converte para objetos Event v3."""
    from core.spec.models import Event
    from core.spec.enums import EventSeverity
    from uuid import UUID

    events = []
    try:
        rows = db.execute(text("""
            SELECT
                i.id,
                s.server_id as host_id,
                i.severity,
                i.title,
                i.created_at,
                s.sensor_type
            FROM incidents i
            JOIN sensors s ON s.id = i.sensor_id
            WHERE i.created_at >= NOW() - CAST(:interval AS INTERVAL)
              AND i.status = 'open'
            ORDER BY i.created_at DESC
            LIMIT 50
        """), {"interval": f"{minutes} minutes"}).fetchall()

        for r in rows:
            sev = EventSeverity.CRITICAL if r.severity == "critical" else EventSeverity.WARNING
            try:
                host_uuid = UUID(int=r.host_id)
            except Exception:
                host_uuid = uuid4()

            event = Event(
                host_id=host_uuid,
                type=f"high_{r.sensor_type}" if r.sensor_type else "incident",
                severity=sev,
                timestamp=r.created_at.replace(tzinfo=timezone.utc) if r.created_at.tzinfo is None else r.created_at,
                description=r.title or "",
            )
            events.append(event)
    except Exception as e:
        logger.error("_build_events_from_db: %s", e)

    return events


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/run")
async def run_pipeline(minutes: int = 30, db: Session = Depends(get_db)):
    """
    Executa o pipeline v3 com incidentes abertos dos últimos N minutos.
    """
    events = _build_events_from_db(db, minutes)

    if not events:
        return {
            "status": "skipped",
            "reason": f"Nenhum incidente aberto nos últimos {minutes} minutos",
            "events_found": 0,
        }

    orch = _get_orchestrator(db)
    if not orch:
        return {"status": "error", "reason": "Orquestrador não disponível"}

    result = orch.run_from_events(events)
    return {"status": "ok", **result}


@router.post("/simulate")
async def simulate_pipeline(
    sensor_type: str = "cpu",
    value: float = 95.0,
    host_label: str = "SRV-SIMULADO",
    db: Session = Depends(get_db),
):
    """
    Simula cenário de teste: gera evento sintético e executa pipeline completo.
    Útil para validar que o pipeline está funcionando sem precisar de dados reais.
    """
    from core.spec.models import Event, Metric
    from core.spec.enums import EventSeverity
    from uuid import uuid4

    host_id = uuid4()
    sensor_id = uuid4()
    now = datetime.now(timezone.utc)

    # Criar evento sintético
    severity = EventSeverity.CRITICAL if value >= 90 else EventSeverity.WARNING
    event = Event(
        host_id=host_id,
        type=f"high_{sensor_type}",
        severity=severity,
        timestamp=now,
        source_metric_id=sensor_id,
        description=f"[SIMULADO] {sensor_type.upper()} = {value}% em {host_label}",
    )

    # Criar métricas sintéticas para baseline do AnomalyDetection
    # 50 amostras normais (40-60%) + 1 anômala (95%)
    metrics = []
    import random
    random.seed(42)
    for i in range(50):
        m = Metric(
            sensor_id=sensor_id,
            host_id=host_id,
            value=random.uniform(40, 60),
            unit="%",
            timestamp=now - timedelta(minutes=50 - i),
            status="ok",
        )
        metrics.append(m)

    # Métrica anômala
    anomaly_metric = Metric(
        sensor_id=sensor_id,
        host_id=host_id,
        value=value,
        unit="%",
        timestamp=now,
        status="critical",
    )
    metrics.append(anomaly_metric)

    orch = _get_orchestrator(db)
    if not orch:
        return {"status": "error", "reason": "Orquestrador não disponível"}

    # Alimentar baseline do agente de anomalia com as métricas normais
    anomaly_agent = orch._pipeline._agents[0]  # AnomalyDetectionAgent
    for m in metrics[:-1]:
        anomaly_agent.get_baseline(str(sensor_id)).add(m.value)

    result = orch.run_from_events([event], metrics=metrics)

    return {
        "status": "ok",
        "simulation": {
            "sensor_type": sensor_type,
            "value": value,
            "host_label": host_label,
            "host_id": str(host_id),
            "sensor_id": str(sensor_id),
        },
        **result,
    }


@router.get("/logs")
async def get_pipeline_logs(
    limit: int = 50,
    agent_name: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retorna histórico de execuções dos agentes (ai_agent_logs)."""
    try:
        where = []
        params: dict = {"limit": limit}
        if agent_name:
            where.append("agent_name = :agent_name")
            params["agent_name"] = agent_name
        if status:
            where.append("status = :status")
            params["status"] = status

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        rows = db.execute(text(f"""
            SELECT id, run_id, agent_name, output, status, error, duration_ms, timestamp
            FROM ai_agent_logs
            {where_sql}
            ORDER BY timestamp DESC
            LIMIT :limit
        """), params).fetchall()

        logs = []
        for r in rows:
            logs.append({
                "id": r.id,
                "run_id": str(r.run_id),
                "agent_name": r.agent_name,
                "output": r.output or {},
                "status": r.status,
                "error": r.error,
                "duration_ms": r.duration_ms,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            })

        return {"logs": logs, "total": len(logs)}
    except Exception as e:
        return {"logs": [], "total": 0, "error": str(e)}


@router.get("/runs")
async def get_pipeline_runs(limit: int = 20, db: Session = Depends(get_db)):
    """Retorna resumo de runs agrupados por run_id."""
    try:
        rows = db.execute(text("""
            SELECT
                run_id,
                MIN(timestamp) as started_at,
                MAX(timestamp) as finished_at,
                COUNT(*) as agents_total,
                COUNT(*) FILTER (WHERE status = 'success') as agents_success,
                COUNT(*) FILTER (WHERE status = 'error') as agents_error,
                array_agg(agent_name ORDER BY timestamp) as agents
            FROM ai_agent_logs
            GROUP BY run_id
            ORDER BY MIN(timestamp) DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()

        runs = []
        for r in rows:
            runs.append({
                "run_id": str(r.run_id),
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                "agents_total": r.agents_total,
                "agents_success": r.agents_success,
                "agents_error": r.agents_error,
                "agents": list(r.agents) if r.agents else [],
            })

        return {"runs": runs, "total": len(runs)}
    except Exception as e:
        return {"runs": [], "total": 0, "error": str(e)}


@router.get("/status")
async def get_pipeline_status(db: Session = Depends(get_db)):
    """Status geral do pipeline: última execução, total de runs, alertas gerados."""
    try:
        last_run = db.execute(text("""
            SELECT run_id, MAX(timestamp) as last_ts, COUNT(*) as agents
            FROM ai_agent_logs
            GROUP BY run_id
            ORDER BY MAX(timestamp) DESC
            LIMIT 1
        """)).fetchone()

        total_runs = db.execute(text(
            "SELECT COUNT(DISTINCT run_id) FROM ai_agent_logs"
        )).scalar() or 0

        total_alerts = db.execute(text(
            "SELECT COUNT(*) FROM intelligent_alerts"
        )).scalar() or 0

        total_actions = db.execute(text(
            "SELECT COUNT(*) FROM ai_feedback_actions"
        )).scalar() or 0

        return {
            "pipeline_active": True,
            "total_runs": total_runs,
            "total_intelligent_alerts": total_alerts,
            "total_remediation_actions": total_actions,
            "last_run": {
                "run_id": str(last_run.run_id) if last_run else None,
                "timestamp": last_run.last_ts.isoformat() if last_run and last_run.last_ts else None,
                "agents": last_run.agents if last_run else 0,
            } if last_run else None,
        }
    except Exception as e:
        return {"pipeline_active": False, "error": str(e)}
