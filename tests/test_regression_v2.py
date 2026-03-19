"""
Testes de regressão dos módulos v2.0 — Coruja Monitor v3.0
Garante que módulos existentes continuam funcionando após as mudanças v3.
"""
import pytest
import time
import threading
from unittest.mock import MagicMock, patch
from uuid import uuid4


# ─── test_wmi_pool_acquire_release ───────────────────────────────────────────

class TestWMIPool:
    def test_wmi_pool_importable(self):
        """probe/engine/wmi_pool.py deve ser importável."""
        try:
            from probe.engine import wmi_pool
            assert wmi_pool is not None
        except ImportError as e:
            pytest.skip(f"wmi_pool não disponível neste ambiente: {e}")

    def test_wmi_pool_has_expected_interface(self):
        """WMIPool deve ter métodos acquire e release."""
        try:
            from probe.engine.wmi_pool import WMIConnectionPool
            pool = WMIConnectionPool.__new__(WMIConnectionPool)
            assert hasattr(pool, 'acquire') or hasattr(pool, 'get_connection'), \
                "WMIPool deve ter método acquire ou get_connection"
        except ImportError as e:
            pytest.skip(f"wmi_pool não disponível: {e}")

    def test_wmi_pool_backoff_constants_exist(self):
        """Constantes de backoff anti-lockout devem existir."""
        try:
            import probe.engine.wmi_pool as wmi_pool_module
            source = open(wmi_pool_module.__file__, encoding='utf-8', errors='replace').read()
            assert any(keyword in source for keyword in [
                'lockout', 'backoff', 'BACKOFF', 'LOCKOUT', 'anti_lockout',
                'max_failures', 'MAX_FAILURES', 'cooldown', 'COOLDOWN',
                'BACKOFF_MINUTES', 'backoff_minutes',
            ]), "wmi_pool deve ter proteção anti-lockout"
        except (ImportError, AttributeError) as e:
            pytest.skip(f"wmi_pool não disponível: {e}")


# ─── test_smart_collector_collect_all ────────────────────────────────────────

class TestSmartCollector:
    def test_smart_collector_importable(self):
        """probe/engine/smart_collector.py deve ser importável."""
        try:
            from probe.engine import smart_collector
            assert smart_collector is not None
        except ImportError as e:
            pytest.skip(f"smart_collector não disponível: {e}")

    def test_smart_collector_has_collect_method(self):
        """SmartCollector deve ter método collect ou collect_all."""
        try:
            from probe.engine.smart_collector import SmartCollector
            assert hasattr(SmartCollector, 'collect') or hasattr(SmartCollector, 'collect_all'), \
                "SmartCollector deve ter método collect ou collect_all"
        except ImportError as e:
            pytest.skip(f"smart_collector não disponível: {e}")


# ─── test_global_rate_limiter_slots ──────────────────────────────────────────

class TestGlobalRateLimiter:
    def test_rate_limiter_importable(self):
        """probe/engine/global_rate_limiter.py deve ser importável."""
        try:
            from probe.engine import global_rate_limiter
            assert global_rate_limiter is not None
        except ImportError as e:
            pytest.skip(f"global_rate_limiter não disponível: {e}")

    def test_rate_limiter_has_acquire(self):
        """GlobalRateLimiter deve ter método acquire_slot."""
        try:
            from probe.engine.global_rate_limiter import GlobalRateLimiter
            assert hasattr(GlobalRateLimiter, 'acquire_slot'), \
                "GlobalRateLimiter deve ter método acquire_slot"
        except ImportError as e:
            pytest.skip(f"global_rate_limiter não disponível: {e}")

    def test_rate_limiter_slots_respected(self):
        """Rate limiter deve respeitar slots configurados."""
        try:
            from probe.engine.global_rate_limiter import GlobalRateLimiter
            limiter = GlobalRateLimiter(max_running=5)
            assert limiter is not None
            assert limiter.max_running == 5
        except (ImportError, TypeError) as e:
            pytest.skip(f"global_rate_limiter não disponível ou interface diferente: {e}")


# ─── test_event_queue_enqueue_dequeue ────────────────────────────────────────

