"""
Stream Consumer — consome métricas do Redis Stream (ou fila em memória)
e persiste no banco via API ou diretamente.

Roda como thread daemon dentro da probe.
"""
import logging
import threading
import time
from typing import Callable, List, Optional

from .stream_producer import MetricEvent, StreamProducer, STREAM_KEY

logger = logging.getLogger(__name__)

BATCH_SIZE = 500
POLL_INTERVAL_SEC = 1.0
CONSUMER_GROUP = "coruja-consumers"
CONSUMER_NAME = "probe-consumer-1"


class StreamConsumer:
    """
    Consome eventos do Redis Stream ou fila em memória do producer.

    Uso:
        def persist(events): ...  # salva no banco
        consumer = StreamConsumer(producer, on_batch=persist)
        consumer.start()
    """

    def __init__(
        self,
        producer: StreamProducer,
        on_batch: Callable[[List[MetricEvent]], None],
        batch_size: int = BATCH_SIZE,
        poll_interval: float = POLL_INTERVAL_SEC,
    ):
        self._producer = producer
        self._on_batch = on_batch
        self._batch_size = batch_size
        self._poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._processed = 0
        self._errors = 0

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="StreamConsumer")
        self._thread.start()
        logger.info("StreamConsumer: iniciado")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("StreamConsumer: parado")

    def _loop(self):
        while self._running:
            try:
                # Tentar Redis primeiro
                if self._producer._redis:
                    self._consume_redis()
                else:
                    self._consume_fallback()
            except Exception as e:
                logger.error(f"StreamConsumer: erro no loop: {e}")
                self._errors += 1
            time.sleep(self._poll_interval)

    def _consume_redis(self):
        try:
            # Criar consumer group se não existir
            try:
                self._producer._redis.xgroup_create(
                    STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True
                )
            except Exception:
                pass  # já existe

            messages = self._producer._redis.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {STREAM_KEY: ">"},
                count=self._batch_size,
                block=int(self._poll_interval * 1000),
            )

            if not messages:
                return

            events = []
            ids = []
            for stream_name, entries in messages:
                for msg_id, data in entries:
                    try:
                        event = MetricEvent(
                            sensor_id=int(data.get("sensor_id", 0)),
                            server_id=int(data.get("server_id", 0)),
                            sensor_type=data.get("sensor_type", ""),
                            value=float(data.get("value", 0)),
                            unit=data.get("unit", ""),
                            status=data.get("status", "ok"),
                            timestamp=float(data.get("timestamp", 0)),
                        )
                        events.append(event)
                        ids.append(msg_id)
                    except Exception as e:
                        logger.warning(f"StreamConsumer: erro ao parsear mensagem: {e}")

            if events:
                self._on_batch(events)
                self._processed += len(events)
                # ACK
                self._producer._redis.xack(STREAM_KEY, CONSUMER_GROUP, *ids)

        except Exception as e:
            logger.error(f"StreamConsumer Redis: {e}")

    def _consume_fallback(self):
        events = self._producer.drain_fallback(self._batch_size)
        if events:
            self._on_batch(events)
            self._processed += len(events)

    def stats(self) -> dict:
        return {
            "processed": self._processed,
            "errors": self._errors,
            "running": self._running,
        }
