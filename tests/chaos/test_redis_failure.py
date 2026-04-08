"""
Chaos: Redis Failure Tests — Coruja Monitor v3.0
Tests: Redis offline simulation via ChaosEngine.
Requirements: 14.1
"""
import pytest

from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent


@pytest.mark.chaos
class TestRedisFailure:
    """Req 14.1 — Redis offline: buffer activates, no data loss."""

    def test_redis_offline_buffer_activates(self, chaos_engine):
        """When Redis is offline, operations raise ConnectionError."""
        with chaos_engine.simulate_redis_offline() as mock_redis:
            with pytest.raises(ConnectionError):
                mock_redis.xadd("stream", {"key": "val"})
            with pytest.raises(ConnectionError):
                mock_redis.ping()

    def test_producer_falls_back_to_memory(self):
        """StreamProducer uses memory buffer when Redis unavailable."""
        producer = StreamProducer()
        event = MetricEvent(sensor_id=1, server_id=1, sensor_type="cpu", value=42.0)
        result = producer.publish(event)
        assert result is True
        assert producer.stats()["backend"] == "memory"

    def test_redis_reconnect_simulation(self, chaos_engine):
        """Redis reconnect: offline then online after delay."""
        import time
        with chaos_engine.simulate_redis_reconnect(offline_seconds=0.1) as ctx:
            mock_redis = ctx["redis"]
            # Initially offline
            with pytest.raises(ConnectionError):
                mock_redis.ping()
            # Wait for reconnect
            time.sleep(0.2)
            assert mock_redis.ping() is True