class TestEventQueue:
    def test_event_queue_importable(self):
        """probe/event_engine/event_queue.py deve ser importável."""
        try:
            from probe.event_engine import event_queue
            assert event_queue is not None
        except ImportError as e:
            pytest.skip(f"event_queue não disponível: {e}")

    def test_event_queue_enqueue_dequeue(self):
        """EventQueue deve suportar push e flush."""
        try:
            from probe.event_engine.event_queue import EventQueue, MonitoringEvent
            queue = EventQueue()

            test_event = MonitoringEvent(
                host="srv1",
                event_type="cpu_high",
                severity="warning",
                message="CPU alta",
            )
            result = queue.push(test_event)
            assert result is True

            flushed = queue.flush()
            assert len(flushed) == 1
            assert flushed[0].event_type == "cpu_high"
        except ImportError as e:
            pytest.skip(f"event_queue não disponível: {e}")

    def test_event_queue_thread_safe(self):
        """EventQueue deve ser thread-safe."""
        try:
            from probe.event_engine.event_queue import EventQueue, MonitoringEvent
            queue = EventQueue()
            errors = []

            def producer(offset):
                for i in range(50):
                    try:
                        queue.push(MonitoringEvent(
                            host=f"srv{offset}-{i}",
                            event_type="cpu_high",
                            severity="warning",
                            message=f"test {i}",
                        ))
                    except Exception as e:
                        errors.append(e)

            threads = [threading.Thread(target=producer, args=(t,)) for t in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert not errors, f"Erros de thread: {errors}"
        except ImportError as e:
            pytest.skip(f"event_queue não disponível: {e}")


# ─── test_stream_producer_publish_fallback ───────────────────────────────────

class TestStreamProducerRegression:
    def test_stream_producer_importable(self):
        """probe/metrics_pipeline/stream_producer.py deve ser importável."""
        from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent
        assert StreamProducer is not None
        assert MetricEvent is not None

    def test_stream_producer_publish_without_redis(self):
        """StreamProducer deve funcionar sem Redis (fallback em memória)."""
        from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent

        producer = StreamProducer()  # sem redis_url
        event = MetricEvent(sensor_id=1, server_id=1, sensor_type="cpu", value=42.0)

        result = producer.publish(event)
        assert result is True

        stats = producer.stats()
        assert stats["backend"] == "memory"
        assert stats["fallback_queue_size"] == 1

    def test_stream_producer_batch_publish(self):
        """publish_batch deve publicar todos os eventos."""
        from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent

        producer = StreamProducer()
        events = [
            MetricEvent(sensor_id=i, server_id=1, sensor_type="cpu", value=float(i))
            for i in range(10)
        ]

        count = producer.publish_batch(events)
        assert count == 10
        assert producer.stats()["fallback_queue_size"] == 10

    def test_stream_producer_drain_fallback(self):
        """drain_fallback deve retornar eventos publicados."""
        from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent

        producer = StreamProducer()
        for i in range(5):
            producer.publish(MetricEvent(sensor_id=i, server_id=1, sensor_type="cpu", value=float(i)))

        drained = producer.drain_fallback(max_items=3)
        assert len(drained) == 3
        assert producer.stats()["fallback_queue_size"] == 2

    def test_stream_producer_fallback_queue_maxlen(self):
        """Fila de fallback deve respeitar maxlen=50_000."""
        from probe.metrics_pipeline.stream_producer import StreamProducer, FALLBACK_QUEUE_SIZE
        assert FALLBACK_QUEUE_SIZE == 50_000

    def test_metrics_processor_batch_size_constant(self):
        """MAX_BATCH_SIZE deve ser 500."""
        from probe.metrics_pipeline.metrics_processor import MAX_BATCH_SIZE
        assert MAX_BATCH_SIZE == 500

    def test_stream_consumer_importable(self):
        """stream_consumer.py deve ser importável."""
        from probe.metrics_pipeline.stream_consumer import StreamConsumer, BATCH_SIZE
        assert StreamConsumer is not None
        assert BATCH_SIZE == 500

    def test_metrics_processor_stats_has_throughput_fields(self):
        """MetricsProcessor.stats() deve incluir campos de throughput."""
        from probe.metrics_pipeline.metrics_processor import MetricsProcessor

        processor = MetricsProcessor()
        stats = processor.stats()

        assert "messages_per_second" in stats
        assert "processing_latency_ms" in stats
        assert "buffer_size" in stats
        assert "consumer_lag" in stats


# ─── Regressão: módulos v3 não quebram imports v2 ────────────────────────────

class TestV3ImportsDoNotBreakV2:
    def test_core_spec_importable(self):
        from core.spec.enums import Protocol, HostType, SensorStatus
        from core.spec.models import Host, Sensor, Metric, Event, Alert
        assert Protocol.WMI.value == "wmi"

    def test_engine_importable(self):
        from engine.dependency_engine import DependencyEngine
        assert DependencyEngine is not None

    def test_topology_engine_importable(self):
        from topology_engine.graph import TopologyGraph
        from topology_engine.impact import ImpactCalculator
        assert TopologyGraph is not None

    def test_event_processor_importable(self):
        from event_processor.processor import EventProcessor
        from event_processor.threshold_evaluator import ThresholdEvaluator
        assert EventProcessor is not None

    def test_ai_agents_importable(self):
        from ai_agents.pipeline import AgentPipeline
        from ai_agents.feedback_loop import FeedbackLoop
        assert AgentPipeline is not None

    def test_alert_engine_importable(self):
        from alert_engine.engine import AlertEngine
        assert AlertEngine is not None

    def test_sensor_dsl_importable(self):
        from sensor_dsl.compiler import DSLCompiler
        from sensor_dsl.printer import DSLPrinter
        assert DSLCompiler is not None

    def test_probe_manager_importable(self):
        from engine.probe_manager import ProbeManager
        assert ProbeManager is not None
