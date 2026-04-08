"""
EventSimulator — Coruja Monitor v3.0.
Gera eventos e métricas sintéticos para testes de integração e carga.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from core.spec.enums import EventSeverity, SensorStatus
from core.spec.models import Event, Metric


class EventSimulator:
    """Gerador de dados sintéticos para testes."""

    def generate_metric(
        self,
        host_id: UUID | None = None,
        sensor_id: UUID | None = None,
        sensor_type: str = "cpu",
        value: float = 50.0,
        unit: str = "%",
        status: SensorStatus = SensorStatus.OK,
        timestamp: datetime | None = None,
    ) -> Metric:
        """Gera uma única métrica sintética."""
        return Metric(
            sensor_id=sensor_id or uuid4(),
            host_id=host_id or uuid4(),
            value=value,
            unit=unit,
            timestamp=timestamp or datetime.now(timezone.utc),
            status=status,
        )

    def generate_event(
        self,
        host_id: UUID | None = None,
        event_type: str = "cpu_warning",
        severity: EventSeverity = EventSeverity.WARNING,
        timestamp: datetime | None = None,
        description: str = "",
    ) -> Event:
        """Gera um único evento sintético."""
        return Event(
            host_id=host_id or uuid4(),
            type=event_type,
            severity=severity,
            timestamp=timestamp or datetime.now(timezone.utc),
            description=description or f"Simulated {event_type}",
        )

    def generate_metric_stream(
        self,
        host_id: UUID | None = None,
        sensor_id: UUID | None = None,
        count: int = 10,
        interval_ms: int = 1000,
        base_value: float = 50.0,
        unit: str = "%",
    ) -> list[Metric]:
        """
        Gera sequência de métricas com timestamps espaçados.
        Valores oscilam levemente em torno de base_value.
        """
        host_id = host_id or uuid4()
        sensor_id = sensor_id or uuid4()
        base_ts = datetime.now(timezone.utc)
        metrics = []
        for i in range(count):
            ts = base_ts + timedelta(milliseconds=i * interval_ms)
            # Oscilação simples: ±5% do base_value
            offset = (i % 5 - 2) * (base_value * 0.02)
            metrics.append(
                Metric(
                    sensor_id=sensor_id,
                    host_id=host_id,
                    value=round(base_value + offset, 2),
                    unit=unit,
                    timestamp=ts,
                    status=SensorStatus.OK,
                )
            )
        return metrics

    def generate_state_transitions(
        self,
        host_id: UUID | None = None,
        sensor_id: UUID | None = None,
        transitions: list[tuple[float, SensorStatus]] | None = None,
    ) -> list[Metric]:
        """
        Gera métricas que provocam transições de estado específicas.
        transitions: lista de (value, expected_status).
        Default: ok → warning → critical → ok.
        """
        host_id = host_id or uuid4()
        sensor_id = sensor_id or uuid4()
        if transitions is None:
            transitions = [
                (30.0, SensorStatus.OK),
                (82.0, SensorStatus.WARNING),
                (96.0, SensorStatus.CRITICAL),
                (25.0, SensorStatus.OK),
            ]
        base_ts = datetime.now(timezone.utc)
        metrics = []
        for i, (value, status) in enumerate(transitions):
            metrics.append(
                Metric(
                    sensor_id=sensor_id,
                    host_id=host_id,
                    value=value,
                    unit="%",
                    timestamp=base_ts + timedelta(seconds=i * 30),
                    status=status,
                )
            )
        return metrics

    def generate_flood(
        self,
        host_id: UUID | None = None,
        count: int = 150,
        window_seconds: float = 60.0,
    ) -> list[Event]:
        """
        Gera flood de eventos para testar flood protection.
        Todos os eventos dentro da janela temporal especificada.
        """
        host_id = host_id or uuid4()
        base_ts = datetime.now(timezone.utc)
        interval = window_seconds / max(count, 1)
        events = []
        for i in range(count):
            events.append(
                Event(
                    host_id=host_id,
                    type="cpu_critical",
                    severity=EventSeverity.CRITICAL,
                    timestamp=base_ts + timedelta(seconds=i * interval),
                    description=f"Flood event {i + 1}/{count}",
                )
            )
        return events
