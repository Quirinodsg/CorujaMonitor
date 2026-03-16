"""
Event Queue — buffer de eventos com deduplicação, agrupamento e rate limiting.

Funcionalidades:
  - deduplicação por (host, event_type) dentro de janela de tempo
  - agrupamento de eventos do mesmo host
  - rate limiting por host (max N eventos/minuto)
"""
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

DEDUP_WINDOW_SEC = 60       # ignora evento duplicado dentro de 60s
MAX_EVENTS_PER_HOST_MIN = 30  # rate limit: 30 eventos/min por host
QUEUE_MAX_SIZE = 10_000
FLUSH_INTERVAL_SEC = 5.0


@dataclass
class MonitoringEvent:
    host: str
    event_type: str
    severity: str
    message: str
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    @property
    def dedup_key(self) -> str:
        return f"{self.host}:{self.event_type}"


class EventQueue:
    """
    Fila de eventos com deduplicação, agrupamento e rate limiting.

    Uso:
        queue = EventQueue(on_flush=lambda events: print(events))
        queue.start()
        queue.push(MonitoringEvent(host="srv1", event_type="cpu_high", ...))
    """

    def __init__(
        self,
        on_flush: Optional[Callable[[List[MonitoringEvent]], None]] = None,
        dedup_window: float = DEDUP_WINDOW_SEC,
        rate_limit: int = MAX_EVENTS_PER_HOST_MIN,
        flush_interval: float = FLUSH_INTERVAL_SEC,
        max_size: int = QUEUE_MAX_SIZE,
    ):
        self._on_flush = on_flush
        self._dedup_window = dedup_window
        self._rate_limit = rate_limit
        self._flush_interval = flush_interval
        self._max_size = max_size

        self._queue: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._dedup_cache: Dict[str, float] = {}  # key -> last_seen
        self._rate_counters: Dict[str, deque] = defaultdict(lambda: deque())

        self._total_pushed = 0
        self._total_deduplicated = 0
        self._total_rate_limited = 0
        self._total_flushed = 0

        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._flush_loop, daemon=True, name="EventQueue")
        self._thread.start()
        logger.info("EventQueue: iniciada")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)

    def push(self, event: MonitoringEvent) -> bool:
        """
        Adiciona evento à fila.
        Retorna False se rejeitado por dedup ou rate limit.
        """
        with self._lock:
            # 1. Deduplicação
            now = time.time()
            key = event.dedup_key
            last = self._dedup_cache.get(key, 0)
            if now - last < self._dedup_window:
                self._total_deduplicated += 1
                logger.debug(f"EventQueue: dedup {key}")
                return False
            self._dedup_cache[key] = now

            # 2. Rate limiting por host
            host_times = self._rate_counters[event.host]
            # remover timestamps fora da janela de 1 minuto
            cutoff = now - 60
            while host_times and host_times[0] < cutoff:
                host_times.popleft()

            if len(host_times) >= self._rate_limit:
                self._total_rate_limited += 1
                logger.warning(f"EventQueue: rate limit atingido para {event.host}")
                return False
            host_times.append(now)

            # 3. Enfileirar
            self._queue.append(event)
            self._total_pushed += 1
            return True

    def push_batch(self, events: List[MonitoringEvent]) -> int:
        return sum(1 for e in events if self.push(e))

    def flush(self) -> List[MonitoringEvent]:
        """Drena a fila e retorna eventos agrupados por host."""
        with self._lock:
            if not self._queue:
                return []
            events = list(self._queue)
            self._queue.clear()
            self._total_flushed += len(events)

        # Agrupar por host (ordenar por host + timestamp)
        events.sort(key=lambda e: (e.host, e.timestamp))
        return events

    def _flush_loop(self):
        while self._running:
            time.sleep(self._flush_interval)
            try:
                events = self.flush()
                if events and self._on_flush:
                    self._on_flush(events)
            except Exception as e:
                logger.error(f"EventQueue flush error: {e}")

    def stats(self) -> dict:
        with self._lock:
            return {
                "queue_size": len(self._queue),
                "total_pushed": self._total_pushed,
                "total_deduplicated": self._total_deduplicated,
                "total_rate_limited": self._total_rate_limited,
                "total_flushed": self._total_flushed,
                "dedup_cache_size": len(self._dedup_cache),
            }
