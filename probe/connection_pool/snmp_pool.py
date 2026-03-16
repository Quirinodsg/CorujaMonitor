"""
SNMP Connection Pool - Pool de até 5 conexões SNMP por host
idle timeout 300s, limpeza a cada 60s
"""
import logging
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

MAX_CONNECTIONS_PER_HOST = 5
IDLE_TIMEOUT_SEC = 300
CLEANUP_INTERVAL_SEC = 60


@dataclass
class SNMPConnection:
    """Representa uma 'conexão' SNMP (parâmetros de sessão reutilizáveis)"""
    host: str
    community: str
    port: int
    version: str
    # SNMPv3
    username: str = ""
    auth_key: str = ""
    priv_key: str = ""
    auth_protocol: str = "SHA"
    priv_protocol: str = "AES"

    created_at: float = field(default_factory=time.monotonic)
    last_used: float = field(default_factory=time.monotonic)
    in_use: bool = False
    error_count: int = 0

    def is_idle_expired(self) -> bool:
        return not self.in_use and (time.monotonic() - self.last_used) > IDLE_TIMEOUT_SEC

    def touch(self):
        self.last_used = time.monotonic()

    def matches(self, community: str, port: int, version: str,
                username: str = "", auth_key: str = "") -> bool:
        """Verifica se esta conexão pode ser reutilizada para os parâmetros dados"""
        return (
            self.community == community
            and self.port == port
            and self.version == version
            and self.username == username
            and self.auth_key == auth_key
        )


class SNMPConnectionPool:
    """
    Pool de conexões SNMP por host.

    Uso:
        pool = SNMPConnectionPool()
        conn = pool.acquire("192.168.1.1", community="public", port=161, version="2c")
        try:
            # usar conn.community, conn.port, conn.version, etc.
            engine = SNMPEngine()
            result = engine.execute(conn.host, community=conn.community, ...)
        finally:
            pool.release("192.168.1.1", conn)
    """

    def __init__(self, max_per_host: int = MAX_CONNECTIONS_PER_HOST):
        self.max_per_host = max_per_host
        self._pools: Dict[str, List[SNMPConnection]] = {}
        self._lock = threading.Lock()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def acquire(
        self,
        host: str,
        community: str = "public",
        port: int = 161,
        version: str = "2c",
        username: str = "",
        auth_key: str = "",
        priv_key: str = "",
        auth_protocol: str = "SHA",
        priv_protocol: str = "AES",
    ) -> Optional[SNMPConnection]:
        """
        Adquire conexão do pool. Reutiliza existente ou cria nova.
        Retorna None se limite atingido.
        """
        with self._lock:
            pool = self._pools.setdefault(host, [])

            # 1. Reutilizar conexão ociosa compatível
            for conn in pool:
                if not conn.in_use and conn.matches(community, port, version, username, auth_key):
                    conn.in_use = True
                    conn.touch()
                    logger.debug(f"SNMPPool: reutilizando conexão para {host} ({len(pool)} no pool)")
                    return conn

            # 2. Criar nova se abaixo do limite
            if len(pool) < self.max_per_host:
                conn = SNMPConnection(
                    host=host,
                    community=community,
                    port=port,
                    version=version,
                    username=username,
                    auth_key=auth_key,
                    priv_key=priv_key,
                    auth_protocol=auth_protocol,
                    priv_protocol=priv_protocol,
                    in_use=True,
                )
                pool.append(conn)
                logger.info(f"SNMPPool: {host} → {len(pool)}/{self.max_per_host} conexões")
                return conn

            # 3. Limite atingido
            logger.warning(f"SNMPPool: limite de {self.max_per_host} conexões atingido para {host}")
            return None

    def release(self, host: str, connection: SNMPConnection):
        """Libera conexão de volta ao pool"""
        with self._lock:
            for conn in self._pools.get(host, []):
                if conn is connection:
                    conn.in_use = False
                    conn.touch()
                    logger.debug(f"SNMPPool: conexão liberada para {host}")
                    return

    def invalidate(self, host: str, connection: SNMPConnection):
        """Remove conexão com erro do pool"""
        with self._lock:
            pool = self._pools.get(host, [])
            self._pools[host] = [c for c in pool if c is not connection]
            logger.warning(f"SNMPPool: conexão inválida removida para {host}")

    def stats(self) -> Dict[str, Dict]:
        """Retorna estatísticas do pool"""
        with self._lock:
            return {
                host: {
                    "total": len(pool),
                    "in_use": sum(1 for c in pool if c.in_use),
                    "idle": sum(1 for c in pool if not c.in_use),
                }
                for host, pool in self._pools.items()
            }

    def _cleanup_loop(self):
        while True:
            time.sleep(CLEANUP_INTERVAL_SEC)
            try:
                self._cleanup_idle()
            except Exception as e:
                logger.error(f"SNMPPool cleanup error: {e}")

    def _cleanup_idle(self):
        with self._lock:
            for host, pool in list(self._pools.items()):
                before = len(pool)
                self._pools[host] = [c for c in pool if not c.is_idle_expired()]
                removed = before - len(self._pools[host])
                if removed:
                    logger.info(f"SNMPPool: removidas {removed} conexões ociosas de {host}")


# Singleton global
_global_pool: Optional[SNMPConnectionPool] = None


def get_pool() -> SNMPConnectionPool:
    global _global_pool
    if _global_pool is None:
        _global_pool = SNMPConnectionPool()
    return _global_pool
