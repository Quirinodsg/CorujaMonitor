from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import secrets

from database import get_db
from models import Probe, User
from auth import get_current_active_user

router = APIRouter()

class ProbeCreate(BaseModel):
    name: str
    tenant_id: Optional[int] = None  # Admin pode especificar tenant_id

class ProbeResponse(BaseModel):
    id: int
    name: str
    token: str
    is_active: bool
    last_heartbeat: Optional[datetime]
    version: Optional[str]
    tenant_id: int  # Adicionar tenant_id na resposta
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ProbeResponse)
async def create_probe(
    probe: ProbeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Se admin especificou tenant_id, usar ele. Senão, usar do usuário atual
    if probe.tenant_id is not None and current_user.role == 'admin':
        tenant_id = probe.tenant_id
    else:
        tenant_id = current_user.tenant_id
    
    token = secrets.token_urlsafe(32)
    new_probe = Probe(
        tenant_id=tenant_id,
        name=probe.name,
        token=token
    )
    db.add(new_probe)
    db.commit()
    db.refresh(new_probe)
    return new_probe

@router.get("/", response_model=List[ProbeResponse])
async def list_probes(
    tenant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Se tenant_id foi especificado (usado pela página de Companies)
    if tenant_id is not None:
        if current_user.role == 'admin':
            # Admin pode ver probes de qualquer tenant
            probes = db.query(Probe).filter(Probe.tenant_id == tenant_id).all()
        else:
            # Usuário normal só vê do seu tenant
            if tenant_id != current_user.tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
            probes = db.query(Probe).filter(Probe.tenant_id == tenant_id).all()
    else:
        # Sem tenant_id especificado
        if current_user.role == 'admin':
            # Admin vê todas as probes
            probes = db.query(Probe).all()
        else:
            # Usuário normal vê apenas do seu tenant
            probes = db.query(Probe).filter(Probe.tenant_id == current_user.tenant_id).all()
    
    return probes

@router.post("/heartbeat")
async def probe_heartbeat(
    probe_token: str,
    version: str,
    db: Session = Depends(get_db)
):
    probe = db.query(Probe).filter(Probe.token == probe_token).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    probe.last_heartbeat = datetime.utcnow()
    probe.version = version
    db.commit()
    
    return {"status": "ok", "probe_id": probe.id}


@router.delete("/{probe_id}")
async def delete_probe(
    probe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a probe
    Admin can delete any probe, users can only delete probes from their tenant
    """
    probe = db.query(Probe).filter(Probe.id == probe_id).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # Check permissions
    if current_user.role != 'admin' and probe.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete probe
    db.delete(probe)
    db.commit()
    
    return {"message": f"Probe {probe.name} deleted successfully"}


@router.get("/servers")
async def get_probe_servers(
    probe_token: str,
    db: Session = Depends(get_db)
):
    """
    Get list of servers assigned to this probe for remote monitoring
    Used by probe to collect metrics from remote servers (PRTG-style agentless)
    """
    from models import Server
    from routers.servers import decrypt_password
    
    probe = db.query(Probe).filter(Probe.token == probe_token).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # Get all active servers for this probe
    servers = db.query(Server).filter(
        Server.probe_id == probe.id,
        Server.is_active == True
    ).all()
    
    # Format response with decrypted passwords for WMI
    result = []
    for server in servers:
        server_data = {
            "id": server.id,
            "hostname": server.hostname,
            "ip_address": server.ip_address,
            "monitoring_protocol": server.monitoring_protocol,
            "device_type": server.device_type,
            "wmi_enabled": server.wmi_enabled or False,
            "wmi_username": server.wmi_username,
            "wmi_domain": server.wmi_domain,
            "snmp_version": server.snmp_version,
            "snmp_community": server.snmp_community,
            "snmp_port": server.snmp_port
        }
        
        # Decrypt WMI password if present
        if server.wmi_password_encrypted:
            try:
                server_data["wmi_password"] = decrypt_password(server.wmi_password_encrypted)
            except:
                server_data["wmi_password"] = None
        else:
            server_data["wmi_password"] = None
        
        result.append(server_data)
    
    return result
