"""
Hyper-V REST API Router — Coruja Monitor
Endpoints: overview, hosts, VMs, FinOps recommendations, heatmap, AI suggestions.
Requirements: 2.1–2.10, 6.1, 6.5, 7.5, 8.1, 8.2, 9.2
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
from uuid import UUID

from database import get_db
from auth import get_current_active_user
from models import User, HyperVHost, HyperVVM, HyperVMetric, HyperVFinOpsRecommendation
from schemas.hyperv import (
    HyperVOverview,
    HyperVHostResponse,
    HyperVVMResponse,
    FinOpsRecommendation,
    AISuggestion,
    HeatmapCell,
    HeatmapResponse,
)
from services.hyperv_health import compute_health_score
from services.hyperv_finops import HyperVFinOpsEngine

router = APIRouter(prefix="/api/v1/hyperv", tags=["Hyper-V"])

VALID_PERIODS = {"24h", "7d", "30d"}
VALID_STATUSES = {"running", "stopped", "paused", "saved"}

# Map VM state strings to DB state values (case-insensitive matching)
STATE_MAP = {
    "running": "Running",
    "stopped": "Off",
    "paused": "Paused",
    "saved": "Saved",
}


def _period_start(period: Optional[str]) -> Optional[datetime]:
    """Convert period string to a UTC-aware start datetime."""
    if not period or period not in VALID_PERIODS:
        return None
    now = datetime.now(timezone.utc)
    if period == "24h":
        return now - timedelta(hours=24)
    elif period == "7d":
        return now - timedelta(days=7)
    elif period == "30d":
        return now - timedelta(days=30)
    return None


# ─── GET /overview ────────────────────────────────────────────────────────────

@router.get("/overview", response_model=HyperVOverview)
async def get_overview(
    period: Optional[str] = Query(None, regex="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Overview summary: hosts, VMs, alerts, aggregate health score."""
    total_hosts = db.query(func.count(HyperVHost.id)).scalar() or 0
    total_vms = db.query(func.count(HyperVVM.id)).scalar() or 0
    running_vms = (
        db.query(func.count(HyperVVM.id))
        .filter(HyperVVM.state == "Running")
        .scalar()
        or 0
    )
    # Active alerts = active FinOps recommendations as proxy
    active_alerts = (
        db.query(func.count(HyperVFinOpsRecommendation.id))
        .filter(HyperVFinOpsRecommendation.status == "active")
        .scalar()
        or 0
    )
    # Aggregate health score: average across all hosts
    avg_health = db.query(func.avg(HyperVHost.health_score)).scalar() or 0.0

    return HyperVOverview(
        total_hosts=total_hosts,
        total_vms=total_vms,
        running_vms=running_vms,
        active_alerts=active_alerts,
        health_score=round(float(avg_health), 1),
        timestamp=datetime.now(timezone.utc),
    )


# ─── GET /hosts ───────────────────────────────────────────────────────────────

