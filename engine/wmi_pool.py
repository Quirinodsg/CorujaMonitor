# Proxy para probe/engine/wmi_pool.py
from probe.engine.wmi_pool import *
try:
    from probe.engine.wmi_pool import WMIConnectionPool, get_pool, PooledConnection, _init_thread_com
    from probe.engine.wmi_pool import MAX_CONNECTIONS_PER_HOST, IDLE_TIMEOUT_SEC
except ImportError:
    pass
