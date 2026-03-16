"""
WMI Connection Pool - Gerencia conexões WMI reutilizáveis por host
Evita sobrecarga do wmiprvse.exe criando conexões desnecessárias.

Limites:
  max_connections_per_host: 3
  connection_timeout: 30s
  idle_timeout: 300s (5 min)
"""
import logging
import time
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Thread-local storage para rastrear se CoInitializeSecurity já foi chamado nesta thread
_thread_local = threading.local()

MAX_CONNECTIONS_PER_HOST = 3
CONNECTION_TIMEOUT_SEC = 30
IDLE_TIMEOUT_SEC = 300  # Fecha conexão ociosa após 5 minutos


def _init_thread_com():
    """
    Inicializa COM e CoInitializeSecurity para a thread atual.
    Deve ser chamado em CADA thread que usa WMI.
    CoInitializeSecurity só pode ser chamado UMA VEZ por processo,
    mas CoInitialize deve ser chamado por thread.
    """
    try:
        import pythoncom

        # CoInitialize por thread (obrigatório)
        pythoncom.CoInitialize()

        # CoInitializeSecurity: apenas uma vez por processo
        if not getattr(_thread_local, 'com_security_initialized', False):
            try:
                pythoncom.CoInitializeSecurity(
                    None,
                    -1,
                    None,
                    None,
                    pythoncom.RPC_C_AUTHN_LEVEL_DEFAULT,
                    pythoncom.RPC_C_IMP_LEVEL_IMPERSONATE,
                    None,
                    pythoncom.EOAC_NONE,
                    None,
                )
                _thread_local.com_security_initialized = True
                logger.info("✅ CoInitializeSecurity configurado com sucesso (thread: %s)", threading.current_thread().name)
            except Exception as e:
                # RPC_E_TOO_LATE (0x80010119) = já foi chamado neste processo, tudo bem
                _thread_local.com_security_initialized = True
                logger.debug(f"CoInitializeSecurity já configurado: {e}")

    except Exception as e:
        logger.warning(f"Erro ao inicializar COM: {e}")


@dataclass
class PooledConnection:
    host: str
    connection: object  # wmi.WMI instance
    created_at: float = field(default_factory=time.monotonic)
    last_used: float = field(default_factory=time.monotonic)
    in_use: bool = False
    error_count: int = 0

    def is_idle_expired(self) -> bool:
        return not self.in_use and (time.monotonic() - self.last_used) > IDLE_TIMEOUT_SEC

    def touch(self):
        self.last_used = time.monotonic()


