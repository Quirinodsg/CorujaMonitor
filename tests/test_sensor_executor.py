"""
Tests for Task 4: SensorExecutor — Execução Isolada de Sensores (Requisitos 3, 10)
Validates sensor routing (WMI/SNMP), standalone routing chain, fault isolation,
and metric format preservation.

**Validates: Requirements 3, 10**
"""
import threading
from datetime import datetime
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from probe.parallel_engine import SensorExecutor


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_probe_mock():
    """Create a mock ProbeCore with buffer and collection methods."""
    probe = MagicMock()
    probe.buffer = []
    probe.config = MagicMock()
    probe.config.api_url = "http://localhost:8000"
    probe.config.probe_token = "test-token"
    return probe


def make_server(hostname="SRV-01", ip="10.0.0.1", protocol="wmi", **kwargs):
    """Create a server dict for testing."""
    s = {
        "id": 1,
        "hostname": hostname,
        "ip_address": ip,
        "monitoring_protocol": protocol,
    }
    s.update(kwargs)
    return s


def make_sensor(name="Test Sensor", sensor_type="snmp", ip="10.0.0.50", **kwargs):
    """Create a standalone sensor dict for testing."""
    s = {
        "id": 100,
        "name": name,
        "sensor_type": sensor_type,
        "ip_address": ip,
    }
    s.update(kwargs)
    return s


# ─── Unit Tests: collect_server ──────────────────────────────────────────────

class TestSensorExecutorCollectServer:
    """Tests for SensorExecutor.collect_server routing and isolation."""

    def test_routes_to_wmi_for_wmi_protocol(self):
        """Servers with monitoring_protocol=wmi route to _collect_wmi_remote."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        server = make_server(protocol="wmi")

        executor.collect_server(server)

        probe._collect_wmi_remote.assert_called_once_with(server)
        probe._collect_snmp_remote.assert_not_called()

    def test_routes_to_snmp_for_snmp_protocol(self):
        """Servers with monitoring_protocol=snmp route to _collect_snmp_remote."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        server = make_server(protocol="snmp")

        executor.collect_server(server)

        probe._collect_snmp_remote.assert_called_once_with(server)
        probe._collect_wmi_remote.assert_not_called()

    def test_routes_to_wmi_when_wmi_enabled(self):
        """Servers with wmi_enabled=true route to WMI even without explicit protocol."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        server = make_server(protocol="other", wmi_enabled=True)

        executor.collect_server(server)

        probe._collect_wmi_remote.assert_called_once_with(server)

    def test_returns_metrics_added_to_buffer(self):
        """collect_server returns metrics that were added to the buffer."""
        probe = make_probe_mock()

        def fake_wmi(server):
            probe.buffer.append({
                "hostname": "SRV-01",
                "sensor_type": "cpu",
                "name": "CPU Usage",
                "value": 45.0,
                "unit": "%",
                "status": "ok",
                "timestamp": "2025-01-01T00:00:00",
                "metadata": {"ip_address": "10.0.0.1"},
            })

        probe._collect_wmi_remote.side_effect = fake_wmi
        executor = SensorExecutor(probe)
        server = make_server(protocol="wmi")

        result = executor.collect_server(server)

        assert len(result) == 1
        assert result[0]["hostname"] == "SRV-01"
        assert result[0]["sensor_type"] == "cpu"

    def test_fault_isolation_wmi_exception(self):
        """Exception in WMI collector does not propagate — returns empty list."""
        probe = make_probe_mock()
        probe._collect_wmi_remote.side_effect = RuntimeError("WMI connection failed")
        executor = SensorExecutor(probe)
        server = make_server(protocol="wmi")

        result = executor.collect_server(server)

        assert result == []

    def test_fault_isolation_snmp_exception(self):
        """Exception in SNMP collector does not propagate — returns empty list."""
        probe = make_probe_mock()
        probe._collect_snmp_remote.side_effect = ConnectionError("SNMP timeout")
        executor = SensorExecutor(probe)
        server = make_server(protocol="snmp")

        result = executor.collect_server(server)

        assert result == []

    def test_default_protocol_is_wmi(self):
        """When monitoring_protocol is missing, defaults to WMI."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        server = {"id": 1, "hostname": "SRV-X", "ip_address": "10.0.0.5"}

        executor.collect_server(server)

        probe._collect_wmi_remote.assert_called_once()


