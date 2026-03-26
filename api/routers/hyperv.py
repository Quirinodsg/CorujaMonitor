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
                cpu_percent=h.cpu_percent,
                memory_percent=h.memory_percent,
                storage_percent=h.storage_percent,
                wmi_latency_ms=h.wmi_latency_ms,
                vm_count=h.vm_count or 0,
                health_score=round(score, 1),
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
            disk_bytes=v.disk_bytes,
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
            disk_bytes=v.disk_bytes,
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
        "rebalance": "move VM to less loaded host",
        "idle": "shutdown idle VM",
        "overprovisioned": "balance cluster workload",
        "right-size": "balance cluster workload",
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
