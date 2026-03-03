"""
Knowledge Base API - Gerenciamento da base de conhecimento da IA
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from database import get_db
from models import KnowledgeBaseEntry, ResolutionAttempt, LearningSession, Incident, User
from auth import get_current_active_user, require_role

router = APIRouter()


class KBEntryResponse(BaseModel):
    id: int
    problem_title: str
    problem_signature: str
    sensor_type: str
    severity: str
    root_cause: str
    solution_description: str
    times_matched: int
    times_successful: int
    success_rate: float
    auto_resolution_enabled: bool
    risk_level: str
    last_matched_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class KBStatsResponse(BaseModel):
    total_entries: int
    auto_resolution_enabled: int
    average_success_rate: float
    total_resolutions_this_month: int
    by_sensor_type: Dict[str, int]
    by_risk_level: Dict[str, int]


@router.get("/", response_model=List[KBEntryResponse])
async def list_knowledge_base(
    sensor_type: Optional[str] = None,
    auto_resolution_only: bool = False,
    min_success_rate: float = 0.0,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar entradas da base de conhecimento"""
    query = db.query(KnowledgeBaseEntry).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    )
    
    if sensor_type:
        query = query.filter(KnowledgeBaseEntry.sensor_type == sensor_type)
    
    if auto_resolution_only:
        query = query.filter(KnowledgeBaseEntry.auto_resolution_enabled == True)
    
    if min_success_rate > 0:
        query = query.filter(KnowledgeBaseEntry.success_rate >= min_success_rate)
    
    entries = query.order_by(desc(KnowledgeBaseEntry.success_rate)).offset(skip).limit(limit).all()
    return entries


@router.get("/stats", response_model=KBStatsResponse)
async def get_knowledge_base_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas da base de conhecimento"""
    
    # Total de entradas
    total = db.query(func.count(KnowledgeBaseEntry.id)).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).scalar()
    
    # Com auto-resolução ativa
    auto_enabled = db.query(func.count(KnowledgeBaseEntry.id)).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id,
        KnowledgeBaseEntry.auto_resolution_enabled == True
    ).scalar()
    
    # Taxa de sucesso média
    avg_success = db.query(func.avg(KnowledgeBaseEntry.success_rate)).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).scalar() or 0.0
    
    # Resoluções este mês
    from datetime import datetime, timedelta
    first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    resolutions_this_month = db.query(func.count(ResolutionAttempt.id)).filter(
        ResolutionAttempt.tenant_id == current_user.tenant_id,
        ResolutionAttempt.created_at >= first_day,
        ResolutionAttempt.success == True
    ).scalar()
    
    # Por tipo de sensor
    by_sensor = {}
    sensor_counts = db.query(
        KnowledgeBaseEntry.sensor_type,
        func.count(KnowledgeBaseEntry.id)
    ).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).group_by(KnowledgeBaseEntry.sensor_type).all()
    
    for sensor_type, count in sensor_counts:
        by_sensor[sensor_type] = count
    
    # Por nível de risco
    by_risk = {}
    risk_counts = db.query(
        KnowledgeBaseEntry.risk_level,
        func.count(KnowledgeBaseEntry.id)
    ).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).group_by(KnowledgeBaseEntry.risk_level).all()
    
    for risk_level, count in risk_counts:
        by_risk[risk_level] = count
    
    return KBStatsResponse(
        total_entries=total or 0,
        auto_resolution_enabled=auto_enabled or 0,
        average_success_rate=float(avg_success),
        total_resolutions_this_month=resolutions_this_month or 0,
        by_sensor_type=by_sensor,
        by_risk_level=by_risk
    )


@router.get("/{entry_id}")
async def get_knowledge_base_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Detalhes de uma entrada da base de conhecimento"""
    entry = db.query(KnowledgeBaseEntry).filter(
        KnowledgeBaseEntry.id == entry_id,
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Buscar histórico de resoluções
    resolutions = db.query(ResolutionAttempt).filter(
        ResolutionAttempt.knowledge_base_id == entry_id,
        ResolutionAttempt.tenant_id == current_user.tenant_id
    ).order_by(desc(ResolutionAttempt.created_at)).limit(10).all()
    
    return {
        "entry": entry,
        "recent_resolutions": [
            {
                "id": r.id,
                "incident_id": r.incident_id,
                "success": r.success,
                "created_at": r.created_at,
                "execution_time_seconds": r.execution_time_seconds,
                "error_message": r.error_message
            }
            for r in resolutions
        ]
    }


@router.post("/search")
async def search_knowledge_base(
    problem_description: str,
    sensor_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Buscar solução na base de conhecimento"""
    query = db.query(KnowledgeBaseEntry).filter(
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    )
    
    if sensor_type:
        query = query.filter(KnowledgeBaseEntry.sensor_type == sensor_type)
    
    # Busca simples por texto (pode ser melhorada com embeddings)
    query = query.filter(
        (KnowledgeBaseEntry.problem_description.ilike(f"%{problem_description}%")) |
        (KnowledgeBaseEntry.problem_title.ilike(f"%{problem_description}%"))
    )
    
    results = query.order_by(desc(KnowledgeBaseEntry.success_rate)).limit(5).all()
    
    return {
        "found": len(results) > 0,
        "results": results
    }


@router.put("/{entry_id}")
async def update_knowledge_base_entry(
    entry_id: int,
    auto_resolution_enabled: Optional[bool] = None,
    requires_approval: Optional[bool] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Atualizar entrada da base de conhecimento (admin only)"""
    entry = db.query(KnowledgeBaseEntry).filter(
        KnowledgeBaseEntry.id == entry_id,
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if auto_resolution_enabled is not None:
        entry.auto_resolution_enabled = auto_resolution_enabled
    
    if requires_approval is not None:
        entry.requires_approval = requires_approval
    
    if risk_level is not None:
        entry.risk_level = risk_level
    
    entry.updated_at = datetime.now()
    db.commit()
    db.refresh(entry)
    
    return {"message": "Entry updated successfully", "entry": entry}


@router.delete("/{entry_id}")
async def delete_knowledge_base_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Remover entrada da base de conhecimento (admin only)"""
    entry = db.query(KnowledgeBaseEntry).filter(
        KnowledgeBaseEntry.id == entry_id,
        KnowledgeBaseEntry.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Entry deleted successfully"}
