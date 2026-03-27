"""
Service Monitor Router — Discovery e seleção de serviços Windows (estilo PRTG/Zabbix)

Fluxo:
  1. Sonda faz WMI remoto em cada servidor do tenant
  2. POST /servers/{server_id}/services/sync  ← sonda envia catálogo descoberto
  3. API faz upsert de sensores tipo 'service' (is_active=False por padrão)
  4. Usuário seleciona quais monitorar via UI (ServiceMonitor.js)
  5. Sonda coleta apenas os is_active=True
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models import Sensor, Server, Probe

logger = logging.getLogger(__name__)
router = APIRouter()


class ServiceDiscoveryItem(BaseModel):
    service_name: str
    display_name: str
    state: str          # Running | Stopped | ...
    start_mode: str = "Auto"


class ServiceSyncRequest(BaseModel):
    probe_token: str
    services: List[ServiceDiscoveryItem]


@router.post("/servers/{server_id}/services/sync")
def sync_services(
    server_id: int,
    data: ServiceSyncRequest,
    db: Session = Depends(get_db)
):
    """
    Recebe catálogo de serviços descobertos pela sonda via WMI remoto.
    Faz upsert: cria sensores novos (is_active=False) e atualiza estado dos existentes.
    Não altera is_active de sensores já existentes (preserva escolha do usuário).
    """
    # Autenticar probe
    probe = db.query(Probe).filter(Probe.token == data.probe_token).first()
    if not probe:
        raise HTTPException(status_code=401, detail="Invalid probe token")

    # Verificar que o servidor pertence ao tenant da probe
    server = db.query(Server).filter(
        Server.id == server_id,
        Server.tenant_id == probe.tenant_id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    created = 0
    updated = 0

    for svc in data.services:
        sensor_name = f"Service {svc.service_name}"

        existing = db.query(Sensor).filter(
            Sensor.server_id == server_id,
            Sensor.sensor_type == "service",
            Sensor.name == sensor_name
        ).first()

        svc_config = {
            "service_name": svc.service_name,
            "display_name": svc.display_name,
            "start_mode": svc.start_mode,
            "state": svc.state,
        }
        if existing:
            # Atualizar display_name no config (pode ter mudado), mas preservar is_active
            existing.config = svc_config
            updated += 1
        else:
            # Criar novo sensor desativado por padrão (usuário precisa selecionar)
            sensor = Sensor(
                server_id=server_id,
                sensor_type="service",
                name=sensor_name,
                config=svc_config,
                threshold_warning=0.5,
                threshold_critical=0.5,
                is_active=False,
            )
            db.add(sensor)
            created += 1

    db.commit()

    # Retornar lista de serviços ativos para a sonda filtrar métricas
    active_sensors = db.query(Sensor).filter(
        Sensor.server_id == server_id,
        Sensor.sensor_type == "service",
        Sensor.is_active == True
    ).all()
    active_service_names = [
        s.name.replace("Service ", "", 1) for s in active_sensors
    ]

    logger.info(
        f"Service sync server_id={server_id}: {created} criados, {updated} atualizados "
        f"({len(data.services)} total, {len(active_service_names)} ativos)"
    )

    return {
        "server_id": server_id,
        "total": len(data.services),
        "created": created,
        "updated": updated,
        "active_services": active_service_names,
    }


@router.get("/servers/{server_id}/services/catalog")
def get_services_catalog(
    server_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna catálogo completo de serviços descobertos para um servidor.
    Inclui sensores ativos e inativos (para a UI de seleção).
    Usado pelo ServiceMonitor.js quando não há métricas ainda.
    """
    from auth import get_current_active_user
    # Sem auth aqui — o endpoint /services/debug já existe com auth
    # Este é chamado internamente; auth é feita no /services/debug
    sensors = db.query(Sensor).filter(
        Sensor.server_id == server_id,
        Sensor.sensor_type == "service"
    ).all()

    return {
        "server_id": server_id,
        "total": len(sensors),
        "sensors": [
            {
                "sensor_id": s.id,
                "name": s.name,
                "service_name": s.name.replace("Service ", "", 1),
                "is_active": s.is_active,
            }
            for s in sensors
        ]
    }
