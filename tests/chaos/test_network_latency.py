"""
Chaos: Network Latency Tests — Coruja Monitor v3.0
Tests: simulated latency 100-500ms.
Requirements: 14.2
"""
import pytest
import time


@pytest.mark.chaos
class TestNetworkLatency:
    """Req 14.2 — network latency 100-500ms simulation."""

    def test_latency_within_range(self, chaos_engine):
        """Simulated latency falls within configured range."""
        with chaos_engine.simulate_network_latency(min_ms=100, max_ms=500) as ctx:
            latency = ctx["add_latency"]()
            assert 100 <= latency <= 500

    def test_latency_wrapper_adds_delay(self, chaos_engine):
        """Wrapped function has added latency."""
        with chaos_engine.simulate_network_latency(min_ms=50, max_ms=100) as ctx:
            def fast_fn():
                return "result"

            wrapped = ctx["wrap"](fast_fn)
            start = time.monotonic()
            result = wrapped()
            elapsed_ms = (time.monotonic() - start) * 1000
            assert result == "result"
            assert elapsed_ms >= 50

    def test_latency_calls_tracked(self, chaos_engine):
        """Latency calls are tracked in context."""
        with chaos_engine.simulate_network_latency(min_ms=10, max_ms=20) as ctx:
            # add_latency returns latency in ms and appends to calls list
            # But calls list is only populated by the wrap() function
            wrapped_fn = ctx["wrap"](lambda: "ok")
            wrapped_fn()
            wrapped_fn()
            assert len(ctx["calls"]) == 2
