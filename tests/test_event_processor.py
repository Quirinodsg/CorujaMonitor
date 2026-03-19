"""
Testes da Fase 4 — Event Processor
Cobre: Property 7 (idempotência — mesmo status não gera evento duplicado)
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from core.spec.models import Metric, Sensor
from core.spec.enums import SensorStatus, EventSeverity, Protocol
from event_processor.threshold_evaluator import ThresholdEvaluator
from event_processor.processor import EventProcessor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_metric(value: float, sensor_id=None, host_id=None, unit="%"):
    return Metric(
        sensor_id=sensor_id or uuid4(),
        host_id=host_id or uuid4(),
        value=value,
        unit=unit,
        timestamp=datetime.now(timezone.utc),
    )


def make_sensor(sensor_type="cpu", thresholds=None):
    return Sensor(
        host_id=uuid4(),
        type=sensor_type,
        protocol=Protocol.WMI,
        interval=60,
        thresholds=thresholds or {"warning": 80, "critical": 95},
    )


# ---------------------------------------------------------------------------
# ThresholdEvaluator
# ---------------------------------------------------------------------------

class TestThresholdEvaluator:
    def setup_method(self):
        self.ev = ThresholdEvaluator()

    def test_ok_below_warning(self):
        m = make_metric(50.0)
        status = self.ev.evaluate(m, {"warning": 80, "critical": 95})
        assert status == SensorStatus.OK

    def test_warning_at_threshold(self):
        m = make_metric(80.0)
        status = self.ev.evaluate(m, {"warning": 80, "critical": 95})
        assert status == SensorStatus.WARNING

    def test_critical_at_threshold(self):
        m = make_metric(95.0)
        status = self.ev.evaluate(m, {"warning": 80, "critical": 95})
        assert status == SensorStatus.CRITICAL

    def test_critical_above_threshold(self):
        m = make_metric(99.9)
        status = self.ev.evaluate(m, {"warning": 80, "critical": 95})
        assert status == SensorStatus.CRITICAL

    def test_no_thresholds_returns_ok(self):
        m = make_metric(999.0)
        status = self.ev.evaluate(m, {})
        assert status == SensorStatus.OK

    def test_lower_is_worse_critical(self):
        """Memória livre: valor baixo é crítico."""
        m = make_metric(5.0)  # 5% livre
        status = self.ev.evaluate(m, {"warning": 20, "critical": 10, "lower": True})
        assert status == SensorStatus.CRITICAL

    def test_lower_is_worse_warning(self):
        m = make_metric(15.0)
        status = self.ev.evaluate(m, {"warning": 20, "critical": 10, "lower": True})
        assert status == SensorStatus.WARNING

    def test_lower_is_worse_ok(self):
        m = make_metric(50.0)
        status = self.ev.evaluate(m, {"warning": 20, "critical": 10, "lower": True})
        assert status == SensorStatus.OK

    def test_event_type_high_cpu(self):
        assert self.ev.get_event_type("cpu", SensorStatus.CRITICAL) == "high_cpu"

    def test_event_type_low_memory(self):
        assert self.ev.get_event_type("memory", SensorStatus.WARNING) == "low_memory"

    def test_event_type_disk_full(self):
        assert self.ev.get_event_type("disk", SensorStatus.CRITICAL) == "disk_full"

    def test_event_type_host_unreachable(self):
        assert self.ev.get_event_type("ping", SensorStatus.CRITICAL) == "host_unreachable"

    def test_event_type_service_down(self):
        assert self.ev.get_event_type("service", SensorStatus.CRITICAL) == "service_down"


# ---------------------------------------------------------------------------
# Property 7: Idempotência do EventProcessor
# ---------------------------------------------------------------------------

class TestEventProcessorIdempotency:
    def setup_method(self):
        self.processor = EventProcessor()  # sem redis, sem db

    def test_first_metric_generates_event_on_transition(self):
        """Primeira métrica crítica (sem estado anterior) gera evento."""
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        m = make_metric(96.0, sensor_id=sensor.id, host_id=sensor.host_id)
        event = self.processor.process(m, sensor)
        # Primeira vez: old_status=None, new_status=critical → transição
        assert event is not None
        assert event.type == "high_cpu"

    def test_same_status_consecutive_no_event(self):
        """Dois CRITICAL consecutivos: apenas o primeiro gera evento."""
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        m1 = make_metric(96.0, sensor_id=sid, host_id=hid)
        m2 = make_metric(97.0, sensor_id=sid, host_id=hid)

        event1 = self.processor.process(m1, sensor)
        event2 = self.processor.process(m2, sensor)

        assert event1 is not None   # transição None → critical
        assert event2 is None       # sem transição: critical → critical

    def test_three_same_status_only_first_event(self):
        """Três WARNING consecutivos: apenas o primeiro gera evento."""
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        events = []
        for val in [82.0, 83.0, 84.0]:
            m = make_metric(val, sensor_id=sid, host_id=hid)
            events.append(self.processor.process(m, sensor))

        assert events[0] is not None
        assert events[1] is None
        assert events[2] is None

    def test_transition_ok_to_warning(self):
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        # Primeiro: OK
        m_ok = make_metric(50.0, sensor_id=sid, host_id=hid)
        e1 = self.processor.process(m_ok, sensor)
        # Segundo: WARNING
        m_warn = make_metric(82.0, sensor_id=sid, host_id=hid)
        e2 = self.processor.process(m_warn, sensor)

        assert e1 is not None   # None → ok (transição)
        assert e2 is not None   # ok → warning (transição)
        assert e2.severity == EventSeverity.WARNING.value

    def test_transition_warning_to_critical(self):
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        self.processor.seed_state(str(sid), SensorStatus.WARNING)

        m = make_metric(96.0, sensor_id=sid, host_id=hid)
        event = self.processor.process(m, sensor)

        assert event is not None
        assert event.severity == EventSeverity.CRITICAL.value

    def test_recovery_critical_to_ok(self):
        """Recuperação (critical → ok) também gera evento."""
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        self.processor.seed_state(str(sid), SensorStatus.CRITICAL)

        m = make_metric(30.0, sensor_id=sid, host_id=hid)
        event = self.processor.process(m, sensor)

        assert event is not None
        assert event.severity == EventSeverity.INFO.value

    def test_seed_state_prevents_false_transition(self):
        """seed_state inicializa estado — evita evento falso na primeira coleta."""
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        # Simular que já estava em WARNING
        self.processor.seed_state(str(sid), SensorStatus.WARNING)

        # Mesma métrica WARNING — não deve gerar evento
        m = make_metric(82.0, sensor_id=sid, host_id=hid)
        event = self.processor.process(m, sensor)
        assert event is None

    def test_get_last_status(self):
        sensor = make_sensor(thresholds={"warning": 80, "critical": 95})
        sid, hid = sensor.id, sensor.host_id

        m = make_metric(96.0, sensor_id=sid, host_id=hid)
        self.processor.process(m, sensor)

        assert self.processor.get_last_status(str(sid)) == SensorStatus.CRITICAL.value

    def test_different_sensors_independent(self):
        """Dois sensores diferentes têm estado independente."""
        s1 = make_sensor(thresholds={"warning": 80, "critical": 95})
        s2 = make_sensor(thresholds={"warning": 80, "critical": 95})

        m1 = make_metric(96.0, sensor_id=s1.id, host_id=s1.host_id)
        m2 = make_metric(96.0, sensor_id=s2.id, host_id=s2.host_id)

        e1 = self.processor.process(m1, s1)
        e2 = self.processor.process(m2, s2)

        # Ambos devem gerar evento (primeiro para cada sensor)
        assert e1 is not None
        assert e2 is not None


# ---------------------------------------------------------------------------
# Testes de thresholds dinâmicos
# ---------------------------------------------------------------------------

class TestDynamicThresholds:
    def test_custom_thresholds_override(self):
        """Thresholds customizados por host sobrescrevem padrão."""
        ev = ThresholdEvaluator()
        m = make_metric(85.0)
        # Threshold padrão: warning=80 → seria WARNING
        # Threshold customizado: warning=90 → deve ser OK
        status = ev.evaluate(m, {"warning": 90, "critical": 98})
        assert status == SensorStatus.OK

    def test_only_critical_threshold(self):
        ev = ThresholdEvaluator()
        m = make_metric(96.0)
        status = ev.evaluate(m, {"critical": 95})
        assert status == SensorStatus.CRITICAL

    def test_only_warning_threshold(self):
        ev = ThresholdEvaluator()
        m = make_metric(82.0)
        status = ev.evaluate(m, {"warning": 80})
        assert status == SensorStatus.WARNING
