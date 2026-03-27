"""Pydantic response schemas for Hyper-V Observability Dashboard."""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class HyperVOverview(BaseModel):
    total_hosts: int
    total_vms: int
    running_vms: int
    active_alerts: int
    health_score: float
    timestamp: datetime


class HyperVHostResponse(BaseModel):
    id: UUID
    hostname: str
    ip_address: str
    status: str
    total_cpus: Optional[int] = None
    total_memory_gb: Optional[float] = None
    total_storage_gb: Optional[float] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    storage_percent: Optional[float] = None
    wmi_latency_ms: Optional[float] = None
    vm_count: int
    health_score: float


class HyperVVMResponse(BaseModel):
    id: UUID
    host_id: UUID
    host_name: Optional[str] = None
    name: str
    state: str
    vcpus: Optional[int] = None
    memory_mb: Optional[int] = None
    memory_demand_mb: Optional[int] = None
    disk_bytes: Optional[float] = None
    disk_max_bytes: Optional[float] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    uptime_seconds: Optional[float] = None


class FinOpsRecommendation(BaseModel):
    id: UUID
    vm_name: str
    host_name: str
    category: str
    description: str
    suggested_action: str
    estimated_savings: Optional[float] = None
    confidence: Optional[float] = None
    status: str


class AISuggestion(BaseModel):
    category: str
    description: str
    affected_vms: List[str]
    target_host: Optional[str] = None
    confidence: float


class HeatmapCell(BaseModel):
    host_id: UUID
    hostname: str
    timestamp: datetime
    cpu_percent: float
    memory_percent: float


class HeatmapResponse(BaseModel):
    hosts: List[str]
    timestamps: List[datetime]
    data: List[HeatmapCell]
