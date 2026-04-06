"""
Tests for Task 2: ProbeTelemetry — Observabilidade (Requisitos 5, 8, 11)
Validates telemetry thread safety, cycle timing, and summary correctness.

**Validates: Requirements 5, 8, 11**
"""
import threading
import time

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from probe.parallel_engine import ProbeTelemetry

settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")

# ─── Strategies ──────────────────────────────────────────────────────────────

hostname_st = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_"),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip() and not s.startswith("-"))

duration_ms_st = st.floats(min_value=0.1, max_value=60000.0, allow_nan=False, allow_infinity=False)

metrics_count_st = st.integers(min_value=0, max_value=500)


# ─── Unit Tests ──────────────────────────────────────────────────────────────

class TestProbeTelemetryUnit:
    """Unit tests for ProbeTelemetry basic behavior."""

    def test_init_creates_lock(self):
        t = ProbeTelemetry()
        assert isinstance(t._lock, type(threading.Lock()))

    def test_start_cycle_clears_previous_data(self):
        t = ProbeTelemetry()
        t.record_host("host-a", 100.0, 5)
        t.start_cycle()
        summary = t.summary()
        assert summary["total_hosts"] == 0
        assert summary["total_metrics"] == 0
        assert summary["total_errors"] == 0

    def test_end_cycle_sets_end_time(self):
        t = ProbeTelemetry()
        t.start_cycle()
        time.sleep(0.01)
        t.end_cycle()
        assert t.cycle_duration_ms > 0

    def test_record_host_without_error(self):
        t = ProbeTelemetry()
        t.start_cycle()
        t.record_host("srv-01", 150.0, 10)
        summary = t.summary()
        assert summary["total_hosts"] == 1
        assert summary["total_metrics"] == 10
        assert summary["total_errors"] == 0
        assert summary["errors"] is None

    def test_record_host_with_error(self):
        t = ProbeTelemetry()
        t.start_cycle()
        t.record_host("srv-fail", 500.0, 0, error="WMI timeout")
        summary = t.summary()
        assert summary["total_errors"] == 1
        assert summary["errors"] == {"srv-fail": "WMI timeout"}

    def test_summary_identifies_slowest_host(self):
        t = ProbeTelemetry()
        t.start_cycle()
        t.record_host("fast-host", 50.0, 5)
        t.record_host("slow-host", 9000.0, 3)
        t.record_host("mid-host", 200.0, 7)
        summary = t.summary()
        assert summary["slowest_host"] == "slow-host"
        assert summary["slowest_ms"] == 9000.0

    def test_summary_empty_cycle(self):
        t = ProbeTelemetry()
        t.start_cycle()
        t.end_cycle()
        summary = t.summary()
        assert summary["total_hosts"] == 0
        assert summary["total_metrics"] == 0
        assert summary["slowest_host"] is None
        assert summary["slowest_ms"] == 0

    def test_cycle_duration_ms_calculation(self):
        t = ProbeTelemetry()
        t.start_cycle()
        time.sleep(0.05)
        t.end_cycle()
        # Should be at least 40ms (allowing some tolerance)
        assert t.cycle_duration_ms >= 40


# ─── Property-Based Test: Thread Safety ──────────────────────────────────────

class TestTelemetryThreadSafety:
    """
    Property: concurrent record_host calls from N threads must not lose data.
    total_hosts in summary must equal N (one unique host per thread).

    **Validates: Requirements 5, 8**
    """

    @given(
        n_threads=st.integers(min_value=2, max_value=50),
        base_duration=duration_ms_st,
        base_metrics=metrics_count_st,
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def test_telemetry_thread_safety(self, n_threads, base_duration, base_metrics):
        """
        Registros concorrentes de N threads não perdem dados (total_hosts == N).

        **Validates: Requirements 5, 8**
        """
        telemetry = ProbeTelemetry()
        telemetry.start_cycle()

        barrier = threading.Barrier(n_threads)
        errors_in_threads = []

        def worker(idx):
            try:
                barrier.wait(timeout=5)
                telemetry.record_host(
                    host=f"host-{idx}",
                    duration_ms=base_duration + idx,
                    metrics_count=base_metrics,
                    error=f"err-{idx}" if idx % 3 == 0 else None,
                )
            except Exception as e:
                errors_in_threads.append(str(e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for th in threads:
            th.start()
        for th in threads:
            th.join(timeout=10)

        telemetry.end_cycle()
        summary = telemetry.summary()

        # No thread errors
        assert not errors_in_threads, f"Thread errors: {errors_in_threads}"

        # Core property: no data loss
        assert summary["total_hosts"] == n_threads
        assert summary["total_metrics"] == base_metrics * n_threads

        # Error count matches threads where idx % 3 == 0
        expected_errors = sum(1 for i in range(n_threads) if i % 3 == 0)
        assert summary["total_errors"] == expected_errors

        # Slowest host should be the one with highest duration
        if n_threads > 0:
            expected_slowest = f"host-{n_threads - 1}"
            assert summary["slowest_host"] == expected_slowest

        # Cycle duration should be non-negative
        assert summary["cycle_duration_ms"] >= 0
