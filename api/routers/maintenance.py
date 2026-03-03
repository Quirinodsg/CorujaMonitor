from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import MaintenanceWindow, Server, User
from auth import get_current_active_user

router = APIRouter()


class MaintenanceWindowCreate(BaseModel):
    server_id: Optional[int] = None  # NULL = toda empresa
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime


class MaintenanceWindowUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None


class MaintenanceWindowResponse(BaseModel):
    id: int
    tenant_id: int
    server_id: Optional[int]
    server_name: Optional[str] = None
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    created_by: Optional[int]
    created_by_name: Optional[str] = None
    is_active: bool
    is_current: bool = False  # Se está ativa agora
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=MaintenanceWindowResponse)
async def create_maintenance_window(
    window_data: MaintenanceWindowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new maintenance window"""
    # Validate dates
    if window_data.end_time <= window_data.start_time:
        raise HTTPException(
            status_code=400, 
            detail="Data de término deve ser posterior à data de início"
        )
    
    # If server_id provided, verify it belongs to user's tenant
    if window_data.server_id:
        server = db.query(Server).filter(
            Server.id == window_data.server_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
        
        if not server:
            raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    # Create maintenance window
    new_window = MaintenanceWindow(
        tenant_id=current_user.tenant_id,
        server_id=window_data.server_id,
        title=window_data.title,
        description=window_data.description,
        start_time=window_data.start_time,
        end_time=window_data.end_time,
        created_by=current_user.id
    )
    
    db.add(new_window)
    db.commit()
    db.refresh(new_window)
    
    # Build response
    response = MaintenanceWindowResponse.from_orm(new_window)
    response.created_by_name = current_user.full_name
    
    if window_data.server_id:
        server = db.query(Server).filter(Server.id == window_data.server_id).first()
        if server:
            response.server_name = server.hostname
    
    # Check if currently active
    now = datetime.utcnow()
    response.is_current = (
        new_window.is_active and 
        new_window.start_time <= now <= new_window.end_time
    )
    
    return response


@router.get("/", response_model=List[MaintenanceWindowResponse])
async def list_maintenance_windows(
    server_id: Optional[int] = None,
    active_only: bool = False,
    current_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List maintenance windows"""
    query = db.query(MaintenanceWindow).filter(
        MaintenanceWindow.tenant_id == current_user.tenant_id
    )
    
    if server_id:
        query = query.filter(
            or_(
                MaintenanceWindow.server_id == server_id,
                MaintenanceWindow.server_id.is_(None)  # Company-wide
            )
        )
    
    if active_only:
        query = query.filter(MaintenanceWindow.is_active == True)
    
    if current_only:
        now = datetime.utcnow()
        query = query.filter(
            and_(
                MaintenanceWindow.is_active == True,
                MaintenanceWindow.start_time <= now,
                MaintenanceWindow.end_time >= now
            )
        )
    
    windows = query.order_by(MaintenanceWindow.start_time.desc()).all()
    
    # Build responses with additional info
    responses = []
    now = datetime.utcnow()
    
    for window in windows:
        response = MaintenanceWindowResponse.from_orm(window)
        
        # Add server name
        if window.server_id:
            server = db.query(Server).filter(Server.id == window.server_id).first()
            if server:
                response.server_name = server.hostname
        else:
            response.server_name = "Toda a Empresa"
        
        # Add creator name
        if window.created_by:
            user = db.query(User).filter(User.id == window.created_by).first()
            if user:
                response.created_by_name = user.full_name
        
        # Check if currently active
        response.is_current = (
            window.is_active and 
            window.start_time <= now <= window.end_time
        )
        
        responses.append(response)
    
    return responses


@router.get("/{window_id}", response_model=MaintenanceWindowResponse)
async def get_maintenance_window(
    window_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific maintenance window"""
    window = db.query(MaintenanceWindow).filter(
        MaintenanceWindow.id == window_id,
        MaintenanceWindow.tenant_id == current_user.tenant_id
    ).first()
    
    if not window:
        raise HTTPException(status_code=404, detail="Janela de manutenção não encontrada")
    
    response = MaintenanceWindowResponse.from_orm(window)
    
    # Add server name
    if window.server_id:
        server = db.query(Server).filter(Server.id == window.server_id).first()
        if server:
            response.server_name = server.hostname
    else:
        response.server_name = "Toda a Empresa"
    
    # Add creator name
    if window.created_by:
        user = db.query(User).filter(User.id == window.created_by).first()
        if user:
            response.created_by_name = user.full_name
    
    # Check if currently active
    now = datetime.utcnow()
    response.is_current = (
        window.is_active and 
        window.start_time <= now <= window.end_time
    )
    
    return response


@router.put("/{window_id}", response_model=MaintenanceWindowResponse)
async def update_maintenance_window(
    window_id: int,
    window_data: MaintenanceWindowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a maintenance window"""
    window = db.query(MaintenanceWindow).filter(
        MaintenanceWindow.id == window_id,
        MaintenanceWindow.tenant_id == current_user.tenant_id
    ).first()
    
    if not window:
        raise HTTPException(status_code=404, detail="Janela de manutenção não encontrada")
    
    # Update fields
    if window_data.title is not None:
        window.title = window_data.title
    if window_data.description is not None:
        window.description = window_data.description
    if window_data.start_time is not None:
        window.start_time = window_data.start_time
    if window_data.end_time is not None:
        window.end_time = window_data.end_time
    if window_data.is_active is not None:
        window.is_active = window_data.is_active
    
    # Validate dates
    if window.end_time <= window.start_time:
        raise HTTPException(
            status_code=400, 
            detail="Data de término deve ser posterior à data de início"
        )
    
    db.commit()
    db.refresh(window)
    
    response = MaintenanceWindowResponse.from_orm(window)
    
    # Add server name
    if window.server_id:
        server = db.query(Server).filter(Server.id == window.server_id).first()
        if server:
            response.server_name = server.hostname
    else:
        response.server_name = "Toda a Empresa"
    
    # Add creator name
    if window.created_by:
        user = db.query(User).filter(User.id == window.created_by).first()
        if user:
            response.created_by_name = user.full_name
    
    # Check if currently active
    now = datetime.utcnow()
    response.is_current = (
        window.is_active and 
        window.start_time <= now <= window.end_time
    )
    
    return response


@router.delete("/{window_id}")
async def delete_maintenance_window(
    window_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a maintenance window"""
    window = db.query(MaintenanceWindow).filter(
        MaintenanceWindow.id == window_id,
        MaintenanceWindow.tenant_id == current_user.tenant_id
    ).first()
    
    if not window:
        raise HTTPException(status_code=404, detail="Janela de manutenção não encontrada")
    
    db.delete(window)
    db.commit()
    
    return {"message": "Janela de manutenção removida com sucesso"}


@router.get("/server/{server_id}/current", response_model=Optional[MaintenanceWindowResponse])
async def get_current_maintenance_for_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if server is currently in maintenance"""
    # Verify server belongs to user's tenant
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    
    now = datetime.utcnow()
    
    # Check for active maintenance window (server-specific or company-wide)
    window = db.query(MaintenanceWindow).filter(
        MaintenanceWindow.tenant_id == current_user.tenant_id,
        MaintenanceWindow.is_active == True,
        MaintenanceWindow.start_time <= now,
        MaintenanceWindow.end_time >= now,
        or_(
            MaintenanceWindow.server_id == server_id,
            MaintenanceWindow.server_id.is_(None)
        )
    ).first()
    
    if not window:
        return None
    
    response = MaintenanceWindowResponse.from_orm(window)
    response.server_name = server.hostname if window.server_id else "Toda a Empresa"
    response.is_current = True
    
    if window.created_by:
        user = db.query(User).filter(User.id == window.created_by).first()
        if user:
            response.created_by_name = user.full_name
    
    return response
