from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import SensorNote, Sensor, Server, User
from auth import get_current_active_user

router = APIRouter()


class SensorNoteCreate(BaseModel):
    sensor_id: int
    note: str
    status: str  # pending, in_analysis, verified, resolved


class SensorNoteResponse(BaseModel):
    id: int
    sensor_id: int
    user_id: int
    note: str
    status: str
    created_at: datetime
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.post("/", response_model=SensorNoteResponse)
async def create_sensor_note(
    note_data: SensorNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new sensor note"""
    # Verify sensor belongs to user's tenant
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == note_data.sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Validate status
    valid_statuses = ["pending", "in_analysis", "verified", "resolved"]
    if note_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Create note
    new_note = SensorNote(
        sensor_id=note_data.sensor_id,
        user_id=current_user.id,
        note=note_data.note,
        status=note_data.status
    )
    
    db.add(new_note)
    
    # Update sensor with latest note info
    sensor.verification_status = note_data.status
    sensor.last_note = note_data.note
    sensor.last_note_by = current_user.id
    sensor.last_note_at = datetime.now()
    
    # IMPORTANTE: Reconhecer sensor quando colocado em análise
    # Isso suprime alertas e ligações
    if note_data.status in ['in_analysis', 'verified']:
        sensor.is_acknowledged = True
        sensor.acknowledged_by = current_user.id
        sensor.acknowledged_at = datetime.now()
    
    # Desreconhecer se voltar para pending ou for resolvido
    if note_data.status in ['pending', 'resolved']:
        sensor.is_acknowledged = False
        sensor.acknowledged_by = None
        sensor.acknowledged_at = None
    
    db.commit()
    db.refresh(new_note)
    
    # Add user name to response
    response = SensorNoteResponse.from_orm(new_note)
    response.user_name = current_user.full_name
    
    return response


@router.get("/sensor/{sensor_id}", response_model=List[SensorNoteResponse])
async def list_sensor_notes(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all notes for a sensor"""
    # Verify sensor belongs to user's tenant
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Get notes with user info
    notes = db.query(SensorNote).filter(
        SensorNote.sensor_id == sensor_id
    ).order_by(SensorNote.created_at.desc()).all()
    
    # Add user names
    response_notes = []
    for note in notes:
        note_response = SensorNoteResponse.from_orm(note)
        user = db.query(User).filter(User.id == note.user_id).first()
        if user:
            note_response.user_name = user.full_name
        response_notes.append(note_response)
    
    return response_notes


@router.delete("/{note_id}")
async def delete_sensor_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a sensor note"""
    note = db.query(SensorNote).filter(SensorNote.id == note_id).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Verify sensor belongs to user's tenant
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == note.sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Only allow deletion by note creator or admin
    if note.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Can only delete your own notes")
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}
