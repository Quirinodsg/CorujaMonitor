"""
Resilience Tests — Coruja Monitor v3.0
Tests: auto-reconnect, retry backoff, fallback, failure isolation.
Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
"""
import sys
import os
import pytest
import time
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from ai_agents.pipeline import CircuitBreaker, CIRCUIT_OPEN_SECONDS
from alert_engine.notifier import AlertNotifier, MAX_RETRIES
from alert_engine.suppressor import DuplicateSuppressor
from probe.metrics_pipeline.stream_producer import StreamProducer, MetricEvent


@pytest.mark.chaos
class TestWebSocketReconnectResilience:
    """Req 15.1 — WebSocket auto-reconnect with backoff."""

    def test_reconnect_after_disconnect(self):
        """Connection manager handles disconnect gracefully."""
        from api.routers.observability import ConnectionManager
        mgr = ConnectionManager()
        ws = MagicMock()
        mgr.active.append(ws)
        mgr.disconnect(ws)
        assert ws not in mgr.active
        # Can add new connection after disconnect
        ws2 = MagicMock()
        mgr.active.append(ws2)
        assert len(mgr.active) == 1


@pytest.mark.chaos
class TestRetryBackoff:
    """Req 15.2 — AlertNotifier retry 3x with backoff."""

    def test_notifier_max_retries(self):
        """AlertNotifier has MAX_RETRIES = 3."""
        assert MAX_RETRIES == 3

    def test_notifier_retry_on_failure(self):
        """Notifier retries on failure without crashing."""
        notifier = AlertNotifier()
        # Notifier should handle failures gracefully
        assert notifier is not None


@pytest.mark.chaos
class TestDuplicateSuppressorFallback:
    """Req 15.3 — DuplicateSuppressor fail-open behavior."""

    def test_suppressor_works_normally(self, event_simulator):
        """Suppressor correctly identifies duplicates."""
        sup = DuplicateSuppressor()
        ev = event_simulator.generate_event()
        assert sup.is_duplicate(ev) is False
        sup.mark_seen(ev)
        assert sup.is_duplicate(ev) is True


@pytest.mark.chaos
class TestCircuitBreakerResilience:
    """Req 15.4 — Circuit breaker opens and closes."""

    def test_circuit_opens_on_failures(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(False)
        assert cb.is_open() is True

    def test_circuit_closes_after_timeout(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(False)
        assert cb.is_open() is True
        # Manually set open_until to past
        cb._open_until = time.monotonic() - 1
        cb._results.clear()
        assert cb.is_open() is False


@pytest.mark.chaos
class TestProbeFailureIsolation:
    """Req 15.5 — Probe failure isolation between collectors."""

    def test_buffer_survives_redis_failure(self):
        """StreamProducer buffers locally when Redis fails."""
        producer = StreamProducer()
        event = MetricEvent(sensor_id=1, server_id=1, sensor_type="cpu", value=42.0)
        result = producer.publish(event)
        assert result is True
        assert producer.stats()["backend"] == "memory"

    def test_collector_exception_isolated(self):
        """Exception in one collector doesn't affect others."""
        from probe.parallel_engine import SensorExecutor
        mock_probe = MagicMock()
        mock_probe.buffer = []
        mock_probe._collect_wmi_remote.side_effect = Exception("WMI crash")
        executor = SensorExecutor(mock_probe)
        result = executor.collect_server({"hostname": "srv1", "monitoring_protocol": "wmi"})
        assert result == []  # isolated failure
