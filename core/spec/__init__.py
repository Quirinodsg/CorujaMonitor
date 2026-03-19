"""
core/spec — Spec Central do Coruja Monitor v3.0
Fonte única da verdade para todos os tipos de dados do sistema.
"""
from .enums import (
    HostType,
    Protocol,
    SensorStatus,
    EventSeverity,
    AlertStatus,
    NodeType,
    ProbeStatus,
)
from .models import (
    Host,
    Sensor,
    Metric,
    Event,
    Alert,
    TopologyNode,
    ProbeNode,
)

__all__ = [
    # enums
    "HostType", "Protocol", "SensorStatus", "EventSeverity",
    "AlertStatus", "NodeType", "ProbeStatus",
    # models
    "Host", "Sensor", "Metric", "Event", "Alert", "TopologyNode", "ProbeNode",
]
