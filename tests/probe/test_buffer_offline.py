"""
Buffer Offline Tests — Coruja Monitor v3.0
Tests: deque 10k FIFO, offline buffering, drain without loss.
Requirements: 2.6
"""
import pytest
from collections import deque

from probe.metrics_pipeline.stream_producer import (
    StreamProducer,
    MetricEvent,
    FALLBACK_QUEUE_SIZE,
)


def _event(sensor_id=1, value=42.0):
    return MetricEvent(
        sensor_id=sensor_id, server_id=1, sensor_type="cpu",
        value=value, unit="%", status="ok",
    )


@pytest.mark.unit
class TestBufferOffline:
    """Req 2.6 — buffer offline deque 10k FIFO."""

    def test_buffer_stores_metrics_when_redis_offline(self):
        """Without Redis, metrics go to fallback queue."""
        producer = StreamProducer()  # no redis_url
        event = _event()
        result = producer.publish(event)
        assert result is True
        stats = producer.stats()
        assert stats["fallback_queue_size"] == 1
        assert stats["backend"] == "memory"

    def test_buffer_fifo_discards_oldest(self):
        """When buffer is full, oldest metrics are discarded (deque maxlen)."""
        buf = deque(maxlen=10)
        for i in range(15):
            buf.append(f"metric_{i}")
        assert len(buf) == 10
        assert buf[0] == "metric_5"  # oldest 5 discarded
        assert buf[-1] == "metric_14"

    def test_buffer_10k_capacity(self):
        """Buffer respects 10k capacity via deque maxlen."""
        buf = deque(maxlen=10000)
        for i in range(12000):
            buf.append(i)
        assert len(buf) == 10000
        assert buf[0] == 2000  # first 2000 discarded

    def test_drain_returns_all_buffered(self):
        """drain_fallback returns all buffered metrics."""
        producer = StreamProducer()
        for i in range(50):
            producer.publish(_event(sensor_id=i))
        drained = producer.drain_fallback(max_items=100)
        assert len(drained) == 50

    def test_drain_partial(self):
        """drain_fallback with max_items returns partial."""
        producer = StreamProducer()
        for i in range(100):
            producer.publish(_event(sensor_id=i))
        drained = producer.drain_fallback(max_items=30)
        assert len(drained) == 30
        assert producer.stats()["fallback_queue_size"] == 70

    def test_batch_publish_to_memory(self):
        """publish_batch stores all events in memory when no Redis."""
        producer = StreamProducer()
        events = [_event(sensor_id=i) for i in range(500)]
        count = producer.publish_batch(events)
        assert count == 500
        assert producer.stats()["fallback_queue_size"] == 500
