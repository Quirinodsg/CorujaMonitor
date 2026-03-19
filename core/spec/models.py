"""
Modelos Pydantic globais do Coruja Monitor v3.0.
Fonte única da verdade — todos os módulos importam daqui.
"""
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

from .enums import (
    HostType,
    Protocol,
    SensorStatus,
    EventSeverity,
    AlertStatus,
    NodeType,
    ProbeStatus,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Host(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    hostname: str
    ip_address: str
    type: HostType
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utcnow)

    model_config = {"use_enum_values": True}


class Sensor(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    host_id: UUID
    type: str
    protocol: Protocol
    interval: int          # segundos
    timeout: int = 30      # segundos
    retries: int = 3
    query: Optional[str] = None
    thresholds: dict = Field(default_factory=dict)  # {"warning": 80, "critical": 95}

    model_config = {"use_enum_values": True}


class Metric(BaseModel):
    sensor_id: UUID
    host_id: UUID
    value: float
    unit: str
    timestamp: datetime
    status: SensorStatus = SensorStatus.UNKNOWN

    model_config = {"use_enum_values": True}


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    host_id: UUID
    type: str
    severity: EventSeverity
    timestamp: datetime
    source_metric_id: Optional[UUID] = None
    description: str = ""

    model_config = {"use_enum_values": True}


class Alert(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_ids: list[UUID] = Field(default_factory=list)
    title: str
    severity: EventSeverity
    status: AlertStatus = AlertStatus.OPEN
    root_cause: Optional[str] = None
    affected_hosts: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utcnow)

    model_config = {"use_enum_values": True}


class TopologyNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: NodeType
    parent_id: Optional[UUID] = None
    children_ids: list[UUID] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class ProbeNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    location: str
    status: ProbeStatus = ProbeStatus.OFFLINE
    capacity: int          # máximo de hosts
    assigned_hosts: list[UUID] = Field(default_factory=list)

    model_config = {"use_enum_values": True}