@router.get("/hosts", response_model=List[HyperVHostResponse])
async def get_hosts(
    host: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List Hyper-V hosts with metrics and health scores."""
    query = db.query(HyperVHost)
    if host:
        query = query.filter(HyperVHost.hostname == host)
    hosts = query.all()

    results = []
    for h in hosts:
        vm_ratio = (h.running_vm_count / h.vm_count) if h.vm_count and h.vm_count > 0 else 0.0
        score = compute_health_score(
            cpu_percent=h.cpu_percent or 0.0,
            memory_percent=h.memory_percent or 0.0,
            storage_percent=h.storage_percent or 0.0,
            vm_ratio=vm_ratio,
            alert_count=0,
        )
        results.append(
            HyperVHostResponse(
                id=h.id,
                hostname=h.hostname,
                ip_address=h.ip_address,
                status=h.status or "unknown",
                total_cpus=h.total_cpus,
                total_memory_gb=h.total_memory_gb,
                total_storage_gb=h.total_storage_gb,
                cpu_percent=h.cpu_percent,
                memory_percent=h.memory_percent,
                storage_percent=h.storage_percent,
                wmi_latency_ms=h.wmi_latency_ms,
                vm_count=h.vm_count or 0,
                health_score=round(score, 1),
                manufacturer=h.manufacturer,
                model=h.model,
                serial_number=h.serial_number,
                bios_version=h.bios_version,
                os_version=h.os_version,
                processor_name=h.processor_name,
                processor_sockets=h.processor_sockets,
                cores_per_socket=h.cores_per_socket,
            )
        )
    return results


# ─── GET /hosts/{host_id}/vms ─────────────────────────────────────────────────

@router.get("/hosts/{host_id}/vms", response_model=List[HyperVVMResponse])
async def get_host_vms(
    host_id: UUID,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """VMs for a specific host. Returns 404 if host not found."""
    host = db.query(HyperVHost).filter(HyperVHost.id == host_id).first()
    if not host:
        raise HTTPException(status_code=404, detail={"error": "Host not found", "host_id": str(host_id)})

    query = db.query(HyperVVM).filter(HyperVVM.host_id == host_id)
    if status and status in VALID_STATUSES:
        db_state = STATE_MAP.get(status, status)
        query = query.filter(HyperVVM.state == db_state)

    vms = query.all()
    return [
        HyperVVMResponse(
            id=v.id,
            host_id=v.host_id,
            host_name=host.hostname,
            name=v.name,
            state=v.state,
            vcpus=v.vcpus,
            memory_mb=v.memory_mb,
            memory_demand_mb=v.memory_demand_mb,
            disk_bytes=v.disk_bytes,
            disk_max_bytes=v.disk_max_bytes,
            cpu_percent=v.cpu_percent,
            memory_percent=v.memory_percent,
            uptime_seconds=v.uptime_seconds,
        )
        for v in vms
    ]


# ─── GET /vms ─────────────────────────────────────────────────────────────────

@router.get("/vms", response_model=List[HyperVVMResponse])
async def get_all_vms(
    host: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """All VMs across all hosts, with optional host/status filters."""
    query = db.query(HyperVVM).join(HyperVHost, HyperVVM.host_id == HyperVHost.id)
    if host:
        query = query.filter(HyperVHost.hostname == host)
    if status and status in VALID_STATUSES:
        db_state = STATE_MAP.get(status, status)
        query = query.filter(HyperVVM.state == db_state)

    vms = query.all()
    # Build host name cache
    host_ids = list({v.host_id for v in vms})
    hosts_map = {}
    if host_ids:
        for h in db.query(HyperVHost).filter(HyperVHost.id.in_(host_ids)).all():
            hosts_map[h.id] = h.hostname

    return [
        HyperVVMResponse(
            id=v.id,
            host_id=v.host_id,
            host_name=hosts_map.get(v.host_id),
            name=v.name,
            state=v.state,
            vcpus=v.vcpus,
            memory_mb=v.memory_mb,
            memory_demand_mb=v.memory_demand_mb,
            disk_bytes=v.disk_bytes,
            disk_max_bytes=v.disk_max_bytes,
            cpu_percent=v.cpu_percent,
            memory_percent=v.memory_percent,
            uptime_seconds=v.uptime_seconds,
        )
        for v in vms
    ]


# ─── GET /finops/recommendations ──────────────────────────────────────────────

@router.get("/finops/recommendations", response_model=List[FinOpsRecommendation])
async def get_finops_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """FinOps analysis results."""
    recs = (
        db.query(HyperVFinOpsRecommendation)
        .filter(HyperVFinOpsRecommendation.status == "active")
        .all()
    )

    # Build name caches
    vm_ids = [r.vm_id for r in recs if r.vm_id]
    host_ids = [r.host_id for r in recs if r.host_id]
    vm_map = {}
    host_map = {}
    if vm_ids:
        for v in db.query(HyperVVM).filter(HyperVVM.id.in_(vm_ids)).all():
            vm_map[v.id] = v.name
    if host_ids:
        for h in db.query(HyperVHost).filter(HyperVHost.id.in_(host_ids)).all():
            host_map[h.id] = h.hostname

    return [
        FinOpsRecommendation(
            id=r.id,
            vm_name=vm_map.get(r.vm_id, ""),
            host_name=host_map.get(r.host_id, ""),
            category=r.category,
            description=r.description,
            suggested_action=r.suggested_action,
            estimated_savings=r.estimated_savings,
            confidence=r.confidence,
            status=r.status,
        )
        for r in recs
    ]


# ─── GET /heatmap ─────────────────────────────────────────────────────────────

@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    period: Optional[str] = Query("24h", regex="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Heatmap time-series grid of utilization values per host."""
    start = _period_start(period)

    query = db.query(HyperVMetric).filter(HyperVMetric.vm_id.is_(None))
    if start:
        query = query.filter(HyperVMetric.timestamp >= start)
    query = query.order_by(HyperVMetric.timestamp)
    metrics = query.all()

    # Build host name cache
    host_ids = list({m.host_id for m in metrics})
    host_map = {}
    if host_ids:
        for h in db.query(HyperVHost).filter(HyperVHost.id.in_(host_ids)).all():
            host_map[h.id] = h.hostname

    # Group metrics by (host_id, timestamp) to build cells
    cells_dict = {}
    timestamps_set = set()
    for m in metrics:
        key = (m.host_id, m.timestamp)
        if key not in cells_dict:
            cells_dict[key] = {"cpu_percent": 0.0, "memory_percent": 0.0}
        if m.metric_type == "cpu":
            cells_dict[key]["cpu_percent"] = m.value
        elif m.metric_type == "memory":
            cells_dict[key]["memory_percent"] = m.value
        timestamps_set.add(m.timestamp)

    data = [
        HeatmapCell(
            host_id=hid,
            hostname=host_map.get(hid, ""),
            timestamp=ts,
            cpu_percent=vals["cpu_percent"],
            memory_percent=vals["memory_percent"],
        )
        for (hid, ts), vals in cells_dict.items()
    ]

    return HeatmapResponse(
        hosts=list(host_map.values()),
        timestamps=sorted(timestamps_set),
        data=data,
    )


# ─── GET /ai/suggestions ─────────────────────────────────────────────────────

@router.get("/ai/suggestions", response_model=List[AISuggestion])
async def get_ai_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """AI optimization suggestions based on current metrics."""
    # Generate suggestions from active recommendations with confidence scores
    recs = (
        db.query(HyperVFinOpsRecommendation)
        .filter(
            HyperVFinOpsRecommendation.status == "active",
            HyperVFinOpsRecommendation.confidence.isnot(None),
        )
        .all()
    )

    # Build name caches
    vm_ids = [r.vm_id for r in recs if r.vm_id]
    host_ids = [r.host_id for r in recs if r.host_id]
    vm_map = {}
    host_map = {}
    if vm_ids:
        for v in db.query(HyperVVM).filter(HyperVVM.id.in_(vm_ids)).all():
            vm_map[v.id] = v.name
    if host_ids:
        for h in db.query(HyperVHost).filter(HyperVHost.id.in_(host_ids)).all():
            host_map[h.id] = h.hostname

    # Map FinOps categories to AI suggestion categories
    category_map = {
        "rebalance": "migrar VM para host menos carregado",
        "right-size": "reduzir recursos (CPU/RAM)",
        "scale-up": "aumentar recursos (CPU/RAM)",
    }

    suggestions = []
    for r in recs:
        vm_name = vm_map.get(r.vm_id, "")
        host_name = host_map.get(r.host_id)
        suggestions.append(
            AISuggestion(
                category=category_map.get(r.category, r.category),
                description=r.description,
                affected_vms=[vm_name] if vm_name else [],
                target_host=host_name,
                confidence=r.confidence or 0.0,
            )
        )
    return suggestions


# ─── POST /ingest (probe → API) ──────────────────────────────────────────────

from pydantic import BaseModel
from typing import Any


class HyperVIngestVM(BaseModel):
    name: str
    state: str
    vcpus: Optional[int] = 0
    memory_mb: Optional[int] = 0
    memory_demand_mb: Optional[int] = 0
    cpu_percent: Optional[float] = 0
    memory_percent: Optional[float] = 0
    disk_bytes: Optional[float] = 0
    disk_max_bytes: Optional[float] = 0
    uptime_seconds: Optional[float] = 0


class HyperVIngestHost(BaseModel):
    total_cpus: int = 0
    total_memory_gb: float = 0
    total_storage_gb: float = 0
    cpu_percent: float = 0
    memory_percent: float = 0
    storage_percent: float = 0
    vm_count: int = 0
    running_vm_count: int = 0
    wmi_latency_ms: float = 0
    status: str = "unknown"
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    bios_version: Optional[str] = None
    os_version: Optional[str] = None
    processor_name: Optional[str] = None
    processor_sockets: Optional[int] = None
    cores_per_socket: Optional[int] = None


class HyperVIngestPayload(BaseModel):
    hostname: str
    ip: str
    host: HyperVIngestHost
    vms: List[HyperVIngestVM] = []


@router.post("/ingest")
async def ingest_hyperv_data(
    payload: HyperVIngestPayload,
    probe_token: str = Query(...),
    db: Session = Depends(get_db),
):
    """Receive Hyper-V data from probe and upsert into DB."""
    from models import Probe
    probe = db.query(Probe).filter(Probe.token == probe_token).first()
    if not probe:
        raise HTTPException(status_code=401, detail="Invalid probe token")

    logger.info(
        f"HyperV ingest: {payload.hostname} | status={payload.host.status} "
        f"cpu={payload.host.cpu_percent} mem={payload.host.memory_percent} "
        f"storage={payload.host.storage_percent} vms={payload.host.vm_count} "
        f"running={payload.host.running_vm_count} | {len(payload.vms)} VM records"
    )

    now = datetime.now(timezone.utc)
    h = payload.host

    # Upsert host
    host = db.query(HyperVHost).filter(HyperVHost.hostname == payload.hostname).first()
    if not host:
        host = HyperVHost(
            hostname=payload.hostname,
            ip_address=payload.ip,
            total_cpus=h.total_cpus,
            total_memory_gb=h.total_memory_gb,
            total_storage_gb=h.total_storage_gb,
        )
        db.add(host)
        db.flush()

    host.cpu_percent = h.cpu_percent
    host.memory_percent = h.memory_percent
    host.storage_percent = h.storage_percent
    host.vm_count = h.vm_count
    host.running_vm_count = h.running_vm_count
    host.wmi_latency_ms = h.wmi_latency_ms
    host.status = h.status
    host.last_seen = now
    host.total_cpus = h.total_cpus or host.total_cpus
    host.total_memory_gb = h.total_memory_gb or host.total_memory_gb
    host.total_storage_gb = h.total_storage_gb or host.total_storage_gb
    if h.manufacturer: host.manufacturer = h.manufacturer
    if h.model: host.model = h.model
    if h.serial_number: host.serial_number = h.serial_number
    if h.bios_version: host.bios_version = h.bios_version
    if h.os_version: host.os_version = h.os_version
    if h.processor_name: host.processor_name = h.processor_name
    if h.processor_sockets: host.processor_sockets = h.processor_sockets
    if h.cores_per_socket: host.cores_per_socket = h.cores_per_socket

    # Compute health score
    vm_ratio = (h.running_vm_count / h.vm_count) if h.vm_count > 0 else 0.0
    host.health_score = compute_health_score(
        h.cpu_percent, h.memory_percent, h.storage_percent, vm_ratio, 0
    )

    # Store host-level metrics
    for mt, val in [("cpu", h.cpu_percent), ("memory", h.memory_percent), ("storage", h.storage_percent)]:
        db.add(HyperVMetric(host_id=host.id, metric_type=mt, value=val, timestamp=now))

    # Upsert VMs
    for vm_data in payload.vms:
        vm = db.query(HyperVVM).filter(
            HyperVVM.host_id == host.id, HyperVVM.name == vm_data.name
        ).first()
        if not vm:
            vm = HyperVVM(host_id=host.id, name=vm_data.name, state=vm_data.state)
            db.add(vm)
            db.flush()
        vm.state = vm_data.state
        vm.vcpus = vm_data.vcpus
        vm.memory_mb = vm_data.memory_mb
        vm.memory_demand_mb = vm_data.memory_demand_mb
        vm.cpu_percent = vm_data.cpu_percent
        vm.memory_percent = vm_data.memory_percent
        vm.disk_bytes = vm_data.disk_bytes
        vm.disk_max_bytes = vm_data.disk_max_bytes
        vm.uptime_seconds = vm_data.uptime_seconds
        vm.last_updated = now

    db.commit()

    # ── Auto-generate FinOps recommendations & AI suggestions ──
    _generate_finops_recommendations(db, host, payload.vms)

    return {"status": "ok", "hostname": payload.hostname, "vms": len(payload.vms)}


def _generate_finops_recommendations(db: Session, host, vms_data):
    """Generate FinOps recommendations based on current VM metrics.
    Custos lidos da tabela hyperv_cost_config (editáveis via API).
    Fallback para valores padrão Techbiz se tabela não existir.
    """
    from routers.hyperv_cost_config import get_cost_map
    cost_map = get_cost_map(db)
    COST_VCPU = cost_map.get("cost_vcpu", 19.70)
    COST_RAM_GB = cost_map.get("cost_ram_gb", 12.31)
    COST_DISK_GB = cost_map.get("cost_disk_gb", 0.45)

    try:
        db.query(HyperVFinOpsRecommendation).filter(
            HyperVFinOpsRecommendation.host_id == host.id,
            HyperVFinOpsRecommendation.status == "active",
        ).delete()

        vms = db.query(HyperVVM).filter(HyperVVM.host_id == host.id).all()

        for vm in vms:
            vcpus = vm.vcpus or 0
            mem_gb = (vm.memory_mb or 0) / 1024
            cpu_pct = vm.cpu_percent or 0
            # Memory: use internal % (demand/assigned) for right-sizing decisions
            mem_demand_mb = vm.memory_demand_mb or 0
            mem_assigned_mb = vm.memory_mb or 1
            mem_internal_pct = (mem_demand_mb / mem_assigned_mb * 100) if mem_assigned_mb > 0 else 0

            # ── RIGHT-SIZE CPU: reduzir vCPUs se uso baixo ──
            if vm.state == "Running" and vcpus >= 8 and cpu_pct < 10:
                target_vcpus = max(4, vcpus // 2)
                freed = vcpus - target_vcpus
                savings = round(freed * COST_VCPU, 2)
                db.add(HyperVFinOpsRecommendation(
                    host_id=host.id, vm_id=vm.id,
                    category="right-size",
                    description=f"VM {vm.name}: {vcpus} vCPUs, uso {cpu_pct}% CPU",
                    suggested_action=f"Reduzir CPU de {vcpus} para {target_vcpus} vCPUs (libera {freed} vCPUs)",
                    estimated_savings=savings,
                    confidence=0.85,
                    status="active",
                ))

            # ── RIGHT-SIZE CPU: aumentar vCPUs se uso alto ──
            if vm.state == "Running" and cpu_pct > 80:
                target_vcpus = min(vcpus * 2, 64)
                added = target_vcpus - vcpus
                if added > 0:
                    db.add(HyperVFinOpsRecommendation(
                        host_id=host.id, vm_id=vm.id,
                        category="scale-up",
                        description=f"VM {vm.name}: CPU em {cpu_pct}% com {vcpus} vCPUs",
                        suggested_action=f"Aumentar CPU de {vcpus} para {target_vcpus} vCPUs (+{added})",
                        estimated_savings=0,
                        confidence=0.9,
                        status="active",
                    ))

            # ── RIGHT-SIZE RAM: reduzir se uso interno < 30% ──
            if vm.state == "Running" and mem_gb >= 16 and mem_internal_pct < 30 and mem_internal_pct > 0:
                target_gb = max(4, int(mem_gb * 0.5))
                freed_gb = mem_gb - target_gb
                savings = round(freed_gb * COST_RAM_GB, 2)
                db.add(HyperVFinOpsRecommendation(
                    host_id=host.id, vm_id=vm.id,
                    category="right-size",
                    description=f"VM {vm.name}: {mem_gb:.0f}GB RAM, uso interno {mem_internal_pct:.0f}%",
                    suggested_action=f"Reduzir RAM de {mem_gb:.0f}GB para {target_gb}GB (libera {freed_gb:.0f}GB)",
                    estimated_savings=savings,
                    confidence=0.75,
                    status="active",
                ))

            # ── RIGHT-SIZE RAM: aumentar se uso interno > 85% ──
            if vm.state == "Running" and mem_internal_pct > 85:
                target_gb = min(int(mem_gb * 1.5), 256)
                added_gb = target_gb - int(mem_gb)
                if added_gb > 0:
                    db.add(HyperVFinOpsRecommendation(
                        host_id=host.id, vm_id=vm.id,
                        category="scale-up",
                        description=f"VM {vm.name}: RAM em {mem_internal_pct:.0f}% ({mem_demand_mb // 1024}GB/{mem_gb:.0f}GB)",
                        suggested_action=f"Aumentar RAM de {mem_gb:.0f}GB para {target_gb}GB (+{added_gb}GB)",
                        estimated_savings=0,
                        confidence=0.9,
                        status="active",
                    ))

        # Host-level: rebalance if memory > 80%
        if (host.memory_percent or 0) > 80:
            db.add(HyperVFinOpsRecommendation(
                host_id=host.id, vm_id=None,
                category="rebalance",
                description=f"Host {host.hostname} com memória alta ({host.memory_percent}%)",
                suggested_action="Migrar VMs para host com mais recursos disponíveis",
                estimated_savings=0,
                confidence=0.9,
                status="active",
            ))

        db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).warning(f"FinOps generation error: {e}")
