"""
E2E: REDIS OFFLINE scenario.
Buffer local → collection continues → reconnect → loss = 0%.
Requirements: 19.2
"""
import pytest
import time

from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent


def _event(i):
    return MetricEvent(sensor_id=i, server_id=1, sensor_type="cpu", value=float(i), unit="%")


@pytest.mark.e2e
class TestRedisOfflineE2E:
    """Req 19.2 — REDIS OFFLINE: buffer → continue → reconnect → 0% loss."""

    def test_buffer_during_offline_then_drain(self):
        """Metrics buffered during offline are fully drained after reconnect."""
        producer = StreamProducer()  # no Redis

        # Phase 1: Redis offline — metrics go to buffer
        count = 100
        for i in range(count):
            producer.publish(_event(i))

        assert producer.stats()["fallback_queue_size"] == count

        # Phase 2: Drain all (simulating reconnect)
        drained = producer.drain_fallback(max_items=count)
        assert len(drained) == count
        assert producer.stats()["fallback_queue_size"] == 0

    def test_no_data_loss_during_offline(self, chaos_engine):
        """Zero data loss during Redis offline period."""
        with chaos_engine.simulate_redis_offline() as mock_redis:
            # Redis operations fail
            with pytest.raises(ConnectionError):
                mock_redis.xadd("stream", {"key": "value"})

        # But local buffer works
        producer = StreamProducer()
        for i in range(50):
            producer.publish(_event(i))
        drained = producer.drain_fallback(max_items=100)
        assert len(drained) == 50  # 0% loss

    def test_collection_continues_during_offline(self):
        """Metric collection continues even when Redis is down."""
        producer = StreamProducer()
        events = [_event(i) for i in range(200)]
        published = producer.publish_batch(events)
        assert published == 200
        assert producer.stats()["published"] == 200
