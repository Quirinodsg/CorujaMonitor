"""
Metrics Processor — processa e persiste lotes de MetricEvent.

Responsabilidades:
  - deduplicação por (sensor_id, timestamp)
  - normalização de valores
  - persistência via HTTP na API (ou diretamente no banco)
  - batch insert máximo 500 métricas por operação
  - métricas de throughput: messages_per_second, processing_latency_ms, buffer_size, consumer_lag
"""
import logging
import time
from collections import deque
from typing import List, Optional

import requests

from .stream_producer import MetricEvent

logger = logging.getLogger(__name__)

DEDUP_WINDOW_SEC = 5  # ignora duplicatas dentro de 5s
MAX_BATCH_SIZE = 500   # máximo de métricas por operação (Requirement 12.3)
LATENCY_WARNING_THRESHOLD_SEC = 5.0  # WARNING se latência > 5s


class MetricsProcessor:
    """
    Processa lotes de MetricEvent e persiste via API.
    Batch insert máximo MAX_BATCH_SIZE (500) métricas por operação.

    Uso:
        processor = MetricsProcessor(api_url="http://api:8000")
        consumer = StreamConsumer(producer, on_batch=processor.process_batch)
    """

    def __init__(self, api_url: str = "http://localhost:8000", api_token: str = ""):
        self._api_url = api_url.rstrip("/")
        self._api_token = api_token
        self._seen: dict = {}  # (sensor_id, ts_bucket) -> True
        self._persisted = 0
        self._deduplicated = 0
        self._errors = 0
        # Throughput tracking
        self._latency_window: deque = deque(maxlen=100)  # últimas 100 latências (ms)
        self._messages_per_second_window: deque = deque(maxlen=60)  # últimos 60 segundos
        self._last_second_ts: float = time.time()
        self._messages_this_second: int = 0

    def process_batch(self, events: List[MetricEvent]):
        """Processa e persiste lote de eventos em sub-batches de MAX_BATCH_SIZE."""
        unique = self._deduplicate(events)
        if not unique:
            return

        # Dividir em sub-batches de no máximo MAX_BATCH_SIZE
        for i in range(0, len(unique), MAX_BATCH_SIZE):
            sub_batch = unique[i:i + MAX_BATCH_SIZE]
            start_ts = time.monotonic()
            try:
                self._persist(sub_batch)
                self._persisted += len(sub_batch)
                latency_ms = (time.monotonic() - start_ts) * 1000
                self._latency_window.append(latency_ms)
                self._track_throughput(len(sub_batch))

                if latency_ms / 1000 > LATENCY_WARNING_THRESHOLD_SEC:
                    logger.warning(
                        f"MetricsProcessor: latência alta {latency_ms:.0f}ms "
                        f"(threshold={LATENCY_WARNING_THRESHOLD_SEC}s). "
                        f"Considere aumentar consumidores."
                    )
            except Exception as e:
                logger.error(f"MetricsProcessor: erro ao persistir {len(sub_batch)} eventos: {e}")
                self._errors += 1

        self._cleanup_dedup_cache()

    def _deduplicate(self, events: List[MetricEvent]) -> List[MetricEvent]:
        unique = []
        for event in events:
            bucket = int(event.timestamp / DEDUP_WINDOW_SEC)
            key = (event.sensor_id, bucket)
            if key not in self._seen:
                self._seen[key] = time.monotonic()
                unique.append(event)
            else:
                self._deduplicated += 1
        return unique

    def _cleanup_dedup_cache(self):
        now = time.monotonic()
        expired = [k for k, t in self._seen.items() if now - t > DEDUP_WINDOW_SEC * 2]
        for k in expired:
            del self._seen[k]

    def _persist(self, events: List[MetricEvent]):
        """Envia lote para a API."""
        headers = {}
        if self._api_token:
            headers["Authorization"] = f"Bearer {self._api_token}"

        payload = [
            {
                "sensor_id": e.sensor_id,
                "server_id": e.server_id,
                "sensor_type": e.sensor_type,
                "value": e.value,
                "unit": e.unit,
                "status": e.status,
                "timestamp": e.timestamp,
            }
            for e in events
        ]

        resp = requests.post(
            f"{self._api_url}/api/v1/metrics/batch",
            json=payload,
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        logger.debug(f"MetricsProcessor: {len(events)} eventos persistidos")

    def _track_throughput(self, count: int):
        now = time.time()
        if now - self._last_second_ts >= 1.0:
            self._messages_per_second_window.append(self._messages_this_second)
            self._messages_this_second = count
            self._last_second_ts = now
        else:
            self._messages_this_second += count

    def stats(self) -> dict:
        avg_latency = (
            sum(self._latency_window) / len(self._latency_window)
            if self._latency_window else 0.0
        )
        avg_mps = (
            sum(self._messages_per_second_window) / len(self._messages_per_second_window)
            if self._messages_per_second_window else 0.0
        )
        return {
            "persisted": self._persisted,
            "deduplicated": self._deduplicated,
            "errors": self._errors,
            "dedup_cache_size": len(self._seen),
            "messages_per_second": round(avg_mps, 2),
            "processing_latency_ms": round(avg_latency, 2),
            "buffer_size": len(self._latency_window),
            "consumer_lag": 0,  # preenchido pelo consumer quando disponível
        }
