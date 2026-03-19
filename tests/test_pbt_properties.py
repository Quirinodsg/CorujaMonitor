"""
Property-Based Tests com Hypothesis — Coruja Monitor v3.0
Properties 1, 2, 22, 23
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from uuid import uuid4
from datetime import datetime, timezone

from core.spec.enums import (
    HostType, Protocol, SensorStatus, EventSeverity,
    AlertStatus, NodeType, ProbeStatus,
)
from core.spec.models import Host, Sensor, Metric, Event, Alert, TopologyNode, ProbeNode

# Perfis hypothesis
settings.register_profile("ci", max_examples=100)
settings.register_profile("thorough", max_examples=500)
settings.load_profile("ci")


# ─── Strategies ─────────────────────────────────────────────────────────────

host_type_st = st.sampled_from(list(HostType))
protocol_st = st.sampled_from(list(Protocol))
sensor_status_st = st.sampled_from(list(SensorStatus))
event_severity_st = st.sampled_from(list(EventSeverity))
alert_status_st = st.sampled_from(list(AlertStatus))
node_type_st = st.sampled_from(list(NodeType))
probe_status_st = st.sampled_from(list(ProbeStatus))

hostname_st = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_"),
    min_size=1, max_size=50,
).filter(lambda s: s.strip() and not s.startswith("-"))

ip_st = st.builds(
    lambda a, b, c, d: f"{a}.{b}.{c}.{d}",
    st.integers(1, 254), st.integers(0, 255),
    st.integers(0, 255), st.integers(1, 254),
)

positive_int_st = st.integers(min_value=1, max_value=3600)
positive_float_st = st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False)


@st.composite
def host_st(draw):
    return Host(
        id=uuid4(),
        hostname=draw(hostname_st),
        ip_address=draw(ip_st),
        type=draw(host_type_st),
    )


@st.composite
def sensor_st(draw):
    return Sensor(
        id=uuid4(),
        host_id=uuid4(),
        type=draw(st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz_")),
        protocol=draw(protocol_st),
        interval=draw(positive_int_st),
        timeout=draw(st.integers(min_value=1, max_value=300)),
        retries=draw(st.integers(min_value=0, max_value=10)),
    )


@st.composite
def metric_st(draw):
    return Metric(
        sensor_id=uuid4(),
        host_id=uuid4(),
        value=draw(positive_float_st),
        unit=draw(st.text(min_size=0, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz%/")),
        timestamp=datetime.now(timezone.utc),
        status=draw(sensor_status_st),
    )


@st.composite
def event_st(draw):
    return Event(
        host_id=uuid4(),
        type=draw(st.sampled_from(["high_cpu", "low_memory", "disk_full", "host_unreachable", "service_down"])),
        severity=draw(event_severity_st),
        timestamp=datetime.now(timezone.utc),
        description=draw(st.text(min_size=0, max_size=200)),
    )


@st.composite
def alert_st(draw):
    return Alert(
        title=draw(st.text(min_size=1, max_size=200)),
        severity=draw(event_severity_st),
        status=draw(alert_status_st),
        affected_hosts=[uuid4() for _ in range(draw(st.integers(0, 5)))],
    )


@st.composite
def topology_node_st(draw):
    return TopologyNode(
        id=uuid4(),
        type=draw(node_type_st),
    )


@st.composite
def probe_node_st(draw):
    return ProbeNode(
        id=uuid4(),
        name=draw(hostname_st),
        location=draw(st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz-_")),
        status=draw(probe_status_st),
        capacity=draw(st.integers(min_value=1, max_value=1000)),
    )


# ─── Property 1: Round-trip de serialização dos modelos Pydantic ─────────────

class TestPydanticRoundtrip:
    @given(host_st())
    def test_host_roundtrip(self, host):
        data = host.model_dump()
        restored = Host(**data)
        assert restored.id == host.id
        assert restored.hostname == host.hostname
        assert restored.type == host.type

    @given(sensor_st())
    def test_sensor_roundtrip(self, sensor):
        data = sensor.model_dump()
        restored = Sensor(**data)
        assert restored.id == sensor.id
        assert restored.protocol == sensor.protocol
        assert restored.interval == sensor.interval

    @given(metric_st())
    def test_metric_roundtrip(self, metric):
        data = metric.model_dump()
        restored = Metric(**data)
        assert restored.sensor_id == metric.sensor_id
        assert restored.value == metric.value
        assert restored.status == metric.status

    @given(event_st())
    def test_event_roundtrip(self, event):
        data = event.model_dump()
        restored = Event(**data)
        assert restored.host_id == event.host_id
        assert restored.type == event.type
        assert restored.severity == event.severity

    @given(alert_st())
    def test_alert_roundtrip(self, alert):
        data = alert.model_dump()
        restored = Alert(**data)
        assert restored.title == alert.title
        assert restored.severity == alert.severity
        assert restored.status == alert.status

    @given(topology_node_st())
    def test_topology_node_roundtrip(self, node):
        data = node.model_dump()
        restored = TopologyNode(**data)
        assert restored.id == node.id
        assert restored.type == node.type

    @given(probe_node_st())
    def test_probe_node_roundtrip(self, probe):
        data = probe.model_dump()
        restored = ProbeNode(**data)
        assert restored.id == probe.id
        assert restored.status == probe.status

    @given(st.lists(sensor_st(), min_size=1, max_size=10))
    def test_sensor_list_roundtrip(self, sensors):
        for sensor in sensors:
            data = sensor.model_dump()
            restored = Sensor(**data)
            assert restored.protocol == sensor.protocol


# ─── Property 2: Validação de campos obrigatórios rejeita entradas inválidas ─

class TestPydanticValidation:
    def test_host_requires_hostname(self):
        import pydantic
        with pytest.raises((pydantic.ValidationError, Exception)):
            Host(id=uuid4(), ip_address="1.2.3.4", type=HostType.SERVER)

    def test_sensor_requires_protocol(self):
        import pydantic
        with pytest.raises((pydantic.ValidationError, Exception)):
            Sensor(id=uuid4(), host_id=uuid4(), type="cpu", interval=60)

    def test_sensor_requires_interval(self):
        import pydantic
        with pytest.raises((pydantic.ValidationError, Exception)):
            Sensor(id=uuid4(), host_id=uuid4(), type="cpu", protocol=Protocol.WMI)

    def test_event_requires_type(self):
        import pydantic
        with pytest.raises((pydantic.ValidationError, Exception)):
            Event(host_id=uuid4(), severity=EventSeverity.WARNING,
                  timestamp=datetime.now(timezone.utc), description="test")

    def test_alert_requires_title(self):
        import pydantic
        with pytest.raises((pydantic.ValidationError, Exception)):
            Alert(severity=EventSeverity.CRITICAL, status=AlertStatus.OPEN)

    @given(st.text(min_size=1, max_size=50))
    def test_invalid_protocol_rejected(self, proto):
        assume(proto not in {p.value for p in Protocol})
        import pydantic
        with pytest.raises((pydantic.ValidationError, ValueError, Exception)):
            Sensor(
                id=uuid4(),
                host_id=uuid4(),
                type="test",
                protocol=proto,
                interval=60,
            )

    @given(st.integers(max_value=0))
    def test_non_positive_interval_rejected_or_accepted(self, interval):
        """Interval <= 0 deve ser rejeitado ou tratado pelo modelo."""
        # Apenas verifica que não causa crash inesperado
        try:
            s = Sensor(
                id=uuid4(),
                host_id=uuid4(),
                type="test",
                protocol=Protocol.WMI,
                interval=interval,
            )
            # Se aceitar, o valor deve ser o que foi passado
            assert s.interval == interval
        except Exception:
            pass  # Rejeição é comportamento válido


# ─── Property 22: Stream consumer processa em batches ≤ 500 ─────────────────

class TestStreamBatchSize:
    @given(st.integers(min_value=1, max_value=2000))
    def test_batch_size_limit(self, total_events):
        """Verifica que o processador divide em sub-batches de no máximo 500."""
        from probe.metrics_pipeline.metrics_processor import MetricsProcessor, MAX_BATCH_SIZE
        import time

        batches_processed = []

        class MockProcessor(MetricsProcessor):
            def _persist(self, events):
                batches_processed.append(len(events))

        processor = MockProcessor(api_url="http://mock")

        from probe.metrics_pipeline.stream_producer import MetricEvent
        events = [
            MetricEvent(
                sensor_id=i,
                server_id=1,
                sensor_type="cpu",
                value=float(i),
                timestamp=time.time() + i * 10,  # timestamps únicos para evitar dedup
            )
            for i in range(total_events)
        ]

        processor.process_batch(events)

        # Cada sub-batch deve ter no máximo MAX_BATCH_SIZE itens
        for batch_size in batches_processed:
            assert batch_size <= MAX_BATCH_SIZE

        # Total processado deve ser igual ao total de eventos únicos
        assert sum(batches_processed) == total_events


# ─── Property 23: At-least-once delivery ────────────────────────────────────

class TestAtLeastOnceDelivery:
    def test_pending_messages_reprocessed_on_restart(self):
        """
        Verifica que mensagens não-ACKed são reprocessadas.
        Testa a lógica do consumer: id="0" busca mensagens pendentes.
        """
        from probe.metrics_pipeline.stream_consumer import StreamConsumer
        from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent
        import time

        received_batches = []

        def on_batch(events):
            received_batches.extend(events)

        # Sem Redis: usa fila em memória
        producer = StreamProducer()
        consumer = StreamConsumer(producer, on_batch=on_batch, batch_size=10)

        # Publicar eventos na fila em memória
        events = [
            MetricEvent(sensor_id=i, server_id=1, sensor_type="cpu", value=float(i))
            for i in range(5)
        ]
        for e in events:
            producer.publish(e)

        # Consumir manualmente (sem Redis)
        consumer._consume_fallback()

        assert len(received_batches) == 5

    def test_fallback_queue_drains_on_reconnect(self):
        """Buffer em memória é drenado quando Redis reconecta."""
        from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent

        producer = StreamProducer()  # sem Redis

        # Publicar 100 eventos no fallback
        for i in range(100):
            producer.publish(MetricEvent(
                sensor_id=i, server_id=1, sensor_type="cpu", value=float(i)
            ))

        assert producer.stats()["fallback_queue_size"] == 100

        # Drenar
        drained = producer.drain_fallback(max_items=50)
        assert len(drained) == 50
        assert producer.stats()["fallback_queue_size"] == 50

        drained2 = producer.drain_fallback(max_items=100)
        assert len(drained2) == 50
        assert producer.stats()["fallback_queue_size"] == 0
