"""
Global Rate Limiter — proteção contra excesso de sensores simultâneos.

MAX_GLOBAL_SENSORS_RUNNING = 200
QUEUE_LIMIT = 1000

Métricas expostas:
  global_active_sensors
  global_queue_depth
"""
import logging
import threading
import time
from collections import deque
from typing import Callable, Optional

logger = logging.getLogger(__name__)

MAX_GLOBAL_SENSORS_RUNNING = 200
QUEUE_LIMIT = 1000
_SLOT_WAIT_TIMEOUT = 30  # segundos máximos aguardando slot


class GlobalRateLimiter:
    """
    Semáforo global que limita sensores em execução simultânea.

    Uso (context manager):
        limiter = get_limiter()
        with limiter.acquire_slot(sensor_id="cpu_host1"):
            # executar coleta
    """

    def __init__(
        self,
        max_running: int = MAX_GLOBAL_SENSORS_RUNNING,
        queue_limit: int = QUEUE_LIMIT,
    ):
        self.max_running = max_running
        self.queue_limit = queue_limit
        self._semaphore = threading.Semaphore(max_running)
        self._active = 0
        self._queued = 0
        self._lock = threading.Lock()
        self._total_executed = 0
        self._total_rejected = 0

    def acquire_slot(self, sensor_id: str = "", timeout: float = _SLOT_WAIT_TIMEOUT):
        """Context manager que adquire um slot de execução."""
        return _RateLimitSlot(self, sensor_id, timeout)

    def _acquire(self, sensor_id: str, timeout: float) -> bool:
        with self._lock:
            if self._queued >= self.queue_limit:
                self._total_rejected += 1
                logger.warning(
                    f"RateLimiter: fila cheia ({self.queue_limit}), sensor {sensor_id} rejeitado"
                )
                return False
            self._queued += 1

        acquired = self._semaphore.acquire(timeout=timeout)

        with self._lock:
            self._queued -= 1
            if acquired:
                self._active += 1
                self._total_executed += 1
                logger.debug(
                    f"RateLimiter: slot adquirido para {sensor_id} "
                    f"({self._active}/{self.max_running} ativos)"
                )
            else:
                self._total_rejected += 1
                logger.warning(
                    f"RateLimiter: timeout aguardando slot para {sensor_id}"
                )
        return acquired

    def _release(self, sensor_id: str):
        with self._lock:
            self._active = max(0, self._active - 1)
        self._semaphore.release()
        logger.debug(f"RateLimiter: slot liberado para {sensor_id} ({self._active} ativos)")

    @property
    def global_active_sensors(self) -> int:
        with self._lock:
            return self._active

    @property
    def global_queue_depth(self) -> int:
        with self._lock:
            return self._queued

    def metrics(self) -> dict:
        with self._lock:
            return {
                "global_active_sensors": self._active,
                "global_queue_depth": self._queued,
                "max_running": self.max_running,
                "queue_limit": self.queue_limit,
                "total_executed": self._total_executed,
                "total_rejected": self._total_rejected,
                "utilization_pct": round(self._active / self.max_running * 100, 1),
            }

    def resize(self, new_max: int):
        """Ajusta limite em runtime (sem reiniciar)."""
        diff = new_max - self.max_running
        if diff > 0:
            for _ in range(diff):
                self._semaphore.release()
        self.max_running = new_max
        logger.info(f"RateLimiter: max_running ajustado para {new_max}")


class _RateLimitSlot:
    """Context manager retornado por acquire_slot()."""

    def __init__(self, limiter: GlobalRateLimiter, sensor_id: str, timeout: float):
        self._limiter = limiter
        self._sensor_id = sensor_id
        self._timeout = timeout
        self._acquired = False

    def __enter__(self):
        self._acquired = self._limiter._acquire(self._sensor_id, self._timeout)
        if not self._acquired:
            raise RuntimeError(
                f"RateLimiter: não foi possível adquirir slot para {self._sensor_id}"
            )
        return self

    def __exit__(self, *_):
        if self._acquired:
            self._limiter._release(self._sensor_id)


# ── Singleton global ──────────────────────────────────────────────────────────

_global_limiter: Optional[GlobalRateLimiter] = None
_limiter_lock = threading.Lock()


def get_limiter() -> GlobalRateLimiter:
    global _global_limiter
    if _global_limiter is None:
        with _limiter_lock:
            if _global_limiter is None:
                _global_limiter = GlobalRateLimiter()
                logger.info(
                    f"GlobalRateLimiter iniciado: max={MAX_GLOBAL_SENSORS_RUNNING}, "
                    f"queue={QUEUE_LIMIT}"
                )
    return _global_limiter
