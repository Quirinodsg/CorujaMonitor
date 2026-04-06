"""
Tests for Task 10: Testes de Integração e Compatibilidade (Requisitos 10, 12)
Validates that parallel mode metrics match sequential format, probe_token presence,
required fields, and metadata preservation.

**Validates: Requirements 10, 12**
"""
import threading
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from probe.parallel_engine import MetricsDispatcher, SensorExecutor, ProbeOrchestrator


# ─── Helpers ─────────────────────────────────────────────────────────────────

class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code


class CaptureHttpxClient:
    """Captures all POST payloads for assertion."""

    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def post(self, url, json=None):
        self.calls.append({"url": url, "json": json})
        return FakeResponse(200)


def make_probe_mock():
    probe = MagicMock()
    probe.buffer = []
    probe.collectors = []
    probe.config = MagicMock()
    probe.config.api_url = "http://localhost:8000"
    probe.config.probe_token = "test-token-abc"
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


# ─── 10.1: Parallel metrics have same JSON format as sequential ──────────────

class TestParallelMetricFormat:
    """
    10.1 — Métricas enviadas pelo modo paralelo têm o mesmo formato JSON
    do modo sequencial.

    **Validates: Requirements 10**
    """

    def test_parallel_dispatch_format_matches_sequential(self):
        """
        The MetricsDispatcher._flush() formats metrics identically to
        ProbeCore._send_metrics(): hostname, sensor_type, sensor_name,
        value, unit, status, timestamp, metadata.
        """
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="test-token",
            batch_size=9999,
        )

        # Simulate metrics as they appear in the buffer (raw format from collectors)
        dispatcher._buffer = [
            {
                "hostname": "SRV-WEB-01",
                "sensor_type": "cpu",
                "name": "CPU Usage",
                "value": 75.5,
                "unit": "%",
                "status": "ok",
                "timestamp": "2025-01-15T10:30:00",
                "metadata": {"ip_address": "10.0.0.1"},
            },
            {
                "hostname": "SRV-DB-01",
                "type": "memory",  # 'type' key (used by some collectors)
                "name": "Memory Usage",
                "value": 82.3,
                "unit": "%",
                "status": "warning",
                "timestamp": "2025-01-15T10:30:00",
                "metadata": {},
            },
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        assert len(capture.calls) == 1
        payload = capture.calls[0]["json"]

        # Validate top-level structure
        assert "probe_token" in payload
        assert "metrics" in payload
        assert isinstance(payload["metrics"], list)
        assert len(payload["metrics"]) == 2

        # Validate each metric has the sequential format fields
        sequential_fields = {
            "hostname", "sensor_type", "sensor_name",
            "value", "status", "timestamp", "metadata",
        }
        for m in payload["metrics"]:
            assert sequential_fields.issubset(set(m.keys())), (
                f"Missing fields: {sequential_fields - set(m.keys())}"
            )

        # First metric: sensor_type from 'sensor_type' key
        assert payload["metrics"][0]["sensor_type"] == "cpu"
        assert payload["metrics"][0]["sensor_name"] == "CPU Usage"

        # Second metric: sensor_type falls back to 'type' key
        assert payload["metrics"][1]["sensor_type"] == "memory"
        assert payload["metrics"][1]["sensor_name"] == "Memory Usage"


# ─── 10.2: probe_token present in all requests ──────────────────────────────

class TestProbeTokenPresence:
    """
    10.2 — probe_token está presente em todas as requisições.

    **Validates: Requirements 10**
    """

    def test_probe_token_in_single_flush(self):
        """probe_token is included in every flush POST."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="my-secret-token-123",
            batch_size=9999,
        )
        dispatcher._buffer = [
            {"hostname": "h1", "name": "cpu", "value": 50, "status": "ok", "timestamp": "2025-01-01T00:00:00"},
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        assert capture.calls[0]["json"]["probe_token"] == "my-secret-token-123"

    def test_probe_token_in_multiple_batches(self):
        """probe_token is present in every batch when batch_size triggers multiple flushes."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="batch-token-xyz",
            batch_size=1,
        )

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.enqueue([
                {"hostname": "h1", "name": "m1", "value": 1, "status": "ok", "timestamp": "2025-01-01T00:00:00"},
            ])
            dispatcher.enqueue([
                {"hostname": "h2", "name": "m2", "value": 2, "status": "ok", "timestamp": "2025-01-01T00:00:00"},
            ])

        # Each enqueue triggers a flush (batch_size=1)
        assert len(capture.calls) == 2
        for call in capture.calls:
            assert call["json"]["probe_token"] == "batch-token-xyz"

    def test_probe_token_matches_config(self):
        """Dispatcher uses the probe_token passed at construction."""
        probe = make_probe_mock()
        probe.config.probe_token = "config-token-456"
        orch = ProbeOrchestrator(probe, make_config())

        assert orch.dispatcher.probe_token == "config-token-456"
        orch._pool.shutdown(wait=False)


# ─── 10.3: Required fields present ──────────────────────────────────────────

