"""
AI Activities API - Dashboard de atividades da IA
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import ResolutionAttempt, LearningSession, KnowledgeBaseEntry, Incident, User, Sensor, Server
from auth import get_current_active_user, require_role

router = APIRouter()


class ActivityResponse(BaseModel):
    id: int
    type: str  # resolution, learning, analysis
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
    """Listar atividades da IA"""
    
    activities = []
    since = datetime.now() - timedelta(days=days)
    
    # Resolution Attempts
    if not activity_type or activity_type == "resolution":
        resolutions = db.query(ResolutionAttempt).join(
            Incident
        ).join(
            Sensor
        ).join(
            Server
        ).filter(
            ResolutionAttempt.tenant_id == current_user.tenant_id,
            ResolutionAttempt.created_at >= since
        ).order_by(desc(ResolutionAttempt.created_at)).limit(limit).all()
        
        for r in resolutions:
            incident = db.query(Incident).filter(Incident.id == r.incident_id).first()
            sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first() if incident else None
            server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor else None
            
            status_emoji = "✅" if r.success else "❌" if r.success == False else "⏳"
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
                sensor_name=sensor.name if sensor else None
            ))
    
    # Learning Sessions
    if not activity_type or activity_type == "learning":
        sessions = db.query(LearningSession).join(
            Incident
        ).join(
            Sensor
        ).join(
            Server
        ).filter(
            LearningSession.tenant_id == current_user.tenant_id,
            LearningSession.created_at >= since
        ).order_by(desc(LearningSession.created_at)).limit(limit).all()
        
        for s in sessions:
            incident = db.query(Incident).filter(Incident.id == s.incident_id).first()
            sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first() if incident else None
            server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor else None
            
            emoji = "🎓" if s.added_to_knowledge_base else "📝"
            activities.append(ActivityResponse(
                id=s.id,
                type="learning",
                title=f"{emoji} Aprendizado",
                description=f"Aprendeu: {s.problem_description[:100]}",
                status="learned" if s.added_to_knowledge_base else "captured",
                success=s.was_successful,
                created_at=s.created_at,
                incident_id=s.incident_id,
                server_name=server.hostname if server else None,
                sensor_name=sensor.name if sensor else None
            ))
    
    # Sort by date
    activities.sort(key=lambda x: x.created_at, reverse=True)
    
    return activities[skip:skip+limit]


@router.get("/stats", response_model=ActivityStatsResponse)
async def get_ai_activity_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas de atividades da IA"""
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Resoluções hoje
    resolutions_today = db.query(func.count(ResolutionAttempt.id)).filter(
        ResolutionAttempt.tenant_id == current_user.tenant_id,
        ResolutionAttempt.created_at >= today
    ).scalar() or 0
    
    # Sessões de aprendizado hoje
    learning_today = db.query(func.count(LearningSession.id)).filter(
        LearningSession.tenant_id == current_user.tenant_id,
        LearningSession.created_at >= today
    ).scalar() or 0
    
    # Aguardando aprovação
    pending = db.query(func.count(ResolutionAttempt.id)).filter(
        ResolutionAttempt.tenant_id == current_user.tenant_id,
        ResolutionAttempt.status == "pending",
        ResolutionAttempt.requires_approval == True
    ).scalar() or 0
    
    # Taxa de sucesso hoje
    successful_today = db.query(func.count(ResolutionAttempt.id)).filter(
        ResolutionAttempt.tenant_id == current_user.tenant_id,
        ResolutionAttempt.created_at >= today,
        ResolutionAttempt.success == True
    ).scalar() or 0
    
    success_rate = (successful_today / resolutions_today * 100) if resolutions_today > 0 else 0.0
    
    # Tempo economizado (estimativa: 15 minutos por resolução automática)
    time_saved = successful_today * 15
    
    return ActivityStatsResponse(
        today_analyses=resolutions_today + learning_today,
        today_resolutions=resolutions_today,
        today_learning_sessions=learning_today,
        pending_approvals=pending,
        success_rate_today=success_rate,
        total_time_saved_minutes=time_saved
    )


@router.get("/pending")
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar resoluções aguardando aprovação"""
    
    pending = db.query(ResolutionAttempt).filter(
        ResolutionAttempt.tenant_id == current_user.tenant_id,
        ResolutionAttempt.status == "pending",
        ResolutionAttempt.requires_approval == True
    ).order_by(ResolutionAttempt.created_at).all()
    
    result = []
    for p in pending:
        incident = db.query(Incident).filter(Incident.id == p.incident_id).first()
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first() if incident else None
        server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor else None
        
        # Get KB entry for confidence
        kb_entry = None
        if p.knowledge_base_id:
            kb_entry = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.id == p.knowledge_base_id
            ).first()
        
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
            "created_at": p.created_at
        })
    
    return result


@router.post("/{attempt_id}/approve")
async def approve_resolution(
    attempt_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Aprovar resolução automática"""
    
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
    """Rejeitar resolução automática"""
    
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
    """Detalhes de uma atividade"""
    
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
        kb_entry = db.query(KnowledgeBaseEntry).filter(
            KnowledgeBaseEntry.id == attempt.knowledge_base_id
        ).first()
    
    return {
        "attempt": attempt,
        "incident": incident,
        "sensor": sensor,
        "server": server,
        "knowledge_base_entry": kb_entry
    }
