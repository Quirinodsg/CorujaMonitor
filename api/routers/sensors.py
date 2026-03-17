from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import Sensor, Server, User
from auth import get_current_active_user

# Imports para teste de conexão
try:
    from pysnmp.hlapi import (
        SnmpEngine, CommunityData, UdpTransportTarget,
        ContextData, ObjectType, ObjectIdentity, getCmd
    )
    PYSNMP_AVAILABLE = True
except ImportError:
    PYSNMP_AVAILABLE = False

try:
    from azure.identity import ClientSecretCredential
    from azure.mgmt.resource import ResourceManagementClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

router = APIRouter()

class SensorCreate(BaseModel):
    server_id: int
    name: str
    sensor_type: str
    config: Optional[Dict[str, Any]] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

class StandaloneSensorCreate(BaseModel):
    probe_id: int
    name: str
    sensor_type: str
    category: str
    ip_address: Optional[str] = None
    snmp_version: Optional[str] = None
    snmp_community: Optional[str] = None
    snmp_port: Optional[int] = None
    snmp_oid: Optional[str] = None
    http_url: Optional[str] = None
    http_method: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_resource_type: Optional[str] = None
    azure_resource_name: Optional[str] = None
    threshold_warning: Optional[float] = 80
    threshold_critical: Optional[float] = 95
    description: Optional[str] = None

class SensorResponse(BaseModel):
    id: int
    server_id: Optional[int] = None
    name: str
    sensor_type: str
    config: Optional[Dict[str, Any]]
    threshold_warning: Optional[float]
    threshold_critical: Optional[float]
    is_active: bool
    is_acknowledged: Optional[bool] = False
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    verification_status: Optional[str] = None
    last_note: Optional[str] = None
    last_note_by: Optional[int] = None
    last_note_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

