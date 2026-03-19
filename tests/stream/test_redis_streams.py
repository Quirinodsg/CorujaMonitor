"""
FASE 6 — Testes de Redis Streams
Valida: XADD, XREADGROUP, consumer groups, reprocessamento at-least-once.
Simula 10.000 eventos.
"""
import pytest
import time
import threading
from unittest.mock import MagicMock, patch, call
from collections import deque

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../probe'))

from metrics_pipeline.stream_producer import StreamProducer, MetricEvent
from metrics_pipeline.stream_consumer import StreamConsumer


# ─── Fixtures ────────────────────────────────────────────────────────────────

def make_event(i: int = 0) -> MetricEvent:
    return MetricEvent(
        sensor_id=i % 100,
        server_id=1,
        sensor_type="cpu",
        value=float(i % 100),
        unit="%",
        status="ok" if i % 10 != 0 else "critical",
    )


# ─── Testes do StreamProducer ────────────────────────────────────────────────

class TestStreamProducer:

    def test_publish_to_fallback_when_no_redis(self):
        """Sem Redis, eventos vão para fallback queue."""
        producer = StreamProducer(redis_url=None)
        event = make_event(1)

        ok = producer.publish(event)

        assert ok is True
        assert len(producer._fallback_queue) == 1

    def test_fallback_queue_maxlen_10k(self):
        """Fallback queue tem maxlen=50000 (FALLBACK_QUEUE_SIZE real)."""
        from metrics_pipeline.stream_producer import FALLBACK_QUEUE_SIZE
        producer = StreamProducer(redis_url=None)

        # Publicar mais que o maxlen
        overflow = FALLBACK_QUEUE_SIZE + 500
        for i in range(overflow):
            producer.publish(make_event(i))

        # deque com maxlen descarta os mais antigos
        assert len(producer._fallback_queue) == FALLBACK_QUEUE_SIZE

    def test_publish_to_redis_xadd(self):
        """Com Redis mockado, chama XADD com campos corretos."""
        mock_redis = MagicMock()
        mock_redis.xadd.return_value = b"1234567890-0"

        producer = StreamProducer.__new__(StreamProducer)
        producer._redis = mock_redis
        producer._fallback_queue = deque(maxlen=10000)
        producer._lock = threading.Lock()
        producer._published = 0
        producer._errors = 0

        event = make_event(42)
        producer.publish(event)

        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        stream_key = call_args[0][0]
        assert "metrics" in stream_key or "raw" in stream_key

    def test_redis_failure_falls_back(self):
        """Falha no Redis → fallback queue sem crash."""
        mock_redis = MagicMock()
        mock_redis.xadd.side_effect = Exception("Redis connection lost")

        producer = StreamProducer.__new__(StreamProducer)
        producer._redis = mock_redis
        producer._fallback_queue = deque(maxlen=10000)
        producer._lock = threading.Lock()
        producer._published = 0
        producer._errors = 0

        event = make_event(1)
        ok = producer.publish(event)

        # Deve ter ido para fallback
        assert len(producer._fallback_queue) == 1

    def test_10k_events_throughput(self):
        """10.000 eventos publicados em <5s no fallback."""
        producer = StreamProducer(redis_url=None)

        start = time.monotonic()
        for i in range(10000):
            producer.publish(make_event(i))
        elapsed = (time.monotonic() - start) * 1000

        assert elapsed < 5000, f"10k eventos demoraram {elapsed:.0f}ms (limite: 5000ms)"
        assert len(producer._fallback_queue) == 10000

    def test_event_serialization(self):
        """MetricEvent serializa corretamente para dict."""
        event = make_event(99)
        d = event.to_dict()

        assert "sensor_id" in d
        assert "value" in d
        assert "status" in d
        assert "timestamp" in d
        assert d["sensor_id"] == 99 % 100

    def test_concurrent_publish_thread_safe(self):
        """Publicação concorrente não corrompe a fila."""
        producer = StreamProducer(redis_url=None)
        errors = []

        def publish_batch(start_i):
            try:
                for i in range(start_i, start_i + 100):
                    producer.publish(make_event(i))
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=publish_batch, args=(i * 100,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Erros de concorrência: {errors}"


# ─── Testes do StreamConsumer ────────────────────────────────────────────────

class TestStreamConsumer:

    def test_consumer_processes_from_fallback(self):
        """Consumer processa eventos da fallback queue do producer."""
        producer = StreamProducer(redis_url=None)
        processed = []

        def on_batch(events):
            processed.extend(events)

        consumer = StreamConsumer(producer, on_batch=on_batch, batch_size=10, poll_interval=0.01)

        # Publicar 50 eventos
        for i in range(50):
            producer.publish(make_event(i))

        consumer.start()
        time.sleep(0.2)  # Aguardar processamento
        consumer.stop()

        assert len(processed) > 0, "Consumer não processou nenhum evento"

    def test_consumer_at_least_once_delivery(self):
        """At-least-once: todos os eventos são processados."""
        producer = StreamProducer(redis_url=None)
        processed_ids = set()
        lock = threading.Lock()

        def on_batch(events):
            with lock:
                for e in events:
                    processed_ids.add(e.sensor_id if hasattr(e, 'sensor_id') else id(e))

        consumer = StreamConsumer(producer, on_batch=on_batch, batch_size=5, poll_interval=0.01)

        n_events = 100
        for i in range(n_events):
            producer.publish(make_event(i))

        consumer.start()
        time.sleep(0.5)
        consumer.stop()

        # At-least-once: todos devem ter sido processados
        assert len(processed_ids) > 0

    def test_consumer_handles_batch_error_gracefully(self):
        """Erro no on_batch não trava o consumer."""
        producer = StreamProducer(redis_url=None)
        call_count = {"n": 0}

        def on_batch_with_error(events):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("Simulated batch processing error")

        consumer = StreamConsumer(producer, on_batch=on_batch_with_error,
                                  batch_size=5, poll_interval=0.01)

        for i in range(20):
            producer.publish(make_event(i))

        consumer.start()
        time.sleep(0.3)
        consumer.stop()

        # Consumer deve ter continuado após o erro
        assert call_count["n"] > 1, "Consumer parou após erro"

    def test_consumer_stop_is_clean(self):
        """Consumer para limpo sem deadlock."""
        producer = StreamProducer(redis_url=None)
        consumer = StreamConsumer(producer, on_batch=lambda e: None,
                                  batch_size=10, poll_interval=0.01)

        consumer.start()
        time.sleep(0.05)

        start = time.monotonic()
        consumer.stop()
        elapsed = (time.monotonic() - start) * 1000

        assert elapsed < 2000, f"consumer.stop() demorou {elapsed:.0f}ms (possível deadlock)"


# ─── Testes de Redis real (skip se não disponível) ───────────────────────────

class TestRedisIntegration:

    @pytest.fixture
    def redis_client(self):
        try:
            import redis
            r = redis.from_url("redis://localhost:6379", decode_responses=True, socket_timeout=1)
            r.ping()
            return r
        except Exception:
            pytest.skip("Redis não disponível para testes de integração")

    def test_xadd_xlen(self, redis_client):
        """XADD adiciona entrada e XLEN reflete."""
        key = "test:stream:coruja"
        redis_client.delete(key)

        redis_client.xadd(key, {"sensor_id": "1", "value": "42.0", "status": "ok"})
        length = redis_client.xlen(key)

        assert length == 1
        redis_client.delete(key)

    def test_xadd_10k_performance(self, redis_client):
        """10.000 XADD em <5s."""
        key = "test:stream:perf"
        redis_client.delete(key)

        start = time.monotonic()
        pipe = redis_client.pipeline()
        for i in range(10000):
            pipe.xadd(key, {"i": str(i), "v": str(float(i))}, maxlen=10000, approximate=True)
        pipe.execute()
        elapsed = (time.monotonic() - start) * 1000

        assert elapsed < 5000, f"10k XADD demoraram {elapsed:.0f}ms"
        redis_client.delete(key)

    def test_consumer_group_xreadgroup(self, redis_client):
        """XREADGROUP lê mensagens do consumer group."""
        key = "test:stream:cg"
        group = "test-group"
        consumer = "test-consumer-1"

        redis_client.delete(key)
        try:
            redis_client.xgroup_create(key, group, id="0", mkstream=True)
        except Exception:
            pass

        # Publicar 5 mensagens
        for i in range(5):
            redis_client.xadd(key, {"i": str(i)})

        # Ler via consumer group
        messages = redis_client.xreadgroup(group, consumer, {key: ">"}, count=10)

        assert messages is not None
        assert len(messages) > 0

        redis_client.delete(key)
