"""
FASE 2 — Testes do TCP Port Sensor
Valida: porta aberta, porta fechada, timeout, latência, RPC validator.
"""
import pytest
import socket
import time
from unittest.mock import patch, MagicMock, call
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../probe'))

from collectors.tcp_port_sensor import TCPPortSensor, RPCFirewallValidator


# ─── Testes básicos ──────────────────────────────────────────────────────────

class TestTCPPortSensorBasic:

    def test_port_open_returns_ok(self):
        """Porta aberta → status ok, is_open True."""
        sensor = TCPPortSensor("192.168.1.1", 80, timeout=3.0, retries=0)

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("socket.create_connection", return_value=mock_conn):
            with patch("time.monotonic", side_effect=[0.0, 0.025]):
                result = sensor.collect()

        assert result["status"] == "ok"
        assert result["is_open"] is True
        assert result["port"] == 80
        assert result["host"] == "192.168.1.1"
        assert result["type"] == "tcp_port"

    def test_port_closed_returns_critical(self):
        """Porta fechada (ConnectionRefusedError) → status critical."""
        sensor = TCPPortSensor("192.168.1.1", 9999, timeout=1.0, retries=0)

        with patch("socket.create_connection", side_effect=ConnectionRefusedError("refused")):
            result = sensor.collect()

        assert result["status"] == "critical"
        assert result["is_open"] is False

    def test_timeout_returns_critical(self):
        """Timeout → status critical."""
        sensor = TCPPortSensor("10.0.0.1", 80, timeout=1.0, retries=0)

        with patch("socket.create_connection", side_effect=socket.timeout("timed out")):
            result = sensor.collect()

        assert result["status"] == "critical"
        assert result["is_open"] is False

    def test_os_error_returns_critical(self):
        """OSError (host unreachable) → status critical."""
        sensor = TCPPortSensor("10.0.0.1", 80, timeout=1.0, retries=0)

        with patch("socket.create_connection", side_effect=OSError("No route to host")):
            result = sensor.collect()

        assert result["status"] == "critical"
        assert result["is_open"] is False

    def test_latency_measured(self):
        """Latência deve ser medida em ms."""
        sensor = TCPPortSensor("192.168.1.1", 443, retries=0)

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("socket.create_connection", return_value=mock_conn):
            with patch("time.monotonic", side_effect=[0.0, 0.042]):
                result = sensor.collect()

        assert result["latency_ms"] == pytest.approx(42.0, abs=1)
        assert result["value"] == result["latency_ms"]
        assert result["unit"] == "ms"


# ─── Testes de retry ─────────────────────────────────────────────────────────

class TestTCPPortSensorRetry:

    def test_retry_on_failure(self):
        """retries=2 → tenta 3x antes de desistir."""
        sensor = TCPPortSensor("10.0.0.1", 80, retries=2)
        call_count = {"n": 0}

        def fail_connect(*args, **kwargs):
            call_count["n"] += 1
            raise ConnectionRefusedError("refused")

        with patch("socket.create_connection", side_effect=fail_connect):
            with patch("time.sleep"):  # evitar delay real
                result = sensor.collect()

        assert result["status"] == "critical"
        assert call_count["n"] == 3  # 1 + 2 retries

    def test_retry_succeeds_on_second_attempt(self):
        """Falha na 1ª, sucesso na 2ª."""
        sensor = TCPPortSensor("192.168.1.1", 80, retries=1)
        call_count = {"n": 0}

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        def flaky_connect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise ConnectionRefusedError("refused")
            return mock_conn

        with patch("socket.create_connection", side_effect=flaky_connect):
            with patch("time.sleep"):
                with patch("time.monotonic", return_value=0.0):
                    result = sensor.collect()

        assert result["status"] == "ok"
        assert call_count["n"] == 2


# ─── Testes de estrutura ─────────────────────────────────────────────────────

class TestTCPPortSensorStructure:

    def test_result_has_required_fields(self):
        sensor = TCPPortSensor("192.168.1.1", 22, retries=0)

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch("socket.create_connection", return_value=mock_conn):
            with patch("time.monotonic", side_effect=[0.0, 0.01]):
                result = sensor.collect()

        required = ["type", "name", "host", "port", "status",
                    "is_open", "latency_ms", "value", "unit", "metadata"]
        for field in required:
            assert field in result, f"Campo '{field}' ausente"

    def test_name_includes_port(self):
        sensor = TCPPortSensor("host", 3389, retries=0)

        with patch("socket.create_connection", side_effect=ConnectionRefusedError()):
            result = sensor.collect()

        assert "3389" in result["name"]

    def test_error_result_has_error_in_metadata(self):
        sensor = TCPPortSensor("host", 80, retries=0)

        with patch("socket.create_connection", side_effect=ConnectionRefusedError("refused")):
            result = sensor.collect()

        assert "error" in result["metadata"]


# ─── Testes de portas comuns ─────────────────────────────────────────────────

class TestTCPCommonPorts:

    @pytest.mark.parametrize("port,name", [
        (22, "SSH"),
        (80, "HTTP"),
        (443, "HTTPS"),
        (3389, "RDP"),
        (5985, "WinRM"),
        (135, "RPC"),
        (445, "SMB"),
    ])
    def test_common_port_sensor_creation(self, port, name):
        """Sensor pode ser criado para qualquer porta comum."""
        sensor = TCPPortSensor("192.168.1.1", port)
        assert sensor.port == port
        assert sensor.host == "192.168.1.1"


# ─── Testes do RPC Firewall Validator ────────────────────────────────────────

class TestRPCFirewallValidator:

    def _make_open_result(self, port):
        return {
            "type": "tcp_port", "host": "192.168.1.1", "port": port,
            "status": "ok", "is_open": True, "latency_ms": 5.0,
            "value": 5.0, "unit": "ms",
            "name": f"TCP Port {port}",
            "metadata": {"attempts": 1, "collection_method": "tcp_connect"},
        }

    def _make_closed_result(self, port):
        return {
            "type": "tcp_port", "host": "192.168.1.1", "port": port,
            "status": "critical", "is_open": False, "latency_ms": 0.0,
            "value": 0.0, "unit": "ms",
            "name": f"TCP Port {port}",
            "metadata": {"attempts": 1, "error": "refused", "collection_method": "tcp_connect"},
        }

    def test_validate_all_open(self):
        """Todas as portas abertas → overall_status ok."""
        validator = RPCFirewallValidator("192.168.1.1")

        with patch.object(TCPPortSensor, "collect", side_effect=lambda: self._make_open_result(135)):
            result = validator.validate()

        assert result["overall_status"] == "ok"
        assert result["rpc_endpoint_mapper_open"] is True

    def test_validate_rpc_closed(self):
        """Porta 135 fechada → overall_status critical."""
        validator = RPCFirewallValidator("192.168.1.1")

        # Simular todas as portas fechadas
        closed = self._make_closed_result(135)
        with patch.object(TCPPortSensor, "collect", return_value=closed):
            result = validator.validate()

        assert result["overall_status"] == "critical"
        assert result["rpc_endpoint_mapper_open"] is False
        assert "135" in result["recommendation"] or "firewall" in result["recommendation"].lower()

    def test_check_wmi_ports_returns_list(self):
        """check_wmi_ports retorna lista de métricas."""
        validator = RPCFirewallValidator("192.168.1.1")

        open_result = self._make_open_result(135)
        with patch.object(TCPPortSensor, "collect", return_value=open_result):
            metrics = validator.check_wmi_ports()

        assert isinstance(metrics, list)
        assert len(metrics) > 0
        assert metrics[0]["type"] == "tcp_port"
