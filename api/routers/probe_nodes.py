"""
Probe Nodes Router — registro, heartbeat e status de ProbeNodes distribuídos.

Entidade ProbeNode:
  id, name, location, status, last_heartbeat, version, capacity
"""
import time
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/probe-nodes", tags=["Probe Nodes"])

OFFLINE_THRESHOLD_SEC = 120


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProbeNodeRegister(BaseModel):
    name: str
    location: Optional[str] = None
    version: str = "2.0"
    capacity: int = 500  # max sensores


class ProbeNodeHeartbeat(BaseModel):
    sensors_active: int = 0
    servers_monitored: int = 0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    queue_depth: int = 0
    wmi_connections: int = 0
    snmp_connections: int = 0


# ── In-memory store ───────────────────────────────────────────────────────────

_nodes: dict = {}  # node_id -> dict


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register")
def register_node(req: ProbeNodeRegister, current_user=Depends(get_current_user)):
    """Registra um ProbeNode no sistema."""
    node_id = f"probe-{req.name}-{int(time.time())}"
    _nodes[node_id] = {
        "id": node_id,
        "name": req.name,
        "location": req.location or "unknown",
        "version": req.version,
        "capacity": req.capacity,
        "status": "online",
        "sensors_active": 0,
        "servers_monitored": 0,
        "cpu_percent": 0.0,
        "memory_mb": 0.0,
        "queue_depth": 0,
        "wmi_connections": 0,
        "snmp_connections": 0,
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"node_id": node_id, "status": "registered"}


@router.post("/{node_id}/heartbeat")
def node_heartbeat(node_id: str, req: ProbeNodeHeartbeat, current_user=Depends(get_current_user)):
    """Recebe heartbeat de um ProbeNode (enviar a cada 60s)."""
    if node_id not in _nodes:
        raise HTTPException(status_code=404, detail="ProbeNode não encontrado")

    _nodes[node_id].update({
        "status": "online",
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "sensors_active": req.sensors_active,
        "servers_monitored": req.servers_monitored,
        "cpu_percent": req.cpu_percent,
        "memory_mb": req.memory_mb,
        "queue_depth": req.queue_depth,
        "wmi_connections": req.wmi_connections,
        "snmp_connections": req.snmp_connections,
    })
    return {"status": "ok", "node_id": node_id}


@router.get("")
def list_nodes(current_user=Depends(get_current_user)):
    """Lista todos os ProbeNodes com status atual."""
    now = time.time()
    result = []

    for node in _nodes.values():
        try:
            last_hb = datetime.fromisoformat(node["last_heartbeat"]).timestamp()
            is_offline = (now - last_hb) > OFFLINE_THRESHOLD_SEC
        except Exception:
            is_offline = True

        node["status"] = "offline" if is_offline else "online"
        result.append(dict(node))

    return {
        "nodes": result,
        "total": len(result),
        "online": sum(1 for n in result if n["status"] == "online"),
        "offline": sum(1 for n in result if n["status"] == "offline"),
    }


@router.get("/{node_id}")
def get_node(node_id: str, current_user=Depends(get_current_user)):
    """Retorna detalhes de um ProbeNode."""
    if node_id not in _nodes:
        raise HTTPException(status_code=404, detail="ProbeNode não encontrado")
    return _nodes[node_id]


@router.delete("/{node_id}")
def remove_node(node_id: str, current_user=Depends(get_current_user)):
    """Remove um ProbeNode."""
    if node_id not in _nodes:
        raise HTTPException(status_code=404, detail="ProbeNode não encontrado")
    _nodes.pop(node_id)
    return {"status": "removed", "node_id": node_id}


@router.get("/{node_id}/assign")
def assign_sensors(node_id: str, current_user=Depends(get_current_user)):
    """Retorna quantos sensores este node deve monitorar (load balancing simples)."""
    if node_id not in _nodes:
        raise HTTPException(status_code=404, detail="ProbeNode não encontrado")

    online_nodes = [n for n in _nodes.values() if n["status"] == "online"]
    if not online_nodes:
        return {"assigned_capacity": 0}

    node = _nodes[node_id]
    total_capacity = sum(n["capacity"] for n in online_nodes)
    share = node["capacity"] / total_capacity if total_capacity > 0 else 0

    return {
        "node_id": node_id,
        "capacity": node["capacity"],
        "share_pct": round(share * 100, 1),
        "online_nodes": len(online_nodes),
    }
