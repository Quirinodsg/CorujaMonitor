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

# Backoff para evitar lockout de conta AD
# Após falha de autenticação, aguarda antes de tentar novamente
AUTH_FAILURE_BACKOFF_SEC = 600   # 10 minutos após falha de auth (Access Denied)
MAX_AUTH_FAILURES = 3            # Após 3 falhas, backoff aumenta para 30 min
AUTH_FAILURE_EXTENDED_SEC = 1800 # 30 minutos após muitas falhas


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
        conn = pool.acquire("SERVER01.ad.empresaxpto.com.br", username, password, domain)
        try:
            engine = WMIEngine(conn)
            metrics = engine.collect_all()
        finally:
            pool.release("SERVER01.ad.empresaxpto.com.br", conn)
    """

    def __init__(self, max_per_host: int = MAX_CONNECTIONS_PER_HOST):
        self.max_per_host = max_per_host
        self._pools: Dict[str, List[PooledConnection]] = {}
        self._lock = threading.Lock()
        # Rastreia falhas de autenticação por host para evitar lockout AD
        # {host: {'count': int, 'last_failure': float}}
        self._auth_failures: Dict[str, Dict] = {}
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _is_in_backoff(self, host: str) -> bool:
        """Verifica se o host está em período de backoff por falha de autenticação."""
        failure_info = self._auth_failures.get(host)
        if not failure_info:
            return False
        count = failure_info.get('count', 0)
        last_failure = failure_info.get('last_failure', 0)
        backoff = AUTH_FAILURE_EXTENDED_SEC if count >= MAX_AUTH_FAILURES else AUTH_FAILURE_BACKOFF_SEC
        elapsed = time.monotonic() - last_failure
        if elapsed < backoff:
            remaining = int(backoff - elapsed)
            logger.warning(
                f"⏳ WMI Pool: {host} em backoff por falha de auth "
                f"({count} falhas, aguardando {remaining}s para evitar lockout AD)"
            )
            return True
        return False

    def _record_auth_failure(self, host: str):
        """Registra falha de autenticação para controle de backoff."""
        if host not in self._auth_failures:
            self._auth_failures[host] = {'count': 0, 'last_failure': 0}
        self._auth_failures[host]['count'] += 1
        self._auth_failures[host]['last_failure'] = time.monotonic()
        count = self._auth_failures[host]['count']
        logger.error(
            f"🔒 WMI Pool: falha de auth registrada para {host} "
            f"(total: {count}) — backoff ativado para evitar lockout AD"
        )

    def _clear_auth_failure(self, host: str):
        """Limpa registro de falha após conexão bem-sucedida."""
        if host in self._auth_failures:
            del self._auth_failures[host]

    def _create_connection(self, host: str, username: str, password: str, domain: str) -> Optional[object]:
        """
        Cria nova conexão WMI com credenciais explícitas.
        Não tenta sem credenciais para evitar tentativas duplas que causam lockout AD.
        """
        try:
            import wmi

            # CRÍTICO: inicializar COM + CoInitializeSecurity para esta thread
            _init_thread_com()

            full_user = f"{domain}\\{username}" if domain and "\\" not in username else username
            logger.info(f"🔌 WMI Pool: criando conexão para {host} ({full_user})")

            conn = wmi.WMI(
                computer=host,
                user=full_user,
                password=password,
                namespace="root/cimv2",
            )
            logger.info(f"✅ WMI Pool: conexão criada para {host}")
            return conn

        except Exception as e:
            err_str = str(e)
            # Detectar erros de autenticação (Access Denied) vs erros de rede
            if "-2147024891" in err_str or "Access is denied" in err_str or "Access denied" in err_str:
                self._record_auth_failure(host)
            else:
                logger.error(f"❌ WMI Pool: falha ao criar conexão para {host}: {e}")
            return None

    def acquire(self, host: str, username: str, password: str, domain: str = "") -> Optional[object]:
        """
        Adquire conexão do pool. Reutiliza existente ou cria nova.
        Retorna None se em backoff, limite atingido ou falha na conexão.
        """
        with self._lock:
            # Verificar backoff antes de qualquer tentativa de auth
            if self._is_in_backoff(host):
                return None

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
                    self._clear_auth_failure(host)
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
