"""
AI: Circuit Breaker Tests — Coruja Monitor v3.0
Tests: open/close behavior based on failure rate.
Requirements: 6.6
"""
import pytest
import time

from ai_agents.pipeline import CircuitBreaker, CIRCUIT_BREAKER_WINDOW, CIRCUIT_BREAKER_THRESHOLD


@pytest.mark.ai
class TestCircuitBreaker:
    """Req 6.6 — circuit breaker opens on >50% failures."""

    def test_initially_closed(self):
        cb = CircuitBreaker()
        assert cb.is_open() is False

    def test_opens_on_high_failure_rate(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(False)  # all failures
        assert cb.is_open() is True

    def test_stays_closed_on_low_failure_rate(self):
        cb = CircuitBreaker(window=10)
        for _ in range(8):
            cb.record(True)
        for _ in range(2):
            cb.record(False)
        assert cb.is_open() is False

    def test_reset_clears_state(self):
        cb = CircuitBreaker(window=10)
        for _ in range(10):
            cb.record(False)
        assert cb.is_open() is True
        cb.reset()
        assert cb.is_open() is False

    def test_not_enough_samples_stays_closed(self):
        cb = CircuitBreaker(window=10)
        for _ in range(5):
            cb.record(False)
        # Less than window size — stays closed
        assert cb.is_open() is False
