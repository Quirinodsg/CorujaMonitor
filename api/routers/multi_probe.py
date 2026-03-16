"""
Multi-Probe Router - Registro e gerenciamento de múltiplas probes
Suporta tipos: probe_datacenter, probe_cloud, probe_edge
"""
import time
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/v1/multi-probe", tags=["Multi-Probe"])

PROBE_TYPES = {"probe_datacenter", "probe_cloud", "probe_edge"}
OFFLINE_THRESHOLD_SECONDS = 120


# ── Schemas ──────────────────────────────────────────────────────────────────

class ProbeRegisterRequest(BaseModel):
    probe_name: str
    probe_type: str
    location: Optional[str] = None
    capacity: int = 100  # max servidores

class HeartbeatRequest(BaseModel):
    sensors_active: int = 0
    servers_monitored: int = 0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0


# ── In-memory store (substituir por DB em produção) ───────────────────────────

_probes: dict = {}  # probe_id -> dict


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register")
def register_probe(req: ProbeRegisterRequest, current_user=Depends(get_current_user)):
    """Registra uma nova probe no sistema"""
    if req.probe_type not in PROBE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Use: {', '.join(PROBE_TYPES)}"
        )

    probe_id = f"{req.probe_type}_{req.probe_name}_{int(time.time())}"
    _probes[probe_id] = {
        "probe_id": probe_id,
        "probe_name": req.probe_name,
        "probe_type": req.probe_type,
        "location": req.location,
        "capacity": req.capacity,
        "status": "online",
        "servers_monitored": 0,
        "sensors_active": 0,
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"probe_id": probe_id, "status": "registered"}


@router.post("/{probe_id}/heartbeat")
def probe_heartbeat(probe_id: str, req: HeartbeatRequest, current_user=Depends(get_current_user)):
    """Recebe heartbeat de uma probe (deve ser enviado a cada 60s)"""
    if probe_id not in _probes:
        raise HTTPException(status_code=404, detail="Probe não encontrada")

    _probes[probe_id].update({
        "status": "online",
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "sensors_active": req.sensors_active,
        "servers_monitored": req.servers_monitored,
        "cpu_percent": req.cpu_percent,
        "memory_mb": req.memory_mb,
    })
    return {"status": "ok"}


@router.get("/status")
def probes_status(current_user=Depends(get_current_user)):
    """Dashboard de todas as probes com status atual"""
    now = time.time()
    result = []

    for probe in _probes.values():
        # Verificar se está offline
        try:
            last_hb = datetime.fromisoformat(probe["last_heartbeat"]).timestamp()
            offline = (now - last_hb) > OFFLINE_THRESHOLD_SECONDS
        except Exception:
            offline = True

        status = "offline" if offline else "online"
        if offline and probe["status"] == "online":
            probe["status"] = "offline"
            _redistribute_servers(probe["probe_id"])

        result.append({
            "probe_id": probe["probe_id"],
            "probe_name": probe["probe_name"],
            "probe_type": probe["probe_type"],
            "location": probe.get("location"),
            "status": status,
            "servers_monitored": probe.get("servers_monitored", 0),
            "sensors_active": probe.get("sensors_active", 0),
            "last_heartbeat": probe.get("last_heartbeat"),
            "cpu_percent": probe.get("cpu_percent", 0),
            "memory_mb": probe.get("memory_mb", 0),
        })

    return {"probes": result, "total": len(result)}


@router.delete("/{probe_id}")
def deregister_probe(probe_id: str, current_user=Depends(get_current_user)):
    """Remove uma probe do sistema"""
    if probe_id not in _probes:
        raise HTTPException(status_code=404, detail="Probe não encontrada")
    _probes.pop(probe_id)
    return {"status": "removed"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _redistribute_servers(offline_probe_id: str):
    """Redistribui servidores de uma probe offline para as demais online"""
    online_probes = [
        p for pid, p in _probes.items()
        if pid != offline_probe_id and p["status"] == "online"
    ]
    if not online_probes:
        return

    offline = _probes.get(offline_probe_id, {})
    servers = offline.get("servers_monitored", 0)
    if servers == 0:
        return

    per_probe = servers // len(online_probes)
    for p in online_probes:
        p["servers_monitored"] = p.get("servers_monitored", 0) + per_probe

    import logging
    logging.getLogger(__name__).warning(
        f"MultiProbe: probe {offline_probe_id} offline — "
        f"{servers} servidores redistribuídos entre {len(online_probes)} probes"
    )
