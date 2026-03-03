from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import get_db
from models import Tenant, User
from auth import get_current_active_user, require_role

router = APIRouter()

class TenantCreate(BaseModel):
    name: str
    slug: str

class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    tenants = db.query(Tenant).all()
    return tenants

@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Check if slug already exists
    existing = db.query(Tenant).filter(Tenant.slug == tenant.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    new_tenant = Tenant(name=tenant.name, slug=tenant.slug)
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    return new_tenant

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin" and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return tenant



class TenantUpdate(BaseModel):
    name: str
    slug: str


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_update: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check if new slug conflicts with another tenant
    if tenant_update.slug != tenant.slug:
        existing = db.query(Tenant).filter(
            Tenant.slug == tenant_update.slug,
            Tenant.id != tenant_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")
    
    tenant.name = tenant_update.name
    tenant.slug = tenant_update.slug
    
    db.commit()
    db.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}/toggle-active", response_model=TenantResponse)
async def toggle_tenant_active(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant.is_active = not tenant.is_active
    
    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Prevent deleting own tenant
    if current_user.tenant_id == tenant_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own tenant")
    
    # Delete all related data (cascade should handle this, but being explicit)
    from models import User, Probe, Server, Sensor, Metric, Incident
    
    # Get all servers for this tenant
    servers = db.query(Server).filter(Server.tenant_id == tenant_id).all()
    server_ids = [s.id for s in servers]
    
    # Get all sensors for these servers
    sensors = db.query(Sensor).filter(Sensor.server_id.in_(server_ids)).all()
    sensor_ids = [s.id for s in sensors]
    
    # Delete metrics
    db.query(Metric).filter(Metric.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
    
    # Delete incidents
    db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
    
    # Delete sensors
    db.query(Sensor).filter(Sensor.server_id.in_(server_ids)).delete(synchronize_session=False)
    
    # Delete servers
    db.query(Server).filter(Server.tenant_id == tenant_id).delete(synchronize_session=False)
    
    # Delete probes
    db.query(Probe).filter(Probe.tenant_id == tenant_id).delete(synchronize_session=False)
    
    # Delete users
    db.query(User).filter(User.tenant_id == tenant_id).delete(synchronize_session=False)
    
    # Finally delete tenant
    db.delete(tenant)
    db.commit()
    
    return {"message": "Tenant deleted successfully"}
