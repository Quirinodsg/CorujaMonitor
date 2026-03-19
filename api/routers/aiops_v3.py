"""
AIOps v3 Router — endpoints públicos (sem auth) para o dashboard AIOpsV3.js
Expõe atividades do pipeline v3 e métricas de feedback.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/v1/aiops-v3", tags=["AIOps v3"])


@router.get("/activities")
async def get_v3_activities(limit: int = 20, db: Session = Depends(get_db)):
    """
    Retorna atividades recentes do pipeline de agentes v3.
    Lê de ai_feedback_actions + intelligent_alerts.
    """
    activities = []

    # Ações de remediação do feedback loop
    try:
        rows = db.execute(text("""
            SELECT action_id, agent_name, action_type, target_host,
                   timestamp, result, outcome
            FROM ai_feedback_actions
            ORDER BY timestamp DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()

        for r in rows:
            activities.append({
                "id": str(r.action_id),
                "agent_name": r.agent_name or "AutoRemediationAgent",
                "action_type": r.action_type,
                "description": f"{r.action_type} em {r.target_host}",
                "target_host": r.target_host,
                "outcome": r.outcome or "pending",
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "type": "remediation",
            })
    except Exception:
        pass

    # Alertas inteligentes como atividades de decisão
    try:
        rows = db.execute(text("""
            SELECT id, title, severity, status, root_cause, confidence, created_at
            FROM intelligent_alerts
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()

        for r in rows:
            activities.append({
                "id": str(r.id),
                "agent_name": "DecisionAgent",
                "action_type": "alert_created",
                "description": r.title,
                "target_host": r.root_cause or "",
                "outcome": "positive" if r.status == "resolved" else "pending",
                "timestamp": r.created_at.isoformat() if r.created_at else None,
                "type": "alert",
                "severity": r.severity,
                "confidence": r.confidence,
            })
    except Exception:
        pass

    # Ordenar por timestamp desc e limitar
    activities.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
    return {"activities": activities[:limit]}


@router.get("/feedback-metrics")
async def get_feedback_metrics(db: Session = Depends(get_db)):
    """Métricas do feedback loop v3."""
    try:
        row = db.execute(text("""
            SELECT
                COUNT(*) as actions_total,
                COUNT(*) FILTER (WHERE result = 'success') as actions_successful,
                AVG(resolution_time_seconds) as mean_resolution_time_seconds,
                COUNT(*) FILTER (WHERE outcome = 'negative')::float /
                    NULLIF(COUNT(*) FILTER (WHERE outcome IS NOT NULL), 0) as false_positive_rate
            FROM ai_feedback_actions
        """)).fetchone()

        return {
            "actions_total": row.actions_total or 0,
            "actions_successful": row.actions_successful or 0,
            "mean_resolution_time_seconds": float(row.mean_resolution_time_seconds or 0),
            "false_positive_rate": float(row.false_positive_rate or 0),
        }
    except Exception as e:
        return {
            "actions_total": 0,
            "actions_successful": 0,
            "mean_resolution_time_seconds": 0.0,
            "false_positive_rate": 0.0,
            "error": str(e),
        }
