"""
Probe Nodes Router — lista probes registradas no banco com status online/offline.

O GET /probe-nodes é usado pelo SystemHealth para exibir saúde das sondas.
Os dados vêm da tabela `probes` (banco real), não de store in-memory.
"""
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Probe, Server, Sensor

router = APIRouter(prefix="/api/v1/probe-nodes", tags=["Probe Nodes"])

OFFLINE_THRESHOLD_SEC = 120


@router.get("")
def list_nodes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Lista probes do banco com status calculado pelo último heartbeat."""
    now = datetime.now(timezone.utc)
    probes = db.query(Probe).filter(Probe.is_active == True).all()

    result = []
    for probe in probes:
        # Calcular status pelo heartbeat
        if probe.last_heartbeat:
            hb = probe.last_heartbeat
            if hb.tzinfo is None:
                hb = hb.replace(tzinfo=timezone.utc)
            elapsed = (now - hb).total_seconds()
            status = "online" if elapsed < OFFLINE_THRESHOLD_SEC else "offline"
            last_hb_iso = hb.isoformat()
        else:
            status = "offline"
            last_hb_iso = None

        # Contar servidores e sensores ativos desta probe
        servers_count = db.query(Server).filter(
            Server.probe_id == probe.id,
            Server.is_active == True
        ).count()

        # Sensores via servidor (caminho principal) + sensores standalone com probe_id direto
        sensors_via_server = db.query(Sensor).join(Server, Sensor.server_id == Server.id).filter(
            Server.probe_id == probe.id,
            Sensor.is_active == True
        ).count()
        sensors_standalone = db.query(Sensor).filter(
            Sensor.probe_id == probe.id,
            Sensor.server_id == None,
            Sensor.is_active == True
        ).count()
        sensors_count = sensors_via_server + sensors_standalone

        result.append({
            "id": str(probe.id),
            "name": probe.name,
            "location": f"Tenant {probe.tenant_id}",
            "version": probe.version or "—",
            "status": status,
            "last_heartbeat": last_hb_iso,
            "capacity": 500,
            "sensors_active": sensors_count,
            "servers_monitored": servers_count,
            # Métricas de runtime do processo da probe
            "cpu_percent": probe.cpu_percent or 0.0,
            "memory_mb": probe.memory_mb or 0.0,
            "queue_depth": 0,
            "wmi_connections": 0,
            "snmp_connections": 0,
        })

    return {
        "nodes": result,
        "total": len(result),
        "online": sum(1 for n in result if n["status"] == "online"),
        "offline": sum(1 for n in result if n["status"] == "offline"),
    }
