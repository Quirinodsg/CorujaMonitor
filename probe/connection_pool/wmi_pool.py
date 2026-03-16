"""
WMI Connection Pool (connection_pool layer)
Wrapper sobre probe/engine/wmi_pool.py para manter consistência
com SNMPConnectionPool e TCPConnectionPool.

max_connections_per_host = 3
idle_timeout = 300s
cleanup_loop = 60s

Funções públicas:
  get_connection(host, credentials)   → alias de acquire()
  release_connection(connection)      → alias de release()
  cleanup_idle_connections()          → remove conexões ociosas expiradas
"""
from probe.engine.wmi_pool import (
    WMIConnectionPool,
    PooledConnection,
    get_pool,
    _init_thread_com,
    MAX_CONNECTIONS_PER_HOST,
    CONNECTION_TIMEOUT_SEC,
    IDLE_TIMEOUT_SEC,
)

__all__ = [
    "WMIConnectionPool",
    "PooledConnection",
    "get_pool",
    "_init_thread_com",
    "MAX_CONNECTIONS_PER_HOST",
    "CONNECTION_TIMEOUT_SEC",
    "IDLE_TIMEOUT_SEC",
    # Funções de conveniência
    "get_connection",
    "release_connection",
    "cleanup_idle_connections",
]


def get_connection(host: str, credentials: dict):
    """Adquire conexão WMI do pool global."""
    pool = get_pool()
    return pool.acquire(
        host,
        credentials.get("username", ""),
        credentials.get("password", ""),
        credentials.get("domain", ""),
    )


def release_connection(host: str, connection) -> None:
    """Libera conexão WMI de volta ao pool global."""
    get_pool().release(host, connection)


def cleanup_idle_connections() -> None:
    """Remove conexões ociosas expiradas do pool global."""
    get_pool().cleanup_idle_connections()
