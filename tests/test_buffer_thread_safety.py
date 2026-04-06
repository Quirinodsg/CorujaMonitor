"""
Tests for Task 9: Controle de Concorrência e Thread Safety (Requisito 8)
Validates thread-safe access to ProbeCore.buffer during parallel collection.

**Validates: Requirements 8**
"""
import threading
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from probe.parallel_engine import ProbeOrchestrator, SensorExecutor


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_probe_mock():
    """Create a mock ProbeCore with a real list buffer."""
    probe = MagicMock()
    probe.buffer = []
    probe.collectors = []
    probe.config = MagicMock()
    probe.config.api_url = "http://localhost:8000"
    probe.config.probe_token = "test-token"
    return probe


def make_config(**overrides):
    cfg = {
        "parallel_enabled": True,
        "max_workers": 4,
        "timeout_seconds": 5,
        "dispatch_mode": "bulk",
        "canary_hosts": [],
    }
    cfg.update(overrides)
    return cfg


# ─── Property-Based Test: Buffer Thread Safety ──────────────────────────────

class TestBufferThreadSafety:
    """
    Property: concurrent writes of N threads to the buffer, each writing
    metrics_per_thread metrics, result in exactly N * metrics_per_thread
    total metrics in the buffer.

    **Validates: Requirements 8**
    """

    @given(
        n_threads=st.integers(min_value=2, max_value=20),
        metrics_per_thread=st.integers(min_value=1, max_value=10),
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def test_buffer_thread_safety(self, n_threads, metrics_per_thread):
        """
        Escritas concorrentes de N threads no buffer resultam em
        exatamente N * metrics_per_thread métricas.

        **Validates: Requirements 8**
        """
        probe = make_probe_mock()

        # Configure mock WMI to append metrics_per_thread metrics per call
        def fake_wmi(server):
            for i in range(metrics_per_thread):
                probe.buffer.append({
                    "hostname": server.get("hostname", "unknown"),
                    "sensor_type": "cpu",
                    "name": f"metric-{i}",
                    "value": 50.0,
                    "unit": "%",
                    "status": "ok",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {},
                })

        probe._collect_wmi_remote.side_effect = fake_wmi

        # Create orchestrator with shared buffer lock
        orch = ProbeOrchestrator(probe, make_config(max_workers=n_threads))
        executor = orch.executor

        barrier = threading.Barrier(n_threads)
        errors_in_threads = []

        def worker(thread_idx):
            try:
                barrier.wait(timeout=10)
                server = {
                    "hostname": f"srv-{thread_idx}",
                    "ip_address": f"10.0.{thread_idx}.1",
                    "monitoring_protocol": "wmi",
                }
                executor.collect_server(server)
            except Exception as e:
                errors_in_threads.append(str(e))

        threads = [
            threading.Thread(target=worker, args=(i,))
            for i in range(n_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        # No thread errors
        assert not errors_in_threads, f"Thread errors: {errors_in_threads}"

        # Core property: no metric loss or duplication
        expected_total = n_threads * metrics_per_thread
        actual_total = len(probe.buffer)
        assert actual_total == expected_total, (
            f"Buffer thread safety violation: expected {expected_total} metrics "
            f"({n_threads} threads × {metrics_per_thread} each), got {actual_total}"
        )

        # Verify all thread hostnames are represented
        hostnames = {m["hostname"] for m in probe.buffer}
        expected_hostnames = {f"srv-{i}" for i in range(n_threads)}
        assert hostnames == expected_hostnames, (
            f"Missing hostnames: expected {expected_hostnames}, got {hostnames}"
        )

        orch._pool.shutdown(wait=False)
