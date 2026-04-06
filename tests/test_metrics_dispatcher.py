"""
Tests for Task 3: MetricsDispatcher — Despacho de Métricas (Requisitos 4, 8, 10, 11)
Validates thread-safe buffering, batch dispatch, flush, stats, and zero metric loss.

**Validates: Requirements 4, 8, 10, 11**
"""
import threading
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from probe.parallel_engine import MetricsDispatcher

settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")


# ─── Strategies ──────────────────────────────────────────────────────────────

hostname_st = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_"),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip() and not s.startswith("-"))

sensor_type_st = st.sampled_from(["cpu", "memory", "disk", "network", "ping", "snmp", "temperature"])

value_st = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

status_st = st.sampled_from(["ok", "warning", "critical"])


@st.composite
def metric_st(draw):
    """Generate a single metric dict matching the expected format."""
    return {
        "hostname": draw(hostname_st),
        "sensor_type": draw(sensor_type_st),
        "name": draw(st.text(min_size=1, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz_ ")),
        "value": draw(value_st),
        "unit": draw(st.sampled_from(["%", "GB", "ms", "status", None])),
        "status": draw(status_st),
        "timestamp": datetime.now().isoformat(),
        "metadata": {},
    }


def metrics_list_st(min_size=1, max_size=200):
    return st.lists(metric_st(), min_size=min_size, max_size=max_size)


# ─── Helper: mock httpx to capture sent payloads ────────────────────────────

class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code


class FakeHttpxClient:
    """Captures all POST calls for assertion."""

    def __init__(self, status_code=200):
        self.calls = []
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def post(self, url, json=None):
        self.calls.append({"url": url, "json": json})
        return FakeResponse(self.status_code)


# ─── Unit Tests ──────────────────────────────────────────────────────────────

class TestMetricsDispatcherUnit:
    """Unit tests for MetricsDispatcher basic behavior."""

    def test_init_creates_lock_and_empty_buffer(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123", batch_size=10)
        assert isinstance(d._lock, type(threading.Lock()))
        assert d._buffer == []
        assert d._sent_count == 0
        assert d._error_count == 0

    def test_enqueue_adds_to_buffer(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123", batch_size=9999)
        metrics = [{"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"}]

        # Patch _flush to prevent actual HTTP call
        with patch.object(d, "_flush"):
            d.enqueue(metrics)

        assert len(d._buffer) == 1

    def test_enqueue_triggers_flush_at_batch_size(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123", batch_size=2)
        metrics = [
            {"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"},
            {"hostname": "srv-02", "name": "RAM", "value": 70, "status": "ok", "timestamp": "2025-01-01T00:00:00"},
        ]

        fake_client = FakeHttpxClient()
        with patch("httpx.Client", return_value=fake_client):
            d.enqueue(metrics)

        # Buffer should be cleared after flush
        assert len(d._buffer) == 0
        assert d._sent_count == 2

    def test_flush_sends_remaining_metrics(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123", batch_size=9999)
        metrics = [{"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"}]
        d._buffer.extend(metrics)

        fake_client = FakeHttpxClient()
        with patch("httpx.Client", return_value=fake_client):
            d.flush()

        assert len(d._buffer) == 0
        assert d._sent_count == 1

    def test_flush_empty_buffer_is_noop(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123")
        fake_client = FakeHttpxClient()
        with patch("httpx.Client", return_value=fake_client):
            d.flush()

        assert len(fake_client.calls) == 0
        assert d._sent_count == 0

    def test_stats_property(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123")
        d._sent_count = 42
        d._error_count = 3
        d._buffer = [{"a": 1}, {"b": 2}]

        stats = d.stats
        assert stats == {"sent": 42, "errors": 3, "buffered": 2}

    def test_error_count_incremented_on_http_failure(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123", batch_size=1)
        metrics = [{"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"}]

        fake_client = FakeHttpxClient(status_code=500)
        with patch("httpx.Client", return_value=fake_client):
            d.enqueue(metrics)

        assert d._error_count == 1
        assert d._sent_count == 0

    def test_error_count_incremented_on_exception(self):
        d = MetricsDispatcher("http://localhost:8000", "token-123", batch_size=1)
        metrics = [{"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"}]

        with patch("httpx.Client", side_effect=Exception("connection refused")):
            d.enqueue(metrics)

        assert d._error_count == 1
        assert d._sent_count == 0

    def test_flush_preserves_probe_token(self):
        d = MetricsDispatcher("http://localhost:8000", "my-secret-token", batch_size=9999)
        d._buffer = [{"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"}]

        fake_client = FakeHttpxClient()
        with patch("httpx.Client", return_value=fake_client):
            d.flush()

        assert len(fake_client.calls) == 1
        assert fake_client.calls[0]["json"]["probe_token"] == "my-secret-token"

    def test_flush_sends_to_correct_endpoint(self):
        d = MetricsDispatcher("http://192.168.1.100:8000", "token", batch_size=9999)
        d._buffer = [{"hostname": "srv-01", "name": "CPU", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"}]

        fake_client = FakeHttpxClient()
        with patch("httpx.Client", return_value=fake_client):
            d.flush()

        assert fake_client.calls[0]["url"] == "http://192.168.1.100:8000/api/v1/metrics/probe/bulk"


# ─── Property-Based Test: No Metric Loss ────────────────────────────────────

class TestDispatcherNoMetricLoss:
    """
    Property: all metrics enqueued are sent after flush — zero metric loss.
    Enqueue N metrics across M threads, then flush. Total sent must equal total enqueued.

    **Validates: Requirements 4, 8**
    """

    @given(
        metrics_batches=st.lists(
            metrics_list_st(min_size=1, max_size=30),
            min_size=1,
            max_size=20,
        ),
        batch_size=st.integers(min_value=1, max_value=100),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def test_dispatcher_no_metric_loss(self, metrics_batches, batch_size):
        """
        Todas as métricas enfileiradas são enviadas após flush (sem perda).

        **Validates: Requirements 4, 8**
        """
        total_enqueued = sum(len(batch) for batch in metrics_batches)
        all_sent_metrics = []

        fake_client = FakeHttpxClient()

        dispatcher = MetricsDispatcher(
            api_url="http://test:8000",
            probe_token="test-token",
            batch_size=batch_size,
        )

        with patch("httpx.Client", return_value=fake_client):
            # Enqueue from multiple threads concurrently
            barrier = threading.Barrier(len(metrics_batches))
            errors_in_threads = []

            def worker(batch):
                try:
                    barrier.wait(timeout=5)
                    dispatcher.enqueue(batch)
                except Exception as e:
                    errors_in_threads.append(str(e))

            threads = [threading.Thread(target=worker, args=(batch,)) for batch in metrics_batches]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=10)

            # Flush remaining
            dispatcher.flush()

        # No thread errors
        assert not errors_in_threads, f"Thread errors: {errors_in_threads}"

        # Collect all metrics sent across all POST calls
        for call in fake_client.calls:
            payload = call["json"]
            assert "probe_token" in payload
            assert payload["probe_token"] == "test-token"
            all_sent_metrics.extend(payload["metrics"])

        # Core property: no metric loss
        assert len(all_sent_metrics) == total_enqueued, (
            f"Metric loss detected: enqueued={total_enqueued}, sent={len(all_sent_metrics)}"
        )

        # Stats should reflect the same count
        stats = dispatcher.stats
        assert stats["sent"] == total_enqueued
        assert stats["errors"] == 0
        assert stats["buffered"] == 0