@router.post("/", response_model=SensorResponse)
async def create_sensor(
    sensor: SensorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    server = db.query(Server).filter(
        Server.id == sensor.server_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    new_sensor = Sensor(**sensor.dict())
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)
    return new_sensor

@router.get("/", response_model=List[SensorResponse])
async def list_sensors(
    server_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Admin vê todos os sensores, usuário normal vê apenas do seu tenant
    if current_user.role == 'admin':
        query = db.query(Sensor).join(Server)
    else:
        query = db.query(Sensor).join(Server).filter(Server.tenant_id == current_user.tenant_id)
    
    if server_id:
        query = query.filter(Sensor.server_id == server_id)
    
    sensors = query.all()
    return sensors


@router.delete("/{sensor_id}")
async def delete_sensor(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Try sensor linked to a server first
    sensor = db.query(Sensor).join(Server, Sensor.server_id == Server.id).filter(
        Sensor.id == sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()

    # Fallback: standalone sensor (server_id is NULL) — verify via probe tenant
    if not sensor:
        from models import Probe
        sensor = db.query(Sensor).join(Probe, Sensor.probe_id == Probe.id).filter(
            Sensor.id == sensor_id,
            Sensor.server_id == None,
            Probe.tenant_id == current_user.tenant_id
        ).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Delete associated metrics first
    from models import Metric
    db.query(Metric).filter(Metric.sensor_id == sensor_id).delete()
    
    # Delete sensor
    db.delete(sensor)
    db.commit()
    
    return {"message": "Sensor deleted successfully"}


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    sensor_type: Optional[str] = None  # Para mover entre categorias
    is_active: Optional[bool] = None  # CORRECAO 09MAR: Campo para ativar/desativar sensor via API


@router.put("/{sensor_id}", response_model=SensorResponse)
async def update_sensor(
    sensor_id: int,
    sensor_update: SensorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify sensor belongs to user's tenant
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Update name (for renaming)
    if sensor_update.name is not None:
        sensor.name = sensor_update.name
    
    # Update sensor_type (for moving between categories)
    if sensor_update.sensor_type is not None:
        sensor.sensor_type = sensor_update.sensor_type
    
    # Update thresholds
    if sensor_update.threshold_warning is not None:
        sensor.threshold_warning = sensor_update.threshold_warning
    if sensor_update.threshold_critical is not None:
        sensor.threshold_critical = sensor_update.threshold_critical
    
    # Update is_active (for enabling/disabling sensor)
    # CORRECAO 09MAR: Permite desativar sensor sem deletar do banco
    if sensor_update.is_active is not None:
        sensor.is_active = sensor_update.is_active
    
    db.commit()
    db.refresh(sensor)
    
    return sensor


@router.post("/fix-categories")
async def fix_sensor_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Corrige automaticamente as categorias dos sensores baseado no nome"""
    
    def detect_sensor_type(sensor_name: str, current_type: str) -> str:
        """Detecta o tipo correto do sensor baseado no nome"""
        name_lower = sensor_name.lower()
        
        # Docker
        if any(keyword in name_lower for keyword in ['docker', 'container']):
            return 'docker'
        
        # Network
        if any(keyword in name_lower for keyword in ['network', 'rede', '_in', '_out', 'bandwidth', 'traffic']):
            return 'network'
        
        # Ping
        if 'ping' in name_lower:
            return 'ping'
        
        # CPU
        if 'cpu' in name_lower or 'processor' in name_lower:
            return 'cpu'
        
        # Memory
        if any(keyword in name_lower for keyword in ['memory', 'mem', 'ram', 'memória']):
            return 'memory'
        
        # Disk
        if any(keyword in name_lower for keyword in ['disk', 'disco', 'hdd', 'ssd', 'storage']):
            return 'disk'
        
        # System/Uptime
        if any(keyword in name_lower for keyword in ['uptime', 'system', 'sistema']):
            return 'system'
        
        # Service
        if any(keyword in name_lower for keyword in ['service', 'serviço', 'servico']):
            return 'service'
        
        # Hyper-V
        if 'hyperv' in name_lower or 'hyper-v' in name_lower:
            return 'hyperv'
        
        # HTTP
        if 'http' in name_lower or 'https' in name_lower:
            return 'http'
        
        # Port
        if 'port' in name_lower or 'porta' in name_lower:
            return 'port'
        
        # DNS
        if 'dns' in name_lower:
            return 'dns'
        
        # SSL
        if 'ssl' in name_lower or 'tls' in name_lower or 'certificate' in name_lower:
            return 'ssl'
        
        # SNMP
        if 'snmp' in name_lower:
            return 'snmp'
        
        # Se não detectou nada, mantém o tipo atual
        return current_type
    
    try:
        # Get all sensors for user's tenant
        sensors = db.query(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id
        ).all()
        
        fixed_sensors = []
        
        for sensor in sensors:
            detected_type = detect_sensor_type(sensor.name, sensor.sensor_type)
            
            if detected_type != sensor.sensor_type:
                old_type = sensor.sensor_type
                sensor.sensor_type = detected_type
                fixed_sensors.append({
                    "id": sensor.id,
                    "name": sensor.name,
                    "old_type": old_type,
                    "new_type": detected_type
                })
        
        db.commit()
        
        return {
            "message": "Categorias corrigidas com sucesso",
            "total_sensors": len(sensors),
            "fixed_count": len(fixed_sensors),
            "fixed_sensors": fixed_sensors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ===== STANDALONE SENSORS (Biblioteca de Sensores) =====

@router.post("/standalone", response_model=SensorResponse)
async def create_standalone_sensor(
    sensor: StandaloneSensorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cria um sensor independente (não vinculado a servidor)"""
    from models import Probe
    
    # Verificar se a probe existe e pertence ao tenant do usuário
    probe = db.query(Probe).filter(
        Probe.id == sensor.probe_id,
        Probe.tenant_id == current_user.tenant_id
    ).first()
    
    if not probe:
        raise HTTPException(status_code=404, detail="Probe not found")
    
    # Criar configuração do sensor
    config = {
        "category": sensor.category,
        "ip_address": sensor.ip_address,
        "description": sensor.description
    }
    
    # Adicionar configurações SNMP se aplicável
    if sensor.snmp_version:
        config["snmp"] = {
            "version": sensor.snmp_version,
            "community": sensor.snmp_community,
            "port": sensor.snmp_port,
            "oid": sensor.snmp_oid
        }
    
    # Adicionar configurações HTTP se aplicável
    if sensor.http_url:
        config["http"] = {
            "url": sensor.http_url,
            "method": sensor.http_method
        }
    
    # Adicionar configurações Azure se aplicável
    if sensor.azure_subscription_id:
        config["azure"] = {
            "subscription_id": sensor.azure_subscription_id,
            "tenant_id": sensor.azure_tenant_id,
            "client_id": sensor.azure_client_id,
            "client_secret": sensor.azure_client_secret,
            "resource_type": sensor.azure_resource_type,
            "resource_name": sensor.azure_resource_name
        }
    
    # Criar sensor sem server_id (standalone)
    new_sensor = Sensor(
        server_id=None,  # Sensor independente
        probe_id=sensor.probe_id,
        name=sensor.name,
        sensor_type=sensor.sensor_type,
        config=config,
        threshold_warning=sensor.threshold_warning,
        threshold_critical=sensor.threshold_critical,
        is_active=True
    )
    
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)
    
    return new_sensor


@router.get("/standalone", response_model=List[SensorResponse])
async def list_standalone_sensors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista sensores independentes (não vinculados a servidores)"""
    from models import Probe
    
    # Buscar sensores sem server_id que pertencem às probes do tenant
    sensors = db.query(Sensor).join(Probe).filter(
        Sensor.server_id == None,
        Probe.tenant_id == current_user.tenant_id
    ).all()
    
    # Adicionar categoria do config para facilitar no frontend
    for sensor in sensors:
        if sensor.config and 'category' in sensor.config:
            sensor.category = sensor.config['category']
        if sensor.config and 'description' in sensor.config:
            sensor.description = sensor.config['description']
        if sensor.config and 'ip_address' in sensor.config:
            sensor.ip_address = sensor.config['ip_address']
    
    return sensors


@router.get("/standalone/by-probe")
async def list_standalone_sensors_by_probe(
    probe_token: str,
    db: Session = Depends(get_db)
):
    """Endpoint para a probe buscar seus sensores standalone (HTTP, SNMP, etc.)"""
    from models import Probe
    probe = db.query(Probe).filter(Probe.token == probe_token).first()
    if not probe:
        raise HTTPException(status_code=401, detail="Invalid probe token")

    sensors = db.query(Sensor).filter(
        Sensor.probe_id == probe.id,
        Sensor.server_id == None,
        Sensor.is_active == True
    ).all()

    result = []
    for s in sensors:
        cfg = s.config or {}
        # http config can be stored as cfg["http"]["url"] or cfg["http_url"] (legacy)
        http_cfg = cfg.get("http") or {}
        http_url = http_cfg.get("url") or cfg.get("http_url")
        http_method = http_cfg.get("method") or cfg.get("http_method", "GET")
        result.append({
            "id": s.id,
            "name": s.name,
            "sensor_type": s.sensor_type,
            "http_url": http_url,
            "http_method": http_method,
            "threshold_warning": s.threshold_warning,
            "threshold_critical": s.threshold_critical,
        })
    return result


class ConnectionTestRequest(BaseModel):
    type: str  # azure, snmp, http, aws
    # Azure
    subscription_id: Optional[str] = None
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    # SNMP
    ip_address: Optional[str] = None
    snmp_version: Optional[str] = None
    snmp_community: Optional[str] = None
    snmp_port: Optional[int] = None
    snmp_oid: Optional[str] = None
    # HTTP
    url: Optional[str] = None
    method: Optional[str] = None


@router.post("/clear-resolved-notes")
async def clear_resolved_sensor_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Limpa anotações de sensores que foram resolvidos e estão OK"""
    try:
        from models import Metric
        
        # Buscar sensores com anotação "Resolvido" que estão OK
        sensors_to_clear = []
        
        sensors = db.query(Sensor).filter(
            Sensor.last_note.ilike('%resolvido%')
        ).all()
        
        for sensor in sensors:
            # Verificar última métrica
            latest_metric = db.query(Metric).filter(
                Metric.sensor_id == sensor.id
            ).order_by(Metric.timestamp.desc()).first()
            
            if latest_metric and latest_metric.status == 'ok':
                # Limpar anotações
                sensor.last_note = None
                sensor.last_note_by = None
                sensor.last_note_at = None
                sensor.verification_status = None
                
                sensors_to_clear.append({
                    "id": sensor.id,
                    "name": sensor.name,
                    "sensor_type": sensor.sensor_type
                })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Limpas {len(sensors_to_clear)} anotações de sensores resolvidos",
            "sensors_cleared": sensors_to_clear
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection")
async def test_sensor_connection(
    test_data: ConnectionTestRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Testa conexão com o sensor antes de criar"""
    
    try:
        if test_data.type == 'azure':
            # Testar conexão Azure
            from azure.identity import ClientSecretCredential
            from azure.mgmt.resource import ResourceManagementClient
            
            try:
                credential = ClientSecretCredential(
                    tenant_id=test_data.tenant_id,
                    client_id=test_data.client_id,
                    client_secret=test_data.client_secret
                )
                
                # Tentar listar resource groups para validar credenciais
                resource_client = ResourceManagementClient(credential, test_data.subscription_id)
                resource_groups = list(resource_client.resource_groups.list())
                
                return {
                    "success": True,
                    "message": f"✅ Conexão Azure estabelecida com sucesso! Encontrados {len(resource_groups)} resource groups.",
                    "details": {
                        "subscription_id": test_data.subscription_id,
                        "tenant_id": test_data.tenant_id,
                        "resource_groups_count": len(resource_groups)
                    }
                }
            except Exception as azure_error:
                return {
                    "success": False,
                    "message": "❌ Falha na autenticação Azure. Verifique as credenciais.",
                    "error": str(azure_error)
                }
        
        elif test_data.type == 'snmp':
            # Testar conexão SNMP
            if not PYSNMP_AVAILABLE:
                return {
                    "success": False,
                    "message": "❌ Biblioteca pysnmp não está instalada"
                }
            
            try:
                # OID padrão: sysDescr (1.3.6.1.2.1.1.1.0)
                oid = test_data.snmp_oid or '1.3.6.1.2.1.1.1.0'
                
                # Configurar versão SNMP
                if test_data.snmp_version == 'v3':
                    raise HTTPException(status_code=400, detail="SNMP v3 requer configuração adicional")
                
                community = CommunityData(test_data.snmp_community or 'public', mpModel=1 if test_data.snmp_version == 'v2c' else 0)
                
                iterator = getCmd(
                    SnmpEngine(),
                    community,
                    UdpTransportTarget((test_data.ip_address, test_data.snmp_port or 161), timeout=5, retries=1),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
                
                errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                
                if errorIndication:
                    return {
                        "success": False,
                        "message": f"❌ Erro SNMP: {errorIndication}",
                        "error": str(errorIndication)
                    }
                elif errorStatus:
                    return {
                        "success": False,
                        "message": f"❌ Erro SNMP: {errorStatus.prettyPrint()}",
                        "error": f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}"
                    }
                else:
                    result_value = str(varBinds[0][1])
                    return {
                        "success": True,
                        "message": f"✅ Conexão SNMP estabelecida com sucesso!",
                        "details": {
                            "ip_address": test_data.ip_address,
                            "oid": oid,
                            "value": result_value[:100]  # Limitar tamanho
                        }
                    }
            except Exception as snmp_error:
                return {
                    "success": False,
                    "message": "❌ Falha na conexão SNMP. Verifique IP, community e firewall.",
                    "error": str(snmp_error)
                }
        
        elif test_data.type == 'http':
            # Testar conexão HTTP
            import requests
            import time
            
            try:
                start_time = time.time()
                response = requests.request(
                    method=test_data.method or 'GET',
                    url=test_data.url,
                    timeout=10,
                    verify=False  # Ignorar SSL para teste
                )
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status_code < 400:
                    return {
                        "success": True,
                        "message": f"✅ Conexão HTTP estabelecida com sucesso!",
                        "details": {
                            "url": test_data.url,
                            "status_code": response.status_code,
                            "response_time": response_time
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": f"❌ HTTP retornou status {response.status_code}",
                        "details": {
                            "url": test_data.url,
                            "status_code": response.status_code,
                            "response_time": response_time
                        }
                    }
            except Exception as http_error:
                return {
                    "success": False,
                    "message": "❌ Falha na conexão HTTP. Verifique a URL.",
                    "error": str(http_error)
                }
        
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de teste não suportado: {test_data.type}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

