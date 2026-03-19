"""
Enums globais do Coruja Monitor v3.0.
Todos os módulos devem importar daqui — nunca redefinir localmente.
"""
from enum import Enum


class HostType(str, Enum):
    SERVER = "server"
    SWITCH = "switch"
    APPLIANCE = "appliance"
    CONTAINER = "container"


class Protocol(str, Enum):
    WMI = "wmi"
    SNMP = "snmp"
    ICMP = "icmp"
    TCP = "tcp"
    HTTP = "http"


class SensorStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class NodeType(str, Enum):
    SWITCH = "switch"
    SERVER = "server"
    SERVICE = "service"
    APPLICATION = "application"


class ProbeStatus(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
