"""
Event Processor — Coruja Monitor v3.0
Converte Metrics em Events apenas em transições de estado.

Princípio: Metric = dado contínuo; Event = mudança de estado discreta.
Gera Event apenas quando status muda (ok→warning, warning→critical, critical→ok).
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from core.spec.models import Metric, Event, Sensor
from core.spec.enums import SensorStatus, EventSeverity
from event_processor.threshold_evaluator import ThresholdEvaluator

logger = logging.getLogger(__name__)

# Mapeamento de SensorStatus → EventSeverity
_STATUS_TO_SEVERITY = {
    SensorStatus.WARNING: EventSeverity.WARNING,
    SensorStatus.CRITICAL: EventSeverity.CRITICAL,
    SensorStatus.OK: EventSeverity.INFO,
    SensorStatus.UNKNOWN: EventSeverity.INFO,
}


class EventProcessor:
    """
    Processa métricas e gera eventos apenas em transições de estado.

    Estado anterior por sensor mantido em memória (_last_status).
    Em reinicialização, o estado pode ser reconstruído externamente via seed_state().

    Publicação no Redis Stream: opcional (redis_client pode ser None para testes).
    """

    def __init__(self, redis_client=None, db_session=None):
        # {sensor_id: SensorStatus_value_str}
        self._last_status: dict[str, str] = {}
        self._evaluator = ThresholdEvaluator()
        self._redis = redis_client
        self._db = db_session
        self._events_stream_key = "events_stream"
        self._stream_maxlen = 50_000

    def seed_state(self, sensor_id: str, status: SensorStatus) -> None:
        """
        Inicializa estado anterior de um sensor (usado na reinicialização
        para reconstruir _last_status a partir da última métrica no banco).
        """
        self._last_status[sensor_id] = status.value if hasattr(status, "value") else status

    def process(self, metric: Metric, sensor: Optional[Sensor] = None) -> Optional[Event]:
        """
        Processa uma métrica.
        Retorna Event se houve transição de estado, None caso contrário.

        Property 7: idempotência — mesmo status consecutivo não gera novo Event.
        """
        sensor_id = str(metric.sensor_id)
        thresholds = sensor.thresholds if sensor else {}
        sensor_type = sensor.type if sensor else "unknown"

        # Avaliar status atual
        new_status = self._evaluator.evaluate(metric, thresholds)
        new_status_val = new_status.value if hasattr(new_status, "value") else new_status

        # Verificar transição de estado
        old_status_val = self._last_status.get(sensor_id)

        if old_status_val == new_status_val:
            # Sem transição — não gera evento
            logger.debug(
                "EventProcessor: sensor %s sem transição (%s → %s)",
                sensor_id, old_status_val, new_status_val,
            )
            self._persist_metric(metric)
            return None

        # Transição detectada — atualizar estado e gerar evento
        self._last_status[sensor_id] = new_status_val
        logger.info(
            "EventProcessor: sensor %s transição %s → %s",
            sensor_id, old_status_val, new_status_val,
        )

        # Persistir métrica
        self._persist_metric(metric)

        # Gerar evento apenas se novo status não for OK (ou se voltou ao OK — recovery)
        # Gera evento em qualquer transição (incluindo recovery ok)
        event_type = self._evaluator.get_event_type(sensor_type, new_status)
        severity = _STATUS_TO_SEVERITY.get(new_status, EventSeverity.INFO)

        event = Event(
            host_id=metric.host_id,
            type=event_type,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            source_metric_id=metric.sensor_id,
            description=(
                f"{sensor_type} {new_status_val}: {metric.value}{metric.unit} "
                f"(anterior: {old_status_val or 'unknown'})"
            ),
        )

        # Publicar no Redis Stream
        self._publish_event(event)

        return event

    def _persist_metric(self, metric: Metric) -> None:
        """Persiste métrica no TimescaleDB (se db_session disponível)."""
        if self._db is None:
            return
        try:
            self._db.execute(
                """
                INSERT INTO metrics_ts (time, sensor_id, host_id, value, unit, status)
                VALUES (:time, :sensor_id, :host_id, :value, :unit, :status)
                """,
                {
                    "time": metric.timestamp,
                    "sensor_id": str(metric.sensor_id),
                    "host_id": str(metric.host_id),
                    "value": metric.value,
                    "unit": metric.unit,
                    "status": metric.status if isinstance(metric.status, str) else metric.status.value,
                },
            )
            self._db.commit()
        except Exception as e:
            logger.error("EventProcessor: falha ao persistir métrica: %s", e)

    def _publish_event(self, event: Event) -> None:
        """Publica evento no Redis Stream events_stream."""
        if self._redis is None:
            return
        try:
            self._redis.xadd(
                self._events_stream_key,
                {
                    "event_id": str(event.id),
                    "host_id": str(event.host_id),
                    "type": event.type,
                    "severity": event.severity if isinstance(event.severity, str) else event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "description": event.description,
                },
                maxlen=self._stream_maxlen,
            )
        except Exception as e:
            logger.error("EventProcessor: falha ao publicar evento no stream: %s", e)

    def get_last_status(self, sensor_id: str) -> Optional[str]:
        """Retorna último status conhecido de um sensor."""
        return self._last_status.get(str(sensor_id))
