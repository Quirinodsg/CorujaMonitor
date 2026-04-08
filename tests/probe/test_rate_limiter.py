"""
Rate Limiter Tests — Coruja Monitor v3.0
Tests: GlobalRateLimiter acquire/release/queue/reject.
Requirements: 2.5
"""
import pytest
import threading

from probe.engine.global_rate_limiter import GlobalRateLimiter


@pytest.mark.unit
class TestGlobalRateLimiter:
    """Req 2.5 — rate limiter global for concurrent sensors."""

    def test_acquire_and_release_slot(self):
        limiter = GlobalRateLimiter(max_running=10, queue_limit=100)
        with limiter.acquire_slot(sensor_id="cpu_host1"):
            assert limiter.global_active_sensors == 1
        assert limiter.global_active_sensors == 0

    def test_max_running_limit(self):
        limiter = GlobalRateLimiter(max_running=2, queue_limit=100)
        # Acquire 2 slots
        acquired1 = limiter._acquire("s1", timeout=1.0)
        acquired2 = limiter._acquire("s2", timeout=1.0)
        assert acquired1 is True
        assert acquired2 is True
        # Third should timeout (all slots taken)
        acquired3 = limiter._acquire("s3", timeout=0.1)
        assert acquired3 is False
        limiter._release("s1")
        limiter._release("s2")

    def test_metrics_report(self):
        limiter = GlobalRateLimiter(max_running=10, queue_limit=100)
        with limiter.acquire_slot(sensor_id="test"):
            m = limiter.metrics()
            assert m["global_active_sensors"] == 1
            assert m["max_running"] == 10

    def test_resize_increases_capacity(self):
        limiter = GlobalRateLimiter(max_running=5, queue_limit=100)
        limiter.resize(10)
        assert limiter.max_running == 10

    def test_slot_raises_on_timeout(self):
        limiter = GlobalRateLimiter(max_running=1, queue_limit=0)
        limiter._acquire("s1", timeout=1.0)
        with pytest.raises(RuntimeError, match="não foi possível"):
            with limiter.acquire_slot(sensor_id="s2", timeout=0.1):
                pass
        limiter._release("s1")

    def test_concurrent_slots(self):
        limiter = GlobalRateLimiter(max_running=5, queue_limit=100)
        results = []

        def worker(sensor_id):
            with limiter.acquire_slot(sensor_id=sensor_id):
                results.append(sensor_id)

        threads = [threading.Thread(target=worker, args=(f"s{i}",)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        assert len(results) == 5
