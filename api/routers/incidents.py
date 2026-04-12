from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import Incident, Sensor, Server, User, RemediationLog, Metric
from auth import get_current_active_user

router = APIRouter()

class IncidentResponse(BaseModel):
    id: int
    sensor_id: int
    severity: str
    status: str
    title: str
    description: Optional[str]
    root_cause: Optional[str]
    ai_analysis: Optional[Dict[str, Any]]
    remediation_attempted: bool
    remediation_successful: Optional[bool]
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class RemediationLogResponse(BaseModel):
    id: int
    incident_id: int
    action_type: str
    action_description: Optional[str]
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    executed_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from models import Probe

    if current_user.role == 'admin':
        # Admin vê todos — incluindo sensores standalone (server_id NULL)
        query = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .outerjoin(Server, Sensor.server_id == Server.id)
        )
    else:
        from sqlalchemy import or_, exists, and_
        # Filtra incidentes cujo sensor pertence ao tenant via:
        # 1. server.tenant_id direto
        # 2. probe.tenant_id (sensores standalone com probe)
        # 3. sensor sem server nem probe (standalone puro)
        query = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .filter(
                or_(
                    # Sensor vinculado a servidor do tenant
                    exists().where(
                        and_(
                            Server.id == Sensor.server_id,
                            Server.tenant_id == current_user.tenant_id,
                        )
                    ),
                    # Sensor standalone vinculado a probe do tenant
                    exists().where(
                        and_(
                            Probe.id == Sensor.probe_id,
                            Probe.tenant_id == current_user.tenant_id,
                        )
                    ),
                    # Sensor completamente standalone (sem server nem probe)
                    and_(
                        Sensor.server_id == None,
                        Sensor.probe_id == None,
                    ),
                )
            )
        )

    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)

    incidents = query.order_by(Incident.created_at.desc()).limit(limit).all()
    return incidents

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    incident = db.query(Incident).join(Sensor).join(Server).filter(
        Incident.id == incident_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident

@router.get("/{incident_id}/remediation", response_model=List[RemediationLogResponse])
async def get_incident_remediation_logs(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    incident = db.query(Incident).join(Sensor).join(Server).filter(
        Incident.id == incident_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    logs = db.query(RemediationLog).filter(
        RemediationLog.incident_id == incident_id
    ).order_by(RemediationLog.executed_at.desc()).all()
    
    return logs


class ResolveIncidentRequest(BaseModel):
    resolution_notes: Optional[str] = None


@router.post("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: int,
    request: ResolveIncidentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Resolve an incident manually
    """
    # Admin pode resolver qualquer incidente, usuário normal apenas do seu tenant
    if current_user.role == 'admin':
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()
    else:
        incident = db.query(Incident).join(Sensor).join(Server).filter(
            Incident.id == incident_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident.resolved_at:
        raise HTTPException(status_code=400, detail="Incident already resolved")
    
    # Resolver incidente
    incident.resolved_at = datetime.utcnow()
    incident.status = "resolved"
    if request.resolution_notes:
        incident.resolution_notes = request.resolution_notes
    
    # Deletar métricas simuladas do sensor para permitir que probe envie valores reais
    sensor_id = incident.sensor_id
    all_metrics = db.query(Metric).filter(Metric.sensor_id == sensor_id).all()
    
    metrics_deleted = 0
    for metric in all_metrics:
        # Verificar se é métrica simulada através do campo metadata (extra_metadata no modelo)
        if metric.extra_metadata and isinstance(metric.extra_metadata, dict) and metric.extra_metadata.get('simulated'):
            db.delete(metric)
            metrics_deleted += 1
    
    db.commit()
    db.refresh(incident)
    
    return {
        "success": True,
        "message": "Incident resolved successfully",
        "incident_id": incident.id,
        "resolved_at": incident.resolved_at.isoformat(),
        "simulated_metrics_deleted": metrics_deleted
    }


class AcknowledgeIncidentRequest(BaseModel):
    notes: Optional[str] = None


@router.post("/{incident_id}/acknowledge")
async def acknowledge_incident(
    incident_id: int,
    request: AcknowledgeIncidentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Acknowledge an incident (mark as being worked on, but not resolved)
    """
    # Admin pode reconhecer qualquer incidente, usuário normal apenas do seu tenant
    if current_user.role == 'admin':
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()
    else:
        incident = db.query(Incident).join(Sensor).join(Server).filter(
            Incident.id == incident_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident.resolved_at:
        raise HTTPException(status_code=400, detail="Incident already resolved")
    
    # Reconhecer incidente (muda status mas NÃO resolve)
    incident.status = "acknowledged"
    incident.acknowledged_at = datetime.utcnow()
    incident.acknowledged_by = current_user.id
    if request.notes:
        incident.acknowledgement_notes = request.notes
    
    db.commit()
    db.refresh(incident)
    
    # Parar escalação ativa para o sensor associado (se houver)
    try:
        import sys, os
        worker_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "worker")
        if worker_dir not in sys.path:
            sys.path.insert(0, worker_dir)
        from escalation import stop_escalation
        stop_escalation(incident.sensor_id, reason="acknowledged")
    except Exception:
        pass  # fail-open: não impedir reconhecimento se escalação falhar
    
    return {
        "success": True,
        "message": "Incident acknowledged successfully",
        "incident_id": incident.id,
        "status": incident.status,
        "acknowledged_at": incident.acknowledged_at.isoformat() if incident.acknowledged_at else None
    }