class WMIConnectionPool:
    """
    Pool de conexões WMI por host.

    Uso:
        pool = WMIConnectionPool()
        conn = pool.acquire("SRVHVSPRD010.ad.techbiz.com.br", username, password, domain)
        try:
            engine = WMIEngine(conn)
            metrics = engine.collect_all()
        finally:
            pool.release("SRVHVSPRD010.ad.techbiz.com.br", conn)
    """

    def __init__(self, max_per_host: int = MAX_CONNECTIONS_PER_HOST):
        self.max_per_host = max_per_host
        self._pools: Dict[str, List[PooledConnection]] = {}
        self._lock = threading.Lock()
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _create_connection(self, host: str, username: str, password: str, domain: str) -> Optional[object]:
        """
        Cria nova conexão WMI.

        Estratégia:
        1. Tenta sem credenciais (usa identidade do serviço via Kerberos - mais confiável)
        2. Fallback com credenciais explícitas (para workgroup ou quando necessário)
        """
        try:
            import wmi

            # CRÍTICO: inicializar COM + CoInitializeSecurity para esta thread
            _init_thread_com()

            full_user = f"{domain}\\{username}" if domain and "\\" not in username else username
            logger.info(f"🔌 WMI Pool: criando conexão para {host} ({full_user})")

            # Tentativa 1: sem credenciais explícitas
            # Quando o serviço roda como coruja.monitor no domínio, o Kerberos
            # usa automaticamente a identidade do serviço - igual ao PRTG
            try:
                conn = wmi.WMI(
                    computer=host,
                    namespace="root/cimv2",
                )
                logger.info(f"✅ WMI Pool: conexão criada para {host} (identidade do serviço)")
                return conn
            except Exception as e1:
                logger.debug(f"WMI sem credenciais falhou para {host}: {e1} — tentando com credenciais explícitas")

            # Tentativa 2: com credenciais explícitas (fallback)
            conn = wmi.WMI(
                computer=host,
                user=full_user,
                password=password,
                namespace="root/cimv2",
            )
            logger.info(f"✅ WMI Pool: conexão criada para {host} (credenciais explícitas)")
            return conn

        except Exception as e:
            logger.error(f"❌ WMI Pool: falha ao criar conexão para {host}: {e}")
            return None

    def acquire(self, host: str, username: str, password: str, domain: str = "") -> Optional[object]:
        """
        Adquire conexão do pool. Reutiliza existente ou cria nova.
        Retorna None se limite atingido ou falha na conexão.
        """
        with self._lock:
            pool = self._pools.setdefault(host, [])

            # 1. Tentar reutilizar conexão ociosa
            for pc in pool:
                if not pc.in_use:
                    pc.in_use = True
                    pc.touch()
                    logger.debug(f"WMI Pool: reutilizando conexão para {host} ({len(pool)} no pool)")
                    return pc.connection

            # 2. Criar nova se abaixo do limite
            if len(pool) < self.max_per_host:
                conn = self._create_connection(host, username, password, domain)
                if conn:
                    pc = PooledConnection(host=host, connection=conn, in_use=True)
                    pool.append(pc)
                    logger.info(f"WMI Pool: {host} → {len(pool)}/{self.max_per_host} conexões")
                    return conn
                return None

            # 3. Limite atingido
            logger.warning(f"WMI Pool: limite de {self.max_per_host} conexões atingido para {host}")
            return None

    def release(self, host: str, connection: object):
        """Libera conexão de volta ao pool"""
        with self._lock:
            pool = self._pools.get(host, [])
            for pc in pool:
                if pc.connection is connection:
                    pc.in_use = False
                    pc.touch()
                    logger.debug(f"WMI Pool: conexão liberada para {host}")
                    return

    def invalidate(self, host: str, connection: object):
        """Remove conexão com erro do pool"""
        with self._lock:
            pool = self._pools.get(host, [])
            self._pools[host] = [pc for pc in pool if pc.connection is not connection]
            logger.warning(f"WMI Pool: conexão inválida removida para {host}")

    def _cleanup_loop(self):
        """Remove conexões ociosas expiradas periodicamente"""
        while True:
            time.sleep(60)
            try:
                self._cleanup_idle()
            except Exception as e:
                logger.error(f"WMI Pool cleanup error: {e}")

    def _cleanup_idle(self):
        with self._lock:
            for host, pool in list(self._pools.items()):
                before = len(pool)
                self._pools[host] = [pc for pc in pool if not pc.is_idle_expired()]
                removed = before - len(self._pools[host])
                if removed:
                    logger.info(f"WMI Pool: removidas {removed} conexões ociosas de {host}")

    # Alias público conforme especificação
    def cleanup_idle_connections(self):
        """Alias público para _cleanup_idle — remove conexões ociosas expiradas."""
        self._cleanup_idle()

    def stats(self) -> Dict[str, Dict]:
        """Retorna estatísticas do pool"""
        with self._lock:
            return {
                host: {
                    "total": len(pool),
                    "in_use": sum(1 for pc in pool if pc.in_use),
                    "idle": sum(1 for pc in pool if not pc.in_use),
                }
                for host, pool in self._pools.items()
            }


# Instância global do pool (singleton)
_global_pool: Optional[WMIConnectionPool] = None


def get_pool() -> WMIConnectionPool:
    global _global_pool
    if _global_pool is None:
        _global_pool = WMIConnectionPool()
    return _global_pool
