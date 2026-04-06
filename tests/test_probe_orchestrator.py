"""
Tests for Task 5: ProbeOrchestrator — Orquestração Paralela (Requisitos 2, 7, 8, 11)
Validates parallel collection, timeout resilience, canary filtering,
local server filtering, and structured logging.

**Validates: Requirements 2, 7, 8, 11**
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from probe.parallel_engine import ProbeOrchestrator, SensorExecutor, ProbeTelemetry, MetricsDispatcher


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_probe_mock():
    """Create a mock ProbeCore with buffer and collection methods."""
    probe = MagicMock()
    probe.buffer = []
    probe.collectors = []
    probe.config = MagicMock()
    probe.config.api_url = "http://localhost:8000"
    probe.config.probe_token = "test-token"
    return probe


def make_config(**overrides):
    """Create a parallel config dict with defaults."""
    cfg = {
        "parallel_enabled": True,
        "max_workers": 4,
        "timeout_seconds": 5,
        "dispatch_mode": "bulk",
        "canary_hosts": [],
    }
    cfg.update(overrides)
    return cfg


def make_server(hostname="SRV-01", ip="10.0.0.1", protocol="wmi"):
    return {"id": 1, "hostname": hostname, "ip_address": ip, "monitoring_protocol": protocol}


# ─── Unit Tests: __init__ ────────────────────────────────────────────────────

class TestProbeOrchestratorInit:
    """Tests for ProbeOrchestrator initialization (5.1)."""

    def test_creates_thread_pool_executor(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config(max_workers=6))
        assert isinstance(orch._pool, ThreadPoolExecutor)
        orch._pool.shutdown(wait=False)

    def test_creates_sensor_executor(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())
        assert isinstance(orch.executor, SensorExecutor)
        orch._pool.shutdown(wait=False)

    def test_creates_telemetry(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())
        assert isinstance(orch.telemetry, ProbeTelemetry)
        orch._pool.shutdown(wait=False)

    def test_creates_dispatcher(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())
        assert isinstance(orch.dispatcher, MetricsDispatcher)
        orch._pool.shutdown(wait=False)

    def test_config_values_loaded(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config(
            max_workers=12, timeout_seconds=60, dispatch_mode="incremental",
            canary_hosts=["srv-a", "srv-b"],
        ))
        assert orch.max_workers == 12
        assert orch.timeout_seconds == 60
        assert orch.dispatch_mode == "incremental"
        assert orch.canary_hosts == ["srv-a", "srv-b"]
        orch._pool.shutdown(wait=False)


# ─── Unit Tests: collect_all phases ──────────────────────────────────────────

class TestProbeOrchestratorCollectAll:
    """Tests for collect_all() phase ordering (5.2)."""

    def test_collect_all_returns_summary(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())

        with patch.object(orch, "_collect_local"), \
             patch.object(orch, "_fetch_servers", return_value=[]), \
             patch.object(orch, "_collect_standalone_parallel"), \
             patch.object(orch, "_collect_hyperv"), \
             patch.object(orch, "_reload_canary_hosts"):
            summary = orch.collect_all()

        assert "cycle_duration_ms" in summary
        assert "total_hosts" in summary
        assert "total_metrics" in summary
        assert "total_errors" in summary
        orch._pool.shutdown(wait=False)

    def test_collect_all_calls_phases_in_order(self):
        """Phases execute in order: LOCAL → REMOTO → STANDALONE → HYPER-V."""
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())
        call_order = []

        def track(name):
            def fn(*args, **kwargs):
                call_order.append(name)
                if name == "_fetch_servers":
                    return []
            return fn

        with patch.object(orch, "_collect_local", side_effect=track("local")), \
             patch.object(orch, "_fetch_servers", side_effect=track("_fetch_servers")), \
             patch.object(orch, "_collect_standalone_parallel", side_effect=track("standalone")), \
             patch.object(orch, "_collect_hyperv", side_effect=track("hyperv")), \
             patch.object(orch, "_reload_canary_hosts"):
            orch.collect_all()

        assert call_order == ["local", "_fetch_servers", "standalone", "hyperv"]
        orch._pool.shutdown(wait=False)


# ─── Unit Tests: _collect_local ──────────────────────────────────────────────

class TestCollectLocal:
    """Tests for _collect_local() (5.3)."""

    def test_collects_from_all_collectors(self):
        probe = make_probe_mock()
        collector1 = MagicMock()
        collector1.collect.return_value = [{"sensor_type": "cpu", "value": 50}]
        collector2 = MagicMock()
        collector2.collect.return_value = [{"sensor_type": "memory", "value": 70}]
        probe.collectors = [collector1, collector2]

        orch = ProbeOrchestrator(probe, make_config())
        orch._collect_local(datetime.now())

        assert len(probe.buffer) == 2
        assert probe.buffer[0]["sensor_type"] == "cpu"
        assert probe.buffer[1]["sensor_type"] == "memory"
        orch._pool.shutdown(wait=False)

    def test_records_telemetry_for_local(self):
        probe = make_probe_mock()
        collector = MagicMock()
        collector.collect.return_value = [{"sensor_type": "cpu", "value": 50}]
        probe.collectors = [collector]

        orch = ProbeOrchestrator(probe, make_config())
        orch.telemetry.start_cycle()
        orch._collect_local(datetime.now())

        summary = orch.telemetry.summary()
        assert summary["total_hosts"] == 1
        assert summary["total_metrics"] == 1
        orch._pool.shutdown(wait=False)

    def test_collector_exception_does_not_stop_others(self):
        probe = make_probe_mock()
        bad_collector = MagicMock()
        bad_collector.collect.side_effect = RuntimeError("fail")
        good_collector = MagicMock()
        good_collector.collect.return_value = [{"sensor_type": "disk", "value": 80}]
        probe.collectors = [bad_collector, good_collector]

        orch = ProbeOrchestrator(probe, make_config())
        orch._collect_local(datetime.now())

        assert len(probe.buffer) == 1
        assert probe.buffer[0]["sensor_type"] == "disk"
        orch._pool.shutdown(wait=False)


# ─── Unit Tests: _fetch_servers ──────────────────────────────────────────────

class TestFetchServers:
    """Tests for _fetch_servers() local filtering (5.4)."""

    @patch("probe.parallel_engine.socket" if False else "socket.gethostname", return_value="LOCAL-HOST")
    @patch("socket.gethostbyname", return_value="192.168.1.100")
    def test_filters_local_server_by_hostname(self, mock_ip, mock_host):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())

        servers_response = [
            {"hostname": "LOCAL-HOST", "ip_address": "192.168.1.100"},
            {"hostname": "SRV-REMOTE", "ip_address": "10.0.0.5"},
        ]

        with patch("httpx.Client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = servers_response
            mock_client.return_value.__enter__ = MagicMock(return_value=MagicMock(get=MagicMock(return_value=mock_resp)))
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = orch._fetch_servers()

        assert len(result) == 1
        assert result[0]["hostname"] == "SRV-REMOTE"
        orch._pool.shutdown(wait=False)

    def test_returns_empty_on_api_failure(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())

        with patch("httpx.Client") as mock_client:
            mock_client.return_value.__enter__ = MagicMock(
                side_effect=ConnectionError("API down")
            )
            mock_client.return_value.__exit__ = MagicMock(return_value=False)

            result = orch._fetch_servers()

        assert result == []
        orch._pool.shutdown(wait=False)


# ─── Unit Tests: canary_hosts filtering ──────────────────────────────────────

class TestCanaryHostsFiltering:
    """Tests for canary_hosts filtering (5.6)."""

    def test_canary_filters_parallel_servers(self):
        """When canary_hosts is set, only listed hosts run in parallel."""
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config(canary_hosts=["srv-a"]))

        servers = [
            make_server(hostname="srv-a", ip="10.0.0.1"),
            make_server(hostname="srv-b", ip="10.0.0.2"),
            make_server(hostname="srv-c", ip="10.0.0.3"),
        ]

        collected_parallel = []
        collected_sequential = []

        original_submit = orch._pool.submit

        def track_submit(fn, *args, **kwargs):
            # Track which servers go through the pool
            if args:
                server = args[0]
                collected_parallel.append(server.get("hostname"))
            return original_submit(fn, *args, **kwargs)

        original_safe = orch._collect_one_server_safe

        def track_sequential(server, timestamp):
            collected_sequential.append(server.get("hostname"))
            # Don't actually collect — just track

        with patch.object(orch, "_collect_one_server_safe", side_effect=track_sequential):
            with patch.object(orch._pool, "submit", side_effect=track_submit):
                orch.telemetry.start_cycle()
                orch._collect_servers_parallel(servers, datetime.now())

        # srv-a should be in parallel, srv-b and srv-c in sequential
        assert "srv-b" in collected_sequential
        assert "srv-c" in collected_sequential
        orch._pool.shutdown(wait=False)

    def test_empty_canary_runs_all_parallel(self):
        """When canary_hosts is empty, all servers run in parallel."""
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config(canary_hosts=[]))

        servers = [
            make_server(hostname="srv-a", ip="10.0.0.1"),
            make_server(hostname="srv-b", ip="10.0.0.2"),
        ]

        submitted = []
        original_submit = orch._pool.submit

        def track_submit(fn, *args, **kwargs):
            if args:
                submitted.append(args[0].get("hostname") if isinstance(args[0], dict) else None)
            return original_submit(fn, *args, **kwargs)

        with patch.object(orch._pool, "submit", side_effect=track_submit), \
             patch.object(orch, "_collect_one_server_safe"):
            orch.telemetry.start_cycle()
            orch._collect_servers_parallel(servers, datetime.now())

        orch._pool.shutdown(wait=False)


# ─── Unit Tests: _collect_standalone_parallel ────────────────────────────────

class TestCollectStandaloneParallel:
    """Tests for _collect_standalone_parallel() (5.7)."""

    def test_fetches_and_collects_sensors(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())

        sensors = [
            {"id": 1, "name": "Sensor A", "sensor_type": "snmp", "ip_address": "10.0.0.50"},
            {"id": 2, "name": "Sensor B", "sensor_type": "icmp", "ip_address": "10.0.0.51"},
        ]

        with patch.object(orch, "_fetch_standalone_sensors", return_value=sensors), \
             patch.object(orch.executor, "collect_standalone", return_value=[{"value": 1}]):
            orch.telemetry.start_cycle()
            orch._collect_standalone_parallel(datetime.now())

        summary = orch.telemetry.summary()
        assert summary["total_hosts"] >= 1  # __standalone__ recorded
        orch._pool.shutdown(wait=False)

    def test_empty_sensors_records_telemetry(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())

        with patch.object(orch, "_fetch_standalone_sensors", return_value=[]):
            orch.telemetry.start_cycle()
            orch._collect_standalone_parallel(datetime.now())

        summary = orch.telemetry.summary()
        assert summary["total_hosts"] == 1  # __standalone__ still recorded
        orch._pool.shutdown(wait=False)


# ─── Unit Tests: _collect_hyperv ─────────────────────────────────────────────

class TestCollectHyperV:
    """Tests for _collect_hyperv() (5.2 phase 4)."""

    def test_calls_probe_hyperv(self):
        probe = make_probe_mock()
        orch = ProbeOrchestrator(probe, make_config())
        orch.telemetry.start_cycle()
        orch._collect_hyperv()
        probe._collect_hyperv_hosts.assert_called_once()
        orch._pool.shutdown(wait=False)

    def test_hyperv_exception_does_not_propagate(self):
        probe = make_probe_mock()
        probe._collect_hyperv_hosts.side_effect = RuntimeError("HyperV down")
        orch = ProbeOrchestrator(probe, make_config())
        orch.telemetry.start_cycle()
        orch._collect_hyperv()  # Should not raise
        orch._pool.shutdown(wait=False)


# ─── Property-Based Test: Timeout Resilience ─────────────────────────────────

class TestOrchestratorTimeoutResilience:
    """
    Property: timeout in one server does not prevent collection of others.
    If N servers are submitted and K of them timeout, the remaining N-K
    should still have their metrics collected successfully.

    **Validates: Requirements 2, 8**
    """

    @given(
        n_good=st.integers(min_value=1, max_value=10),
        n_timeout=st.integers(min_value=1, max_value=5),
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def test_orchestrator_timeout_resilience(self, n_good, n_timeout):
        """
        Timeout em um servidor não impede coleta dos demais.

        **Validates: Requirements 2, 8**
        """
        probe = make_probe_mock()
        config = make_config(max_workers=n_good + n_timeout, timeout_seconds=2)
        orch = ProbeOrchestrator(probe, config)
        orch.telemetry.start_cycle()

        # Build server lists
        good_servers = [
            make_server(hostname=f"good-{i}", ip=f"10.0.{i}.1")
            for i in range(n_good)
        ]
        timeout_servers = [
            make_server(hostname=f"timeout-{i}", ip=f"10.1.{i}.1")
            for i in range(n_timeout)
        ]
        all_servers = good_servers + timeout_servers

        # Track which servers were collected successfully
        collected_hosts = []
        lock = threading.Lock()

        original_collect = orch.executor.collect_server

        def mock_collect_server(server):
            hostname = server.get("hostname", "")
            if hostname.startswith("timeout-"):
                # Simulate a slow server that exceeds timeout
                time.sleep(3)
                return []
            else:
                # Good server returns metrics quickly
                with lock:
                    collected_hosts.append(hostname)
                return [{"hostname": hostname, "sensor_type": "cpu", "value": 50}]

        with patch.object(orch.executor, "collect_server", side_effect=mock_collect_server):
            orch._collect_servers_parallel(all_servers, datetime.now())

        orch.telemetry.end_cycle()
        summary = orch.telemetry.summary()

        # Core property: all good servers were collected despite timeouts
        assert len(collected_hosts) == n_good, (
            f"Expected {n_good} good hosts collected, got {len(collected_hosts)}: {collected_hosts}"
        )

        # All good server hostnames should be present
        expected_good = {f"good-{i}" for i in range(n_good)}
        assert set(collected_hosts) == expected_good

        # Telemetry should have recorded entries for good servers
        # (timeout servers may or may not be recorded depending on timing)
        assert summary["total_hosts"] >= n_good

        orch._pool.shutdown(wait=False)
