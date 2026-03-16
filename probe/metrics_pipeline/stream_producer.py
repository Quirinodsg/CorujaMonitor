"""
Stream Producer — publica métricas em Redis Streams (ou fila em memória como fallback).

Arquitetura:
  probe → stream_producer → Redis Stream "metrics:raw" → stream_consumer → TimescaleDB

Fallback sem Redis:
  probe → stream_producer → in-memory deque → stream_consumer → TimescaleDB
"""
import json
import logging
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

STREAM_KEY = "metrics:raw"
MAX_STREAM_LEN = 100_000  # trim automático no Redis
FALLBACK_QUEUE_SIZE = 50_000


@dataclass
class MetricEvent:
    sensor_id: int
    server_id: int
    sensor_type: str
    value: float
    unit: str = ""
    status: str = "ok"
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class StreamProducer:
    """
    Publica MetricEvent no Redis Stream ou fila em memória.

    Uso:
        producer = StreamProducer()
        producer.publish(MetricEvent(sensor_id=1, server_id=2, ...))
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._redis = None
        self._fallback_queue: deque = deque(maxlen=FALLBACK_QUEUE_SIZE)
        self._lock = threading.Lock()
        self._published = 0
        self._errors = 0

        if redis_url:
            self._connect_redis(redis_url)

    def _connect_redis(self, redis_url: str):
        try:
            import redis
            self._redis = redis.from_url(redis_url, decode_responses=True)
            self._redis.ping()
            logger.info(f"StreamProducer: conectado ao Redis {redis_url}")
        except Exception as e:
            logger.warning(f"StreamProducer: Redis indisponível ({e}), usando fila em memória")
            self._redis = None

    def publish(self, event: MetricEvent) -> bool:
        """Publica evento. Retorna True se bem-sucedido."""
        try:
            if self._redis:
                self._redis.xadd(
                    STREAM_KEY,
                    event.to_dict(),
                    maxlen=MAX_STREAM_LEN,
                    approximate=True,
                )
            else:
                with self._lock:
                    self._fallback_queue.append(event)

            with self._lock:
                self._published += 1
            return True

        except Exception as e:
            logger.error(f"StreamProducer: erro ao publicar evento: {e}")
            # fallback para fila em memória
            with self._lock:
                self._fallback_queue.append(event)
                self._errors += 1
            return False

    def publish_batch(self, events: list) -> int:
        """Publica lote de eventos. Retorna quantidade publicada."""
        count = 0
        for event in events:
            if self.publish(event):
                count += 1
        return count

    def drain_fallback(self, max_items: int = 1000) -> list:
        """Drena fila em memória (para o consumer processar)."""
        items = []
        with self._lock:
            for _ in range(min(max_items, len(self._fallback_queue))):
                items.append(self._fallback_queue.popleft())
        return items

    def stats(self) -> dict:
        with self._lock:
            return {
                "published": self._published,
                "errors": self._errors,
                "fallback_queue_size": len(self._fallback_queue),
                "backend": "redis" if self._redis else "memory",
            }


# Singleton global
_producer: Optional[StreamProducer] = None


def get_producer(redis_url: Optional[str] = None) -> StreamProducer:
    global _producer
    if _producer is None:
        _producer = StreamProducer(redis_url=redis_url)
    return _producer
