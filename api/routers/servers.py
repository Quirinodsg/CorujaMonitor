from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from cryptography.fernet import Fernet
import os

from database import get_db
from models import Server, User, Probe
from auth import get_current_active_user

router = APIRouter()

# WMI password encryption
def get_cipher():
    """Get Fernet cipher for password encryption"""
    key = os.getenv('WMI_ENCRYPTION_KEY')
    if not key:
        # Generate a default key for development (NOT for production!)
        key = Fernet.generate_key().decode()
        print(f"⚠️ WARNING: Using auto-generated encryption key. Set WMI_ENCRYPTION_KEY in .env for production!")
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def encrypt_password(password: str) -> str:
    """Encrypt WMI password"""
    if not password:
        return None
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    """Decrypt WMI password"""
    if not encrypted:
        return None
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()

class ServerCreate(BaseModel):
    probe_id: int
    hostname: str
    ip_address: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = 'server'  # server, switch, router, firewall, printer, storage, etc
    monitoring_protocol: Optional[str] = 'wmi'  # wmi, snmp
    snmp_version: Optional[str] = None  # v1, v2c, v3
    snmp_community: Optional[str] = None
    snmp_port: Optional[int] = 161
    environment: Optional[str] = 'production'  # production, staging, development, custom
    monitoring_schedule: Optional[dict] = None  # Custom schedule for 'custom' environment
    # WMI Remote credentials (optional)
    wmi_username: Optional[str] = None
    wmi_password: Optional[str] = None
    wmi_domain: Optional[str] = None
    wmi_enabled: Optional[bool] = True  # True por padrão para servidores WMI
    group_name: Optional[str] = None

