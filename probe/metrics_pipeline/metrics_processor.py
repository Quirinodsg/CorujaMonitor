"""
Metrics Processor — processa e persiste lotes de MetricEvent.

Responsabilidades:
  - deduplicação por (sensor_id, timestamp)
  - normalização de valores
  - persistência via HTTP na API (ou diretamente no banco)
"""
import logging
import time
from typing import List, Optional

import requests

from .stream_producer import MetricEvent

logger = logging.getLogger(__name__)

DEDUP_WINDOW_SEC = 5  # ignora duplicatas dentro de 5s


class MetricsProcessor:
    """
    Processa lotes de MetricEvent e persiste via API.

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

    def process_batch(self, events: List[MetricEvent]):
        """Processa e persiste lote de eventos."""
        unique = self._deduplicate(events)
        if not unique:
            return

        try:
            self._persist(unique)
            self._persisted += len(unique)
        except Exception as e:
            logger.error(f"MetricsProcessor: erro ao persistir {len(unique)} eventos: {e}")
            self._errors += 1

        # Limpar cache de dedup periodicamente
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

    def stats(self) -> dict:
        return {
            "persisted": self._persisted,
            "deduplicated": self._deduplicated,
            "errors": self._errors,
            "dedup_cache_size": len(self._seen),
        }
