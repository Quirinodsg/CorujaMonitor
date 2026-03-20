"""
Audit Log Router — Coruja Monitor v3.5 Enterprise
GET /api/v1/audit — lista entradas de auditoria
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import AuditLog

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Log"])


@router.get("")
def list_audit_logs(
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    action: str = Query(None),
    resource_type: str = Query(None),
    user_id: int = Query(None),
    db: Session = Depends(get_db),
):
    """Lista entradas de auditoria com filtros opcionais."""
    q = db.query(AuditLog).order_by(desc(AuditLog.created_at))

    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        q = q.filter(AuditLog.resource_type == resource_type)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)

    total = q.count()
    entries = q.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": e.id,
                "action": e.action,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "user_id": e.user_id,
                "tenant_id": e.tenant_id,
                "details": e.details,
                "ip_address": e.ip_address,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
    }
