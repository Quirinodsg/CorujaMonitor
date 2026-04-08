"""
ProbeOrchestrator Tests — Coruja Monitor v3.0
Tests: parallel collection, failure isolation.
Requirements: 2.7
"""
import pytest
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from probe.parallel_engine import (
    ProbeOrchestrator,
    SensorExecutor,
    ProbeTelemetry,
    MetricsDispatcher,
    MetricsComparator,
)


@pytest.mark.unit
class TestProbeTelemetry:
    """Telemetry tracks cycle duration, host times, errors."""

    def test_telemetry_cycle(self):
        t = ProbeTelemetry()
        t.start_cycle()
        t.record_host("host1", 100.0, 5)
        t.record_host("host2", 200.0, 10, error="timeout")
        t.end_cycle()
        s = t.summary()
        assert s["total_hosts"] == 2
        assert s["total_metrics"] == 15
        assert s["total_errors"] == 1
        assert s["slowest_host"] == "host2"

    def test_telemetry_empty_cycle(self):
        t = ProbeTelemetry()
        t.start_cycle()
        t.end_cycle()
        s = t.summary()
        assert s["total_hosts"] == 0
        assert s["total_metrics"] == 0


@pytest.mark.unit
class TestMetricsComparator:
    """MCT shadow mode comparator."""

    def test_compare_within_tolerance(self):
        comp = MetricsComparator()
        result = comp.compare("host1", "cpu", 50.0, 51.0)
        assert result["status"] == "OK"

    def test_compare_drift_detected(self):
        comp = MetricsComparator()
        result = comp.compare("host1", "cpu", 50.0, 60.0)
        assert result["status"] == "DRIFT"

    def test_compare_zero_values(self):
        comp = MetricsComparator()
        result = comp.compare("host1", "cpu", 0.0, 0.0)
        assert result["status"] == "OK"
        assert result["diff_pct"] == 0.0

    def test_summary_all_ok(self):
        comp = MetricsComparator()
        comp.compare("h1", "cpu", 50.0, 51.0)
        comp.compare("h1", "mem", 70.0, 71.0)
        s = comp.summary
        assert s["pass"] is True
        assert s["drifts"] == 0


@pytest.mark.unit
class TestMetricsDispatcher:
    """Dispatcher enqueue and flush."""

    def test_enqueue_buffers_metrics(self):
        d = MetricsDispatcher(api_url="http://localhost", probe_token="test", batch_size=100)
        d.enqueue([{"hostname": "h1", "value": 42}])
        assert d.stats["buffered"] == 1

    def test_stats_initial(self):
        d = MetricsDispatcher(api_url="http://localhost", probe_token="test")
        s = d.stats
        assert s["sent"] == 0
        assert s["errors"] == 0


@pytest.mark.unit
class TestSensorExecutor:
    """SensorExecutor isolates failures between collectors."""

    def test_collect_server_isolates_failure(self):
        """Exception in one collector doesn't propagate."""
        mock_probe = MagicMock()
        mock_probe.buffer = []
        mock_probe._collect_wmi_remote.side_effect = Exception("WMI failed")
        executor = SensorExecutor(mock_probe)
        metrics = executor.collect_server({"hostname": "srv1", "monitoring_protocol": "wmi"})
        assert metrics == []  # failure isolated, returns empty

    def test_collect_server_returns_metrics(self):
        """Successful collection returns metrics from buffer."""
        mock_probe = MagicMock()
        mock_probe.buffer = []

        def fake_collect(server):
            mock_probe.buffer.append({"hostname": "srv1", "value": 42})

        mock_probe._collect_wmi_remote.side_effect = fake_collect
        executor = SensorExecutor(mock_probe)
        metrics = executor.collect_server({"hostname": "srv1", "monitoring_protocol": "wmi"})
        assert len(metrics) == 1
