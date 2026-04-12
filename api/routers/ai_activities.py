"""
AI Activities API - Dashboard de atividades da IA
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import ResolutionAttempt, LearningSession, KnowledgeBaseEntry, Incident, User, Sensor, Server
from auth import get_current_active_user, require_role

router = APIRouter()


class ActivityResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    status: str
    success: Optional[bool]
    created_at: datetime
    incident_id: Optional[int]
    server_name: Optional[str]
    sensor_name: Optional[str]

    class Config:
        from_attributes = True


class ActivityStatsResponse(BaseModel):
    today_analyses: int
    today_resolutions: int
    today_learning_sessions: int
    pending_approvals: int
    success_rate_today: float
    total_time_saved_minutes: int


@router.get("/", response_model=List[ActivityResponse])
async def list_ai_activities(
    activity_type: Optional[str] = None,
    days: int = 7,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar atividades da IA — combina pipeline v3 (ai_agent_logs) com dados legados."""
    activities = []
    since = datetime.now() - timedelta(days=days)

    # ── 1. Logs do pipeline v3 (ai_agent_logs) ──────────────────────────
    try:
        rows = db.execute(text("""
            SELECT id, run_id, agent_name, status, error, timestamp,
                   output->>'analysis' as ollama_analysis
            FROM ai_agent_logs
            WHERE timestamp >= :since
            ORDER BY timestamp DESC
            LIMIT :limit
        """), {"since": since, "limit": limit}).fetchall()

        agent_icons = {
            "AnomalyDetectionAgent": "📈",
            "CorrelationAgent": "🔗",
            "RootCauseAgent": "🔍",
            "DecisionAgent": "⚖️",
            "AutoRemediationAgent": "🔧",
            "OllamaAnalysisAgent": "🧠",
        }

        for r in rows:
            icon = agent_icons.get(r.agent_name, "🤖")
            desc_text = r.ollama_analysis[:120] + "..." if r.ollama_analysis and len(r.ollama_analysis) > 120 else (r.ollama_analysis or r.error or "Análise concluída")
            activities.append(ActivityResponse(
                id=r.id,
                type="analysis",
                title=f"{icon} {r.agent_name}",
                description=desc_text,
                status=r.status or "success",
                success=r.status == "success",
                created_at=r.timestamp,
                incident_id=None,
                server_name=None,
                sensor_name=None,
            ))
    except Exception:
        pass

    # ── 2. Alertas inteligentes (intelligent_alerts) ─────────────────────
    try:
        alerts = db.execute(text("""
            SELECT id, title, severity, status, root_cause, confidence, created_at
            FROM intelligent_alerts
            WHERE created_at >= :since
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"since": since, "limit": limit}).fetchall()

        for a in alerts:
            sev_icon = "🔴" if a.severity == "critical" else "🟡"
            activities.append(ActivityResponse(
                id=a.id,
                type="analysis",
                title=f"{sev_icon} Alerta Inteligente: {a.title or 'Padrão detectado'}",
                description=a.root_cause or f"Confiança: {int((a.confidence or 0) * 100)}%",
                status=a.status or "open",
                success=a.status == "resolved",
                created_at=a.created_at,
                incident_id=None,
                server_name=None,
                sensor_name=None,
            ))
    except Exception:
        pass

    # ── 3. Dados legados (ResolutionAttempt) ─────────────────────────────
    try:
        resolutions = db.query(ResolutionAttempt).filter(
            ResolutionAttempt.tenant_id == current_user.tenant_id,
            ResolutionAttempt.created_at >= since
        ).order_by(desc(ResolutionAttempt.created_at)).limit(limit).all()

        for r in resolutions:
            incident = db.query(Incident).filter(Incident.id == r.incident_id).first()
            sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first() if incident else None
            server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor else None
            status_emoji = "✅" if r.success else "❌" if r.success is False else "⏳"
            activities.append(ActivityResponse(
                id=r.id,
                type="resolution",
                title=f"{status_emoji} Auto-Resolução",
                description=f"Problema: {r.problem_signature[:100]}",
                status=r.status,
                success=r.success,
                created_at=r.created_at,
                incident_id=r.incident_id,
                server_name=server.hostname if server else None,
                sensor_name=sensor.name if sensor else None,
            ))
    except Exception:
        pass

    activities.sort(key=lambda x: x.created_at, reverse=True)
    return activities[skip:skip + limit]


@router.get("/stats", response_model=ActivityStatsResponse)
async def get_ai_activity_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas de atividades da IA — usa pipeline v3 + dados legados."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        analyses_today = db.execute(text(
            "SELECT COUNT(*) FROM ai_agent_logs WHERE timestamp >= :today"
        ), {"today": today}).scalar() or 0
    except Exception:
        analyses_today = 0

    try:
        alerts_today = db.execute(text(
            "SELECT COUNT(*) FROM intelligent_alerts WHERE created_at >= :today"
        ), {"today": today}).scalar() or 0
    except Exception:
        alerts_today = 0

    try:
        resolutions_today = db.query(func.count(ResolutionAttempt.id)).filter(
            ResolutionAttempt.tenant_id == current_user.tenant_id,
            ResolutionAttempt.created_at >= today
        ).scalar() or 0
        successful_today = db.query(func.count(ResolutionAttempt.id)).filter(
            ResolutionAttempt.tenant_id == current_user.tenant_id,
            ResolutionAttempt.created_at >= today,
            ResolutionAttempt.success == True
        ).scalar() or 0
    except Exception:
        resolutions_today = 0
        successful_today = 0

    try:
        success_count = db.execute(text(
            "SELECT COUNT(*) FROM ai_agent_logs WHERE timestamp >= :today AND status = 'success'"
        ), {"today": today}).scalar() or 0
        success_rate = (success_count / analyses_today * 100) if analyses_today > 0 else 0.0
    except Exception:
        success_rate = 0.0

    time_saved = (alerts_today + successful_today) * 15

    return ActivityStatsResponse(
        today_analyses=analyses_today,
        today_resolutions=resolutions_today + alerts_today,
        today_learning_sessions=0,
        pending_approvals=0,
        success_rate_today=round(success_rate, 1),
        total_time_saved_minutes=time_saved,
    )


@router.get("/pending")
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar resoluções aguardando aprovação"""
    try:
        pending = db.query(ResolutionAttempt).filter(
            ResolutionAttempt.tenant_id == current_user.tenant_id,
            ResolutionAttempt.status == "pending",
            ResolutionAttempt.requires_approval == True
        ).order_by(ResolutionAttempt.created_at).all()
    except Exception:
        return []

    result = []
    for p in pending:
        incident = db.query(Incident).filter(Incident.id == p.incident_id).first()
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first() if incident else None
        server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor else None
        kb_entry = None
        if p.knowledge_base_id:
            kb_entry = db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == p.knowledge_base_id).first()
        result.append({
            "id": p.id,
            "incident_id": p.incident_id,
            "problem": p.problem_signature,
            "solution": p.solution_applied,
            "commands": p.commands_executed,
            "server": server.hostname if server else None,
            "sensor": sensor.name if sensor else None,
            "confidence": kb_entry.root_cause_confidence if kb_entry else 0.0,
            "success_rate": kb_entry.success_rate if kb_entry else 0.0,
            "risk_level": kb_entry.risk_level if kb_entry else "unknown",
            "created_at": p.created_at,
        })
    return result


@router.post("/{attempt_id}/approve")
async def approve_resolution(
    attempt_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    attempt = db.query(ResolutionAttempt).filter(
        ResolutionAttempt.id == attempt_id,
        ResolutionAttempt.tenant_id == current_user.tenant_id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Resolution attempt not found")
    if attempt.status != "pending":
        raise HTTPException(status_code=400, detail="Resolution is not pending approval")
    attempt.approved_by = current_user.id
    attempt.approved_at = datetime.now()
    attempt.approval_notes = notes
    attempt.status = "approved"
    db.commit()
    return {"message": "Resolution approved", "attempt_id": attempt_id}


@router.post("/{attempt_id}/reject")
async def reject_resolution(
    attempt_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    attempt = db.query(ResolutionAttempt).filter(
        ResolutionAttempt.id == attempt_id,
        ResolutionAttempt.tenant_id == current_user.tenant_id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Resolution attempt not found")
    if attempt.status != "pending":
        raise HTTPException(status_code=400, detail="Resolution is not pending approval")
    attempt.status = "rejected"
    attempt.approval_notes = reason
    attempt.approved_by = current_user.id
    attempt.approved_at = datetime.now()
    db.commit()
    return {"message": "Resolution rejected", "attempt_id": attempt_id}


@router.get("/{attempt_id}")
async def get_activity_detail(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    attempt = db.query(ResolutionAttempt).filter(
        ResolutionAttempt.id == attempt_id,
        ResolutionAttempt.tenant_id == current_user.tenant_id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Activity not found")
    incident = db.query(Incident).filter(Incident.id == attempt.incident_id).first()
    sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first() if incident else None
    server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor else None
    kb_entry = None
    if attempt.knowledge_base_id:
        kb_entry = db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == attempt.knowledge_base_id).first()
    return {
        "attempt": attempt,
        "incident": incident,
        "sensor": sensor,
        "server": server,
        "knowledge_base_entry": kb_entry,
    }
