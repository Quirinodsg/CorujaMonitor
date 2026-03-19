"""
Fase 11 — Distributed Probes Manager Router — Coruja Monitor v3.0
FastAPI router que expõe o ProbeManager via REST.
"""
import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from engine.probe_manager import ProbeManager, MAX_LOAD

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/probe-manager", tags=["probe-manager"])

# ─── Singleton global ────────────────────────────────────────────────────────

_manager = None


def get_probe_manager() -> ProbeManager:
    global _manager
    if _manager is None:
        _manager = ProbeManager()
    return _manager


# ─── Endpoints REST ──────────────────────────────────────────────────────────

class HeartbeatRequest(BaseModel):
    probe_id: str


class RegisterProbeRequest(BaseModel):
    name: str
    probe_type: str
    subnet: str = ""
    capacity: int = 100


@router.get("/status")
def get_status():
    return get_probe_manager().get_status()


@router.post("/probes/register")
def register_probe(req: RegisterProbeRequest):
    manager = get_probe_manager()
    probe_id = uuid4()
    state = manager.register_probe(
        probe_id=probe_id,
        name=req.name,
        probe_type=req.probe_type,
        subnet=req.subnet,
        capacity=req.capacity,
    )
    return {"probe_id": str(state.probe_id), "name": state.name}


@router.post("/probes/heartbeat")
def probe_heartbeat(req: HeartbeatRequest):
    manager = get_probe_manager()
    try:
        probe_id = UUID(req.probe_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="probe_id inválido")
    manager.heartbeat(probe_id)
    return {"ok": True}


@router.post("/probes/{probe_id}/offline")
def probe_offline(probe_id: str):
    manager = get_probe_manager()
    try:
        pid = UUID(probe_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="probe_id inválido")
    manager.handle_probe_offline(pid)
    return {"ok": True}


@router.post("/probes/{probe_id}/restore")
def probe_restore(probe_id: str):
    manager = get_probe_manager()
    try:
        pid = UUID(probe_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="probe_id inválido")
    manager.restore_probe(pid)
    return {"ok": True}
