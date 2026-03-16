from .snmp_pool import SNMPConnectionPool, SNMPConnection, get_pool as get_snmp_pool
from .tcp_pool import TCPConnectionPool, TCPConnection, get_pool as get_tcp_pool

# WMIConnectionPool fica em engine/wmi_pool.py (Windows-only)
# Re-exportado aqui para visibilidade na auditoria de arquitetura
try:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from engine.wmi_pool import WMIConnectionPool, get_pool as get_wmi_pool
except Exception:
    WMIConnectionPool = None
    get_wmi_pool = None

__all__ = [
    "SNMPConnectionPool", "SNMPConnection", "get_snmp_pool",
    "TCPConnectionPool", "TCPConnection", "get_tcp_pool",
    "WMIConnectionPool", "get_wmi_pool",
]
