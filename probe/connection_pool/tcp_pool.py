"""
TCP Connection Pool - Pool de até 10 conexões TCP por host
idle timeout 300s
"""
import logging
import socket
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

MAX_CONNECTIONS_PER_HOST = 10
IDLE_TIMEOUT_SEC = 300
CLEANUP_INTERVAL_SEC = 60


@dataclass
class TCPConnection:
    """Conexão TCP persistente gerenciada pelo pool"""
    host: str
    port: int
    sock: socket.socket

    created_at: float = field(default_factory=time.monotonic)
    last_used: float = field(default_factory=time.monotonic)
    in_use: bool = False
    error_count: int = 0

    def is_idle_expired(self) -> bool:
        return not self.in_use and (time.monotonic() - self.last_used) > IDLE_TIMEOUT_SEC

    def touch(self):
        self.last_used = time.monotonic()

    def is_alive(self) -> bool:
        """Verifica se o socket ainda está conectado"""
        try:
            self.sock.setblocking(False)
            data = self.sock.recv(1, socket.MSG_PEEK)
            self.sock.setblocking(True)
            return len(data) > 0
        except BlockingIOError:
            self.sock.setblocking(True)
            return True  # sem dados mas conexão ativa
        except Exception:
            return False

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


class TCPConnectionPool:
    """
    Pool de conexões TCP persistentes por host:port.

    Uso:
        pool = TCPConnectionPool()
        conn = pool.acquire("192.168.1.1", 80)
        try:
            conn.sock.sendall(b"GET / HTTP/1.0\\r\\n\\r\\n")
            data = conn.sock.recv(4096)
        finally:
            pool.release("192.168.1.1", 80, conn)
    """

    def __init__(self, max_per_host: int = MAX_CONNECTIONS_PER_HOST, connect_timeout: float = 5.0):
        self.max_per_host = max_per_host
        self.connect_timeout = connect_timeout
        self._pools: Dict[str, List[TCPConnection]] = {}
        self._lock = threading.Lock()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _pool_key(self, host: str, port: int) -> str:
        return f"{host}:{port}"

    def _create_connection(self, host: str, port: int) -> Optional[TCPConnection]:
        """Cria nova conexão TCP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connect_timeout)
            sock.connect((host, port))
            sock.settimeout(None)  # blocking após conectar
            conn = TCPConnection(host=host, port=port, sock=sock, in_use=True)
            logger.info(f"TCPPool: nova conexão criada para {host}:{port}")
            return conn
        except Exception as e:
            logger.warning(f"TCPPool: falha ao criar conexão para {host}:{port}: {e}")
            return None

    def acquire(self, host: str, port: int) -> Optional[TCPConnection]:
        """
        Adquire conexão do pool. Reutiliza existente ou cria nova.
        Retorna None se limite atingido ou falha na conexão.
        """
        key = self._pool_key(host, port)
        with self._lock:
            pool = self._pools.setdefault(key, [])

            # 1. Reutilizar conexão ociosa viva
            for conn in pool:
                if not conn.in_use:
                    if conn.is_alive():
                        conn.in_use = True
                        conn.touch()
                        logger.debug(f"TCPPool: reutilizando conexão para {host}:{port}")
                        return conn
                    else:
                        # Conexão morta - remover
                        conn.close()
                        pool.remove(conn)
                        break

            # 2. Criar nova se abaixo do limite
            if len(pool) < self.max_per_host:
                conn = self._create_connection(host, port)
                if conn:
                    pool.append(conn)
                    logger.info(f"TCPPool: {host}:{port} → {len(pool)}/{self.max_per_host} conexões")
                    return conn
                return None

            # 3. Limite atingido
            logger.warning(f"TCPPool: limite de {self.max_per_host} conexões atingido para {host}:{port}")
            return None

    def release(self, host: str, port: int, connection: TCPConnection):
        """Libera conexão de volta ao pool"""
        key = self._pool_key(host, port)
        with self._lock:
            for conn in self._pools.get(key, []):
                if conn is connection:
                    conn.in_use = False
                    conn.touch()
                    logger.debug(f"TCPPool: conexão liberada para {host}:{port}")
                    return

    def invalidate(self, host: str, port: int, connection: TCPConnection):
        """Remove conexão com erro do pool e fecha o socket"""
        key = self._pool_key(host, port)
        with self._lock:
            pool = self._pools.get(key, [])
            self._pools[key] = [c for c in pool if c is not connection]
            connection.close()
            logger.warning(f"TCPPool: conexão inválida removida para {host}:{port}")

    def stats(self) -> Dict[str, Dict]:
        """Retorna estatísticas do pool"""
        with self._lock:
            return {
                key: {
                    "total": len(pool),
                    "in_use": sum(1 for c in pool if c.in_use),
                    "idle": sum(1 for c in pool if not c.in_use),
                }
                for key, pool in self._pools.items()
            }

    def _cleanup_loop(self):
        while True:
            time.sleep(CLEANUP_INTERVAL_SEC)
            try:
                self._cleanup_idle()
            except Exception as e:
                logger.error(f"TCPPool cleanup error: {e}")

    def _cleanup_idle(self):
        with self._lock:
            for key, pool in list(self._pools.items()):
                before = len(pool)
                expired = [c for c in pool if c.is_idle_expired()]
                for c in expired:
                    c.close()
                self._pools[key] = [c for c in pool if not c.is_idle_expired()]
                removed = before - len(self._pools[key])
                if removed:
                    logger.info(f"TCPPool: removidas {removed} conexões ociosas de {key}")


# Singleton global
_global_pool: Optional[TCPConnectionPool] = None


def get_pool() -> TCPConnectionPool:
    global _global_pool
    if _global_pool is None:
        _global_pool = TCPConnectionPool()
    return _global_pool