class ServerResponse(BaseModel):
    id: int
    probe_id: int
    hostname: str
    ip_address: Optional[str]
    public_ip: Optional[str]
    os_type: Optional[str]
    os_version: Optional[str]
    group_name: Optional[str]
    tags: Optional[List[str]]
    device_type: Optional[str]
    monitoring_protocol: Optional[str]
    snmp_version: Optional[str]
    snmp_community: Optional[str]
    snmp_port: Optional[int]
    environment: Optional[str]
    monitoring_schedule: Optional[dict]
    wmi_username: Optional[str] = None
    wmi_domain: Optional[str] = None
    wmi_enabled: Optional[bool] = False
    is_active: bool
    sort_order: Optional[int] = 0
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ServerResponse)
async def create_server(
    server: ServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    probe = db.query(Probe).filter(
        Probe.id == server.probe_id,
        Probe.tenant_id == current_user.tenant_id
    ).first()
    
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # Check for duplicate IP address
    if server.ip_address:
        existing_server = db.query(Server).filter(
            Server.ip_address == server.ip_address,
            Server.tenant_id == current_user.tenant_id,
            Server.is_active == True
        ).first()
        
        if existing_server:
            raise HTTPException(
                status_code=400, 
                detail=f"Servidor com IP {server.ip_address} já existe: {existing_server.hostname} (ID: {existing_server.id})"
            )
    
    # Encrypt WMI password if provided
    wmi_password_encrypted = None
    if server.wmi_password:
        wmi_password_encrypted = encrypt_password(server.wmi_password)
    
    new_server = Server(
        tenant_id=current_user.tenant_id,
        probe_id=server.probe_id,
        hostname=server.hostname,
        ip_address=server.ip_address,
        os_type=server.os_type,
        os_version=server.os_version,
        device_type=server.device_type,
        monitoring_protocol=server.monitoring_protocol,
        snmp_version=server.snmp_version,
        snmp_community=server.snmp_community,
        snmp_port=server.snmp_port,
        environment=server.environment,
        monitoring_schedule=server.monitoring_schedule,
        wmi_username=server.wmi_username,
        wmi_password_encrypted=wmi_password_encrypted,
        wmi_domain=server.wmi_domain,
        wmi_enabled=server.wmi_enabled,
        group_name=server.group_name
    )
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    
    # Auto-create default sensors for Windows servers
    if server.device_type == 'server' and server.monitoring_protocol == 'wmi':
        from models import Sensor, DefaultSensorProfile

        # Mapeamento device_type → asset_type
        asset_type_map = {
            'server': 'physical_server',
            'vm': 'VM',
            'switch': 'network_device',
            'router': 'network_device',
            'firewall': 'network_device',
        }
        asset_type = asset_type_map.get((server.device_type or 'server').lower(), 'physical_server')

        profiles = db.query(DefaultSensorProfile).filter(
            DefaultSensorProfile.asset_type == asset_type
        ).all()

        if profiles:
            for p in profiles:
                if not p.enabled:
                    continue
                sensor = Sensor(
                    server_id=new_server.id,
                    name=p.sensor_type.replace('_', ' ').title(),
                    sensor_type=p.sensor_type,
                    alert_mode=p.alert_mode,
                    threshold_warning=p.threshold_warning,
                    threshold_critical=p.threshold_critical,
                    is_active=True
                )
                db.add(sensor)
        else:
            # Perfil de fábrica hardcoded
            factory = [
                {"name": "CPU Usage",   "sensor_type": "cpu",         "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
                {"name": "Memory Usage","sensor_type": "memory",       "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
                {"name": "Disk C:",     "sensor_type": "disk",         "alert_mode": "normal",      "threshold_warning": 80, "threshold_critical": 95},
                {"name": "Network IN",  "sensor_type": "network_in",   "alert_mode": "metric_only", "threshold_warning": 80, "threshold_critical": 95},
                {"name": "Network OUT", "sensor_type": "network_out",  "alert_mode": "metric_only", "threshold_warning": 80, "threshold_critical": 95},
                {"name": "Uptime",      "sensor_type": "uptime",       "alert_mode": "normal",      "threshold_warning": None, "threshold_critical": None},
            ]
            for s in factory:
                sensor = Sensor(
                    server_id=new_server.id,
                    name=s["name"],
                    sensor_type=s["sensor_type"],
                    alert_mode=s["alert_mode"],
                    threshold_warning=s["threshold_warning"],
                    threshold_critical=s["threshold_critical"],
                    is_active=True
                )
                db.add(sensor)

        db.commit()
    
    # Auto-create default sensors for SNMP devices (routers, switches, etc)
    elif server.monitoring_protocol == 'snmp':
        from models import Sensor
        
        # SNMP OIDs padrão baseados em PRTG e Zabbix
        # PING removido - agora é criado automaticamente pelo worker a cada 60s
        snmp_sensors = [
            {
                "name": "SNMP_Uptime",
                "sensor_type": "snmp_uptime",
                "threshold_warning": None,
                "threshold_critical": None,
                "snmp_oid": "1.3.6.1.2.1.1.3.0"  # sysUpTime
            },
            {
                "name": "SNMP_CPU_Load",
                "sensor_type": "snmp_cpu",
                "threshold_warning": 80,
                "threshold_critical": 95,
                "snmp_oid": "1.3.6.1.4.1.2021.10.1.3.1"  # laLoad.1 (1 min avg)
            },
            {
                "name": "SNMP_Memory_Usage",
                "sensor_type": "snmp_memory",
                "threshold_warning": 80,
                "threshold_critical": 95,
                "snmp_oid": "1.3.6.1.4.1.2021.4.6.0"  # memTotalFree
            },
            {
                "name": "SNMP_Traffic_In",
                "sensor_type": "snmp_traffic",
                "threshold_warning": 80,
                "threshold_critical": 95,
                "snmp_oid": "1.3.6.1.2.1.2.2.1.10.1"  # ifInOctets (interface 1)
            },
            {
                "name": "SNMP_Traffic_Out",
                "sensor_type": "snmp_traffic",
                "threshold_warning": 80,
                "threshold_critical": 95,
                "snmp_oid": "1.3.6.1.2.1.2.2.1.16.1"  # ifOutOctets (interface 1)
            },
            {
                "name": "SNMP_Interface_Status",
                "sensor_type": "snmp_interface",
                "threshold_warning": None,
                "threshold_critical": None,
                "snmp_oid": "1.3.6.1.2.1.2.2.1.8.1"  # ifOperStatus (interface 1)
            }
        ]
        
        for sensor_data in snmp_sensors:
            sensor = Sensor(
                server_id=new_server.id,
                name=sensor_data["name"],
                sensor_type=sensor_data["sensor_type"],
                threshold_warning=sensor_data["threshold_warning"],
                threshold_critical=sensor_data["threshold_critical"],
                collection_protocol='snmp' if sensor_data["snmp_oid"] else 'icmp',
                snmp_oid=sensor_data["snmp_oid"],
                is_active=True
            )
            db.add(sensor)
        
        db.commit()
    
    return new_server

@router.get("/", response_model=List[ServerResponse])
async def list_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Admin vê todos os servidores, usuário normal vê apenas do seu tenant
    if current_user.role == 'admin':
        servers = db.query(Server).order_by(Server.sort_order, Server.id).all()
    else:
        servers = db.query(Server).filter(Server.tenant_id == current_user.tenant_id).order_by(Server.sort_order, Server.id).all()
    return servers


class ServerUpdate(BaseModel):
    group_name: Optional[str] = None
    tags: Optional[List[str]] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None
    monitoring_protocol: Optional[str] = None
    snmp_version: Optional[str] = None
    snmp_community: Optional[str] = None
    snmp_port: Optional[int] = None
    environment: Optional[str] = None
    monitoring_schedule: Optional[dict] = None


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    server_update: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if server_update.group_name is not None:
        server.group_name = server_update.group_name
    if server_update.tags is not None:
        server.tags = server_update.tags
    if server_update.ip_address is not None:
        server.ip_address = server_update.ip_address
    if server_update.device_type is not None:
        server.device_type = server_update.device_type
    if server_update.monitoring_protocol is not None:
        server.monitoring_protocol = server_update.monitoring_protocol
    if server_update.snmp_version is not None:
        server.snmp_version = server_update.snmp_version
    if server_update.snmp_community is not None:
        server.snmp_community = server_update.snmp_community
    if server_update.snmp_port is not None:
        server.snmp_port = server_update.snmp_port
    if server_update.environment is not None:
        server.environment = server_update.environment
    if server_update.monitoring_schedule is not None:
        server.monitoring_schedule = server_update.monitoring_schedule
    
    db.commit()
    db.refresh(server)
    return server


@router.delete("/{server_id}")
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a server and all its associated data (sensors, metrics, incidents)
    """
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Delete associated data in order
    from models import Sensor, Metric, Incident, RemediationLog, SensorNote, AIAnalysisLog
    
    # Get all sensors for this server
    sensors = db.query(Sensor).filter(Sensor.server_id == server_id).all()
    sensor_ids = [s.id for s in sensors]
    
    if sensor_ids:
        # Get all incidents for these sensors
        incidents = db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).all()
        incident_ids = [i.id for i in incidents]
        
        if incident_ids:
            # Delete AI analysis logs (they reference incidents)
            db.query(AIAnalysisLog).filter(AIAnalysisLog.incident_id.in_(incident_ids)).delete(synchronize_session=False)
            
            # Delete remediation logs (they reference incidents)
            db.query(RemediationLog).filter(RemediationLog.incident_id.in_(incident_ids)).delete(synchronize_session=False)
        
        # Delete incidents for these sensors
        db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
        
        # Delete sensor notes (they reference sensors)
        db.query(SensorNote).filter(SensorNote.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
        
        # Delete metrics for these sensors
        db.query(Metric).filter(Metric.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
        
        # Delete sensors
        db.query(Sensor).filter(Sensor.server_id == server_id).delete(synchronize_session=False)
    
    # Delete server
    db.delete(server)
    db.commit()
    
    return {"message": f"Server '{server.hostname}' and all associated data deleted successfully"}


@router.post("/resolve-ips")
async def resolve_missing_ips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Resolve IPs via DNS para servidores sem ip_address configurado.
    Útil para servidores cadastrados apenas com hostname (ex: SRVHVSPRD011).
    """
    import socket

    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Server.is_active == True,
        Server.ip_address == None
    ).all()

    resolved = []
    failed = []

    for server in servers:
        try:
            ip = socket.gethostbyname(server.hostname)
            server.ip_address = ip
            db.commit()
            resolved.append({"hostname": server.hostname, "ip": ip})
        except Exception as e:
            failed.append({"hostname": server.hostname, "error": str(e)})

    return {
        "resolved": resolved,
        "failed": failed,
        "total_resolved": len(resolved)
    }



async def create_ping_sensor(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create PING sensor for an existing server if it doesn't exist yet"""
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if not server.ip_address:
        raise HTTPException(status_code=400, detail="Server has no IP address configured")
    
    from models import Sensor
    existing = db.query(Sensor).filter(
        Sensor.server_id == server_id,
        Sensor.sensor_type == 'ping'
    ).first()
    
    if existing:
        return {"message": "PING sensor already exists", "sensor_id": existing.id}
    
    ping_sensor = Sensor(
        server_id=server_id,
        sensor_type='ping',
        name='PING',
        threshold_warning=100,
        threshold_critical=200,
        is_active=True
    )
    db.add(ping_sensor)
    db.commit()
    db.refresh(ping_sensor)
    
    return {"message": "PING sensor created", "sensor_id": ping_sensor.id}


@router.post("/create-ping-all")
async def create_ping_all_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create PING sensor for all servers that don't have one yet"""
    from models import Sensor
    
    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Server.is_active == True,
        Server.ip_address != None
    ).all()
    
    created = []
    skipped = []
    
    for server in servers:
        existing = db.query(Sensor).filter(
            Sensor.server_id == server.id,
            Sensor.sensor_type == 'ping'
        ).first()
        
        if existing:
            skipped.append(server.hostname)
            continue
        
        ping_sensor = Sensor(
            server_id=server.id,
            sensor_type='ping',
            name='PING',
            threshold_warning=100,
            threshold_critical=200,
            is_active=True
        )
        db.add(ping_sensor)
        created.append(server.hostname)
    
    db.commit()
    
    return {
        "created": created,
        "skipped": skipped,
        "total_created": len(created)
    }


# Auto-registration endpoints for probes
@router.get("/check")
async def check_server_exists(
    probe_token: str,
    hostname: str,
    db: Session = Depends(get_db)
):
    """
    Check if a server with given hostname already exists for this probe
    Used by probe for auto-registration
    """
    # Find probe by token
    probe = db.query(Probe).filter(Probe.token == probe_token).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # Check if server exists
    server = db.query(Server).filter(
        Server.probe_id == probe.id,
        Server.hostname == hostname
    ).first()
    
    if server:
        return {
            "exists": True,
            "server_id": server.id,
            "hostname": server.hostname,
            "ip_address": server.ip_address
        }
    else:
        return {
            "exists": False
        }


@router.post("/auto-register")
async def auto_register_server(
    probe_token: str,
    server_data: dict,
    db: Session = Depends(get_db)
):
    """
    Auto-register a server when probe starts
    Used by probe to automatically create its server entry
    """
    # Find probe by token
    probe = db.query(Probe).filter(Probe.token == probe_token).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    hostname = server_data.get("hostname")
    ip_address = server_data.get("ip_address", "127.0.0.1")
    os_info = server_data.get("os_info", "Unknown")
    description = server_data.get("description", "Auto-registered server")
    
    # Check if server already exists
    existing_server = db.query(Server).filter(
        Server.probe_id == probe.id,
        Server.hostname == hostname
    ).first()
    
    if existing_server:
        return {
            "id": existing_server.id,
            "hostname": existing_server.hostname,
            "message": "Server already exists"
        }
    
    # Create new server
    new_server = Server(
        probe_id=probe.id,
        tenant_id=probe.tenant_id,
        hostname=hostname,
        ip_address=ip_address,
        os_type=os_info.split()[0] if os_info else "Unknown",
        os_version=os_info,
        device_type="server",
        monitoring_protocol="local",
        environment="production",
        is_active=True
    )
    
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    
    return {
        "id": new_server.id,
        "hostname": new_server.hostname,
        "ip_address": new_server.ip_address,
        "message": "Server registered successfully"
    }


class ServerReorder(BaseModel):
    sort_order: int


@router.get("/{server_id}/discover/services")
async def discover_services(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Descobre serviços Windows via WMI (Win32_Service WHERE StartMode='Auto').
    Retorna lista de serviços com nome, estado e modo de inicialização.
    """
    import logging
    logger = logging.getLogger(__name__)

    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if server.monitoring_protocol != 'wmi':
        raise HTTPException(status_code=400, detail="Server does not use WMI protocol")

    # Buscar credencial WMI
    from models import Credential
    credential = db.query(Credential).filter(
        Credential.server_id == server_id,
        Credential.credential_type == 'wmi',
        Credential.is_active == True
    ).first()

    if not credential:
        # Tentar credencial de grupo/tenant
        credential = db.query(Credential).filter(
            Credential.tenant_id == current_user.tenant_id,
            Credential.credential_type == 'wmi',
            Credential.is_active == True,
            Credential.server_id == None
        ).first()

    if not credential:
        raise HTTPException(status_code=400, detail="No WMI credential configured for this server")

    hostname = server.ip_address or server.hostname
    username = credential.wmi_username
    password = decrypt_password(credential.wmi_password_encrypted) if credential.wmi_password_encrypted else None
    domain = credential.wmi_domain or ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="WMI credential is incomplete")

    try:
        import wmi
        conn_str = f"{domain}\\{username}" if domain else username
        conn = wmi.WMI(computer=hostname, user=conn_str, password=password)
        rows = conn.query("SELECT Name,State,StartMode,DisplayName FROM Win32_Service WHERE StartMode='Auto'")
        services = [
            {
                "name": r.Name,
                "display_name": r.DisplayName,
                "state": r.State,
                "start_mode": r.StartMode,
                "is_running": r.State == "Running"
            }
            for r in rows
        ]
        return {"server_id": server_id, "hostname": server.hostname, "services": services, "total": len(services)}
    except Exception as e:
        logger.error(f"WMI service discovery failed for {hostname}: {e}")
        raise HTTPException(status_code=500, detail=f"WMI discovery failed: {str(e)}")

@router.put("/{server_id}/reorder")
async def reorder_server(
    server_id: int,
    data: ServerReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza a ordem de exibição de um servidor na árvore"""
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    server.sort_order = data.sort_order
    db.commit()
    return {"message": "Ordem atualizada", "sort_order": data.sort_order}