class TestRequiredFieldsPresent:
    """
    10.3 — Campos obrigatórios (hostname, sensor_type, sensor_name,
    value, status, timestamp) estão presentes em todas as métricas enviadas.

    **Validates: Requirements 10**
    """

    REQUIRED_FIELDS = {"hostname", "sensor_type", "sensor_name", "value", "status", "timestamp"}

    def test_required_fields_in_dispatched_metrics(self):
        """All required fields are present after MetricsDispatcher formats metrics."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="token",
            batch_size=9999,
        )

        # Various metric shapes that collectors might produce
        dispatcher._buffer = [
            # Full metric from WMI collector
            {
                "hostname": "SRV-01",
                "sensor_type": "cpu",
                "name": "CPU Usage",
                "value": 45.0,
                "unit": "%",
                "status": "ok",
                "timestamp": "2025-01-15T10:00:00",
                "metadata": {"ip_address": "10.0.0.1"},
            },
            # Minimal metric (some fields missing — dispatcher should fill defaults)
            {
                "hostname": "SRV-02",
                "name": "Disk C:",
                "value": 80,
                "status": "warning",
                "timestamp": "2025-01-15T10:00:00",
            },
            # Standalone metric
            {
                "hostname": "__standalone__",
                "sensor_type": "icmp",
                "name": "Ping Gateway",
                "value": 5.2,
                "unit": "ms",
                "status": "ok",
                "timestamp": "2025-01-15T10:00:00",
                "metadata": {"sensor_id": 42},
            },
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        for m in capture.calls[0]["json"]["metrics"]:
            for field in self.REQUIRED_FIELDS:
                assert field in m, f"Missing required field '{field}' in metric: {m}"

    def test_standalone_sensor_has_required_fields(self):
        """SensorExecutor.collect_standalone ensures all required fields via setdefault."""
        probe = make_probe_mock()

        def fake_snmp(sensor, ts):
            # Simulate a collector that adds a minimal metric
            probe.buffer.append({"name": sensor["name"], "value": 1})

        probe._collect_snmp_standalone.side_effect = fake_snmp
        executor = SensorExecutor(probe)
        sensor = {"id": 100, "name": "Switch", "sensor_type": "snmp", "ip_address": "10.0.0.1"}
        ts = datetime(2025, 1, 15)

        result = executor.collect_standalone(sensor, ts)

        assert len(result) == 1
        m = result[0]
        for field in ["hostname", "sensor_type", "sensor_name", "value", "status", "timestamp", "metadata"]:
            assert field in m, f"Missing field '{field}' in standalone metric"


# ─── 10.4: Metadata preserves ip_address, public_ip, sensor_id ──────────────

class TestMetadataPreservation:
    """
    10.4 — metadata preserva ip_address, public_ip e sensor_id quando aplicável.

    **Validates: Requirements 10**
    """

    def test_metadata_preserves_ip_address(self):
        """ip_address in metadata is preserved through dispatch."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="token",
            batch_size=9999,
        )
        dispatcher._buffer = [
            {
                "hostname": "SRV-LOCAL",
                "name": "CPU",
                "value": 50,
                "status": "ok",
                "timestamp": "2025-01-15T10:00:00",
                "metadata": {"ip_address": "192.168.1.100"},
            },
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        sent_metric = capture.calls[0]["json"]["metrics"][0]
        assert "metadata" in sent_metric
        assert sent_metric["metadata"]["ip_address"] == "192.168.1.100"

    def test_metadata_preserves_public_ip(self):
        """public_ip in metadata is preserved through dispatch."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="token",
            batch_size=9999,
        )
        dispatcher._buffer = [
            {
                "hostname": "SRV-LOCAL",
                "name": "CPU",
                "value": 50,
                "status": "ok",
                "timestamp": "2025-01-15T10:00:00",
                "metadata": {"ip_address": "192.168.1.100", "public_ip": "203.0.113.5"},
            },
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        sent_metric = capture.calls[0]["json"]["metrics"][0]
        assert sent_metric["metadata"]["public_ip"] == "203.0.113.5"

    def test_metadata_preserves_sensor_id(self):
        """sensor_id in metadata is preserved for standalone sensors."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="token",
            batch_size=9999,
        )
        dispatcher._buffer = [
            {
                "hostname": "__standalone__",
                "sensor_type": "icmp",
                "name": "Ping Device",
                "value": 3.5,
                "unit": "ms",
                "status": "ok",
                "timestamp": "2025-01-15T10:00:00",
                "metadata": {"sensor_id": 42},
            },
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        sent_metric = capture.calls[0]["json"]["metrics"][0]
        assert sent_metric["metadata"]["sensor_id"] == 42

    def test_sensor_executor_standalone_preserves_sensor_id_in_metadata(self):
        """SensorExecutor.collect_standalone preserves sensor_id in metadata."""
        probe = make_probe_mock()

        def fake_icmp(sensor, ts):
            probe.buffer.append({
                "sensor_id": sensor["id"],
                "sensor_type": "icmp",
                "name": sensor["name"],
                "value": 5.0,
                "unit": "ms",
                "status": "ok",
                "timestamp": ts.isoformat(),
                "hostname": "__standalone__",
                "metadata": {"sensor_id": sensor["id"]},
            })

        probe._collect_icmp_standalone.side_effect = fake_icmp
        executor = SensorExecutor(probe)
        sensor = {"id": 99, "name": "Ping Router", "sensor_type": "icmp", "ip_address": "10.0.0.1"}
        ts = datetime(2025, 1, 15)

        result = executor.collect_standalone(sensor, ts)

        assert len(result) == 1
        assert result[0]["metadata"]["sensor_id"] == 99

    def test_metadata_empty_dict_when_not_provided(self):
        """Metrics without metadata get an empty dict (not None)."""
        dispatcher = MetricsDispatcher(
            api_url="http://localhost:8000",
            probe_token="token",
            batch_size=9999,
        )
        dispatcher._buffer = [
            {
                "hostname": "SRV-01",
                "name": "CPU",
                "value": 50,
                "status": "ok",
                "timestamp": "2025-01-15T10:00:00",
                # No metadata key
            },
        ]

        capture = CaptureHttpxClient()
        with patch("httpx.Client", return_value=capture):
            dispatcher.flush()

        sent_metric = capture.calls[0]["json"]["metrics"][0]
        assert "metadata" in sent_metric
        assert isinstance(sent_metric["metadata"], dict)
