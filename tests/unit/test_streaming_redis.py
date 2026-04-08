"""
Testes unitários do Streaming Redis — tests/unit/
Testa StreamProducer, StreamConsumer e MockRedisStream.

Requisitos: 4.1, 4.2, 4.3, 4.4, 4.5
"""
import pytest

from probe.metrics_pipeline.stream_producer import (
    StreamProducer,
    MetricEvent,
    STREAM_KEY,
    FALLBACK_QUEUE_SIZE,
)
from probe.metrics_pipeline.stream_consumer import (
    StreamConsumer,
    BATCH_SIZE,
    CONSUMER_GROUP,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _event(sensor_id=1, value=42.0):
    return MetricEvent(
        sensor_id=sensor_id,
        server_id=1,
        sensor_type="cpu",
        value=value,
        unit="%",
        status="ok",
    )


# ---------------------------------------------------------------------------
# XADD batch 500
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestXADDBatch:
    """Validates: Requirements 4.1"""

    def test_batch_publish_500_via_redis(self, mock_redis):
        """publish_batch with 500 events persists all to stream."""
        producer = StreamProducer()
        producer._redis = mock_redis

        events = [_event(sensor_id=i, value=float(i)) for i in range(500)]
        count = producer.publish_batch(events)

        assert count == 500
        assert mock_redis.xlen(STREAM_KEY) == 500

    def test_batch_publish_exceeding_500(self, mock_redis):
        """publish_batch with >500 events still persists all."""
        producer = StreamProducer()
        producer._redis = mock_redis

        events = [_event(sensor_id=i) for i in range(600)]
        count = producer.publish_batch(events)

        assert count == 600
        assert mock_redis.xlen(STREAM_KEY) == 600

    def test_batch_publish_empty_list(self, mock_redis):
        producer = StreamProducer()
        producer._redis = mock_redis
        assert producer.publish_batch([]) == 0

    def test_single_publish_via_redis(self, mock_redis):
        producer = StreamProducer()
        producer._redis = mock_redis

        result = producer.publish(_event())
        assert result is True
        assert mock_redis.xlen(STREAM_KEY) == 1

    def test_batch_size_constant_is_500(self):
        assert BATCH_SIZE == 500


# ---------------------------------------------------------------------------
# XREADGROUP consumer groups
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestXREADGROUP:
    """Validates: Requirements 4.2"""

    def test_consumer_reads_published_messages(self, mock_redis):
        """Consumer group reads messages published by producer."""
        # Publish messages
        for i in range(5):
            mock_redis.xadd(STREAM_KEY, {"sensor_id": str(i), "value": str(float(i))})

        # Create consumer group and read
        mock_redis.xgroup_create(STREAM_KEY, "test-group", id="0", mkstream=True)
        messages = mock_redis.xreadgroup(
            "test-group", "consumer-1", {STREAM_KEY: ">"}, count=10
        )

        assert len(messages) == 1  # one stream
        stream_name, entries = messages[0]
        assert len(entries) == 5

    def test_consumer_group_tracks_offset(self, mock_redis):
        """After reading, subsequent read returns no new messages."""
        for i in range(3):
            mock_redis.xadd(STREAM_KEY, {"value": str(i)})

        mock_redis.xgroup_create(STREAM_KEY, "grp", id="0", mkstream=True)
        first = mock_redis.xreadgroup("grp", "c1", {STREAM_KEY: ">"}, count=10)
        second = mock_redis.xreadgroup("grp", "c1", {STREAM_KEY: ">"}, count=10)

        assert len(first) == 1
        assert len(first[0][1]) == 3
        assert len(second) == 0  # no new messages


# ---------------------------------------------------------------------------
# At-least-once delivery (no XACK = reprocessing)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAtLeastOnce:
    """Validates: Requirements 4.3"""

    def test_unacked_messages_tracked_as_pending(self, mock_redis):
        """Messages read but not ACKed remain in pending list."""
        mock_redis.xadd(STREAM_KEY, {"data": "msg1"})
        mock_redis.xadd(STREAM_KEY, {"data": "msg2"})

        mock_redis.xgroup_create(STREAM_KEY, "grp", id="0", mkstream=True)
        messages = mock_redis.xreadgroup("grp", "c1", {STREAM_KEY: ">"}, count=10)

        # Pending list should have 2 messages
        pending = mock_redis._pending[STREAM_KEY]["grp"]
        assert len(pending) == 2

    def test_xack_removes_from_pending(self, mock_redis):
        """XACK removes messages from pending list."""
        msg_id = mock_redis.xadd(STREAM_KEY, {"data": "msg1"})
        mock_redis.xgroup_create(STREAM_KEY, "grp", id="0", mkstream=True)
        mock_redis.xreadgroup("grp", "c1", {STREAM_KEY: ">"}, count=10)

        acked = mock_redis.xack(STREAM_KEY, "grp", msg_id)
        assert acked == 1
        assert len(mock_redis._pending[STREAM_KEY]["grp"]) == 0

    def test_consumer_acks_after_processing(self, mock_redis):
        """StreamConsumer ACKs messages after on_batch callback."""
        producer = StreamProducer()
        producer._redis = mock_redis

        for i in range(3):
            producer.publish(_event(sensor_id=i))

        processed = []

        def on_batch(events):
            processed.extend(events)

        consumer = StreamConsumer(producer, on_batch=on_batch, batch_size=10)
        # Manually trigger redis consumption
        consumer._consume_redis()

        assert len(processed) == 3
        # After processing, pending should be empty (ACKed)
        pending = mock_redis._pending[STREAM_KEY].get(CONSUMER_GROUP, [])
        assert len(pending) == 0


# ---------------------------------------------------------------------------
# Buffer offline (deque 10k)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBufferOffline:
    """Validates: Requirements 4.4"""

    def test_publish_without_redis_uses_fallback(self):
        producer = StreamProducer()  # no redis
        result = producer.publish(_event())
        assert result is True
        assert producer.stats()["fallback_queue_size"] == 1
        assert producer.stats()["backend"] == "memory"

    def test_fallback_stores_multiple_events(self):
        producer = StreamProducer()
        for i in range(100):
            producer.publish(_event(sensor_id=i))
        assert producer.stats()["fallback_queue_size"] == 100

    def test_fallback_queue_maxlen_constant(self):
        assert FALLBACK_QUEUE_SIZE == 50_000

    def test_batch_publish_fallback_when_no_redis(self):
        producer = StreamProducer()
        events = [_event(sensor_id=i) for i in range(50)]
        count = producer.publish_batch(events)
        assert count == 50
        assert producer.stats()["fallback_queue_size"] == 50

    def test_drain_fallback_returns_events(self):
        producer = StreamProducer()
        for i in range(10):
            producer.publish(_event(sensor_id=i))

        drained = producer.drain_fallback(5)
        assert len(drained) == 5
        assert producer.stats()["fallback_queue_size"] == 5

    def test_drain_fallback_fifo_order(self):
        producer = StreamProducer()
        for i in range(5):
            producer.publish(_event(sensor_id=i, value=float(i)))

        drained = producer.drain_fallback(5)
        values = [e.value for e in drained]
        assert values == [0.0, 1.0, 2.0, 3.0, 4.0]


# ---------------------------------------------------------------------------
# Reconnection and buffer drain
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestReconnectionDrain:
    """Validates: Requirements 4.5"""

    def test_fallback_then_redis_drain(self, mock_redis):
        """Events buffered offline can be drained and sent to Redis."""
        producer = StreamProducer()  # no redis initially

        # Buffer events offline
        for i in range(20):
            producer.publish(_event(sensor_id=i))
        assert producer.stats()["fallback_queue_size"] == 20

        # "Reconnect" — attach redis
        producer._redis = mock_redis

        # Drain fallback and publish to redis
        drained = producer.drain_fallback(20)
        count = producer.publish_batch(drained)

        assert count == 20
        assert mock_redis.xlen(STREAM_KEY) == 20
        assert producer.stats()["fallback_queue_size"] == 0

    def test_partial_drain_leaves_remainder(self):
        producer = StreamProducer()
        for i in range(100):
            producer.publish(_event(sensor_id=i))

        drained = producer.drain_fallback(30)
        assert len(drained) == 30
        assert producer.stats()["fallback_queue_size"] == 70

    def test_redis_failure_falls_back_to_memory(self, mock_redis):
        """When Redis publish fails, events go to fallback queue."""
        producer = StreamProducer()

        # Simulate broken redis that raises on xadd
        class BrokenRedis:
            def xadd(self, *args, **kwargs):
                raise ConnectionError("Redis offline")
            def pipeline(self, **kwargs):
                raise ConnectionError("Redis offline")

        producer._redis = BrokenRedis()
        result = producer.publish(_event())

        # Should fall back to memory
        assert result is False
        assert producer.stats()["fallback_queue_size"] == 1


# ---------------------------------------------------------------------------
# Pipeline mock
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRedisPipeline:
    """Test pipeline batch operations via mock_redis."""

    def test_pipeline_xadd_batch(self, mock_redis):
        pipe = mock_redis.pipeline()
        for i in range(10):
            pipe.xadd(STREAM_KEY, {"value": str(i)})
        results = pipe.execute()

        assert len(results) == 10
        assert mock_redis.xlen(STREAM_KEY) == 10

    def test_pipeline_context_manager(self, mock_redis):
        with mock_redis.pipeline() as pipe:
            pipe.xadd(STREAM_KEY, {"data": "test"})
            results = pipe.execute()
        assert len(results) == 1