# ─── Unit Tests: collect_standalone routing ──────────────────────────────────

class TestSensorExecutorCollectStandalone:
    """Tests for SensorExecutor.collect_standalone routing chain."""

    def test_routes_http_sensor(self):
        """HTTP sensors route to _collect_http."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(sensor_type="http", http_url="https://example.com")
        ts = datetime(2025, 1, 1)

        with patch.object(executor, "_collect_http") as mock_http:
            executor.collect_standalone(sensor, ts)
            mock_http.assert_called_once_with(sensor, ts)

    def test_routes_icmp_by_sensor_type(self):
        """ICMP sensors route to _collect_icmp_standalone."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Ping Device", sensor_type="icmp", ip="10.0.0.10")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_icmp_standalone.assert_called_once_with(sensor, ts)

    def test_routes_icmp_by_category(self):
        """Sensors with category=icmp route to ICMP collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Automator", sensor_type="other", ip="10.0.0.10", category="icmp")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_icmp_standalone.assert_called_once_with(sensor, ts)

    def test_routes_engetron_by_name(self):
        """Sensors with 'engetron' in name route to Engetron collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Engetron UPS Sala 1", sensor_type="ups", ip="10.0.0.20")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_engetron.assert_called_once_with(sensor, ts)

    def test_routes_conflex_by_name(self):
        """Sensors with 'conflex' in name route to Conflex collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Conflex HVAC DC1", sensor_type="hvac", ip="10.0.0.30")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_conflex.assert_called_once_with(sensor, ts)

    def test_routes_ar_condicionado_to_conflex(self):
        """Sensors with 'ar-condicionado' in name route to Conflex collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Ar-Condicionado Sala TI", sensor_type="hvac", ip="10.0.0.31")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_conflex.assert_called_once_with(sensor, ts)

    def test_routes_printer_by_name(self):
        """Sensors with printer keywords in name route to Printer collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="HP LaserJet 4050", sensor_type="printer", ip="10.0.0.40")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_printer.assert_called_once_with(sensor, ts)

    def test_routes_impressora_to_printer(self):
        """Sensors with 'impressora' in name route to Printer collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Impressora RH", sensor_type="printer", ip="10.0.0.41")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_printer.assert_called_once_with(sensor, ts)

    def test_routes_equallogic_by_name(self):
        """Sensors with 'equallogic' in name route to EqualLogic collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="EqualLogic PS6100", sensor_type="storage", ip="10.0.0.50")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_equallogic.assert_called_once_with(sensor, ts)

    def test_routes_storage_to_equallogic(self):
        """Sensors with 'storage' in name route to EqualLogic collector."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Dell Storage SAN", sensor_type="storage", ip="10.0.0.51")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_equallogic.assert_called_once_with(sensor, ts)

    def test_routes_snmp_sensor(self):
        """SNMP sensors route to _collect_snmp_standalone."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Switch Core", sensor_type="snmp", ip="10.0.0.60")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_snmp_standalone.assert_called_once_with(sensor, ts)

    def test_routes_fallback_to_snmp(self):
        """Sensors with IP but no specific type fall back to SNMP."""
        probe = make_probe_mock()
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Unknown Device", sensor_type="other", ip="10.0.0.70")
        ts = datetime(2025, 1, 1)

        executor.collect_standalone(sensor, ts)

        probe._collect_snmp_standalone.assert_called_once_with(sensor, ts)

    def test_fault_isolation_standalone_exception(self):
        """Exception in standalone collector does not propagate."""
        probe = make_probe_mock()
        probe._collect_engetron.side_effect = RuntimeError("HTTP scraping failed")
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Engetron UPS", sensor_type="ups", ip="10.0.0.20")
        ts = datetime(2025, 1, 1)

        result = executor.collect_standalone(sensor, ts)

        # Should not raise, returns empty list
        assert result == []


# ─── Unit Tests: Metric Format Preservation ──────────────────────────────────

class TestSensorExecutorMetricFormat:
    """Tests for metric format preservation (Req 10)."""

    def test_collect_server_preserves_all_fields(self):
        """Metrics from collect_server have all required fields."""
        probe = make_probe_mock()

        def fake_wmi(server):
            probe.buffer.append({
                "hostname": "SRV-01",
                "sensor_type": "cpu",
                "name": "CPU Usage",
                "value": 75.5,
                "unit": "%",
                "status": "warning",
                "timestamp": "2025-01-01T10:00:00",
                "metadata": {"ip_address": "10.0.0.1"},
            })

        probe._collect_wmi_remote.side_effect = fake_wmi
        executor = SensorExecutor(probe)
        server = make_server()

        result = executor.collect_server(server)

        assert len(result) == 1
        m = result[0]
        assert m["hostname"] == "SRV-01"
        assert m["sensor_type"] == "cpu"
        assert m["name"] == "CPU Usage"
        assert m["value"] == 75.5
        assert m["unit"] == "%"
        assert m["status"] == "warning"
        assert m["timestamp"] == "2025-01-01T10:00:00"
        assert "ip_address" in m["metadata"]

    def test_collect_standalone_ensures_default_fields(self):
        """collect_standalone ensures all required fields have defaults."""
        probe = make_probe_mock()

        def fake_snmp(sensor, ts):
            # Simulate a collector that adds a minimal metric
            probe.buffer.append({
                "sensor_id": sensor["id"],
                "name": sensor["name"],
                "value": 1,
            })

        probe._collect_snmp_standalone.side_effect = fake_snmp
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Switch Core", sensor_type="snmp", ip="10.0.0.60")
        ts = datetime(2025, 1, 1)

        result = executor.collect_standalone(sensor, ts)

        assert len(result) == 1
        m = result[0]
        # All required fields should be present with defaults
        assert "hostname" in m
        assert "sensor_type" in m
        assert "sensor_name" in m
        assert "value" in m
        assert "status" in m
        assert "timestamp" in m
        assert "metadata" in m

    def test_collect_standalone_preserves_existing_fields(self):
        """collect_standalone does not overwrite existing fields."""
        probe = make_probe_mock()

        def fake_snmp(sensor, ts):
            probe.buffer.append({
                "hostname": "__standalone__",
                "sensor_type": "snmp",
                "name": "Switch Core",
                "value": 1,
                "unit": "status",
                "status": "ok",
                "timestamp": "2025-06-01T12:00:00",
                "metadata": {"sensor_id": 100},
            })

        probe._collect_snmp_standalone.side_effect = fake_snmp
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Switch Core", sensor_type="snmp", ip="10.0.0.60")
        ts = datetime(2025, 1, 1)

        result = executor.collect_standalone(sensor, ts)

        assert len(result) == 1
        m = result[0]
        # Existing values should be preserved (not overwritten by defaults)
        assert m["hostname"] == "__standalone__"
        assert m["status"] == "ok"
        assert m["timestamp"] == "2025-06-01T12:00:00"
        assert m["metadata"] == {"sensor_id": 100}


# ─── Fault Isolation Tests ───────────────────────────────────────────────────

class TestSensorExecutorFaultIsolation:
    """Tests for fault isolation — exceptions in one collector don't affect others."""

    def test_multiple_servers_isolated(self):
        """Exception in one server collection doesn't affect another."""
        probe = make_probe_mock()
        call_count = 0

        def fake_wmi(server):
            nonlocal call_count
            call_count += 1
            if server["hostname"] == "SRV-FAIL":
                raise RuntimeError("WMI connection refused")
            probe.buffer.append({
                "hostname": server["hostname"],
                "sensor_type": "cpu",
                "name": "CPU",
                "value": 50,
                "unit": "%",
                "status": "ok",
                "timestamp": "2025-01-01T00:00:00",
                "metadata": {},
            })

        probe._collect_wmi_remote.side_effect = fake_wmi
        executor = SensorExecutor(probe)

        # First server fails
        result_fail = executor.collect_server(make_server(hostname="SRV-FAIL"))
        assert result_fail == []

        # Second server succeeds — not affected by first failure
        result_ok = executor.collect_server(make_server(hostname="SRV-OK"))
        assert len(result_ok) == 1
        assert result_ok[0]["hostname"] == "SRV-OK"

    def test_standalone_exception_returns_empty(self):
        """Any exception in standalone collection returns empty list, not raises."""
        probe = make_probe_mock()
        probe._collect_icmp_standalone.side_effect = OSError("Network unreachable")
        executor = SensorExecutor(probe)
        sensor = make_sensor(name="Ping Test", sensor_type="icmp", ip="10.0.0.99")
        ts = datetime(2025, 1, 1)

        result = executor.collect_standalone(sensor, ts)

        assert result == []
