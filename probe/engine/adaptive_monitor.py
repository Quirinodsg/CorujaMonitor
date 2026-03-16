"""
Adaptive Monitor - Ajusta intervalos de coleta dinamicamente baseado no status dos sensores
warning → 60s | critical → 30s | 5x ok consecutivo → volta para 300s
"""
import logging
import threading
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)

INTERVAL_NORMAL   = 300  # segundos
INTERVAL_WARNING  = 60
INTERVAL_CRITICAL = 30
OK_CYCLES_TO_RESTORE = 5


class AdaptiveMonitor:
    def __init__(self):
        self._host_intervals: Dict[str, int] = {}
        self._ok_streak: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()

    def update(self, host: str, status: str) -> int:
        """
        Atualiza o intervalo do host baseado no status recebido.
        Retorna o novo intervalo em segundos.
        """
        with self._lock:
            current = self._host_intervals.get(host, INTERVAL_NORMAL)

            if status == "critical":
                new_interval = INTERVAL_CRITICAL
                self._ok_streak[host] = 0
            elif status == "warning":
                new_interval = INTERVAL_WARNING
                self._ok_streak[host] = 0
            elif status == "ok":
                self._ok_streak[host] += 1
                if self._ok_streak[host] >= OK_CYCLES_TO_RESTORE:
                    new_interval = INTERVAL_NORMAL
                else:
                    new_interval = current  # mantém intervalo atual até restaurar
            else:
                new_interval = current

            if new_interval != current:
                logger.info(
                    f"AdaptiveMonitor [{host}]: intervalo {current}s → {new_interval}s "
                    f"(status={status}, ok_streak={self._ok_streak[host]})"
                )
                self._host_intervals[host] = new_interval

            return new_interval

    def get_interval(self, host: str) -> int:
        with self._lock:
            return self._host_intervals.get(host, INTERVAL_NORMAL)

    def reset(self, host: str):
        with self._lock:
            self._host_intervals.pop(host, None)
            self._ok_streak.pop(host, None)

    def status(self) -> Dict:
        with self._lock:
            return {
                host: {
                    "interval": interval,
                    "ok_streak": self._ok_streak.get(host, 0),
                }
                for host, interval in self._host_intervals.items()
            }
