"""
FASE 2 — Testes do ICMP Sensor
Valida: ping ok, host offline, latência alta, packet loss, parse de output.
"""
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../probe'))

from collectors.icmp_sensor import ICMPSensor


# ─── Outputs de ping simulados ───────────────────────────────────────────────

WINDOWS_PING_OK = """
Pinging 192.168.1.1 with 32 bytes of data:
Reply from 192.168.1.1: bytes=32 time=2ms TTL=128
Reply from 192.168.1.1: bytes=32 time=1ms TTL=128
Reply from 192.168.1.1: bytes=32 time=3ms TTL=128
Reply from 192.168.1.1: bytes=32 time=2ms TTL=128

Ping statistics for 192.168.1.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 1ms, Maximum = 3ms, Average = 2ms
"""

WINDOWS_PING_OFFLINE = """
Pinging 192.168.1.99 with 32 bytes of data:
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Ping statistics for 192.168.1.99:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
"""

WINDOWS_PING_PARTIAL_LOSS = """
Pinging 192.168.1.1 with 32 bytes of data:
Reply from 192.168.1.1: bytes=32 time=5ms TTL=128
Request timed out.
Reply from 192.168.1.1: bytes=32 time=6ms TTL=128
Request timed out.

Ping statistics for 192.168.1.1:
    Packets: Sent = 4, Received = 2, Lost = 2 (50% loss),
Approximate round trip times in milli-seconds:
    Minimum = 5ms, Maximum = 6ms, Average = 5ms
"""

LINUX_PING_OK = """
PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.456 ms
64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=0.512 ms
64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0.489 ms
64 bytes from 192.168.1.1: icmp_seq=4 ttl=64 time=0.501 ms

--- 192.168.1.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3003ms
rtt min/avg/max/mdev = 0.456/0.489/0.512/0.021 ms
"""

LINUX_PING_OFFLINE = """
PING 10.0.0.99 (10.0.0.99) 56(84) bytes of data.

--- 10.0.0.99 ping statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 3000ms
"""

LINUX_PING_HIGH_LATENCY = """
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=250.1 ms
64 bytes from 10.0.0.1: icmp_seq=2 ttl=64 time=310.5 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=280.3 ms
64 bytes from 10.0.0.1: icmp_seq=4 ttl=64 time=295.2 ms

--- 10.0.0.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3003ms
rtt min/avg/max/mdev = 250.1/284.0/310.5/22.1 ms
"""


def make_proc(stdout="", returncode=0):
    proc = MagicMock()
    proc.stdout = stdout
    proc.stderr = ""
    proc.returncode = returncode
    return proc


# ─── Testes de parse ─────────────────────────────────────────────────────────

class TestICMPSensorParse:

    def test_parse_windows_ok(self):
        sensor = ICMPSensor("192.168.1.1")
        sensor._is_windows = True
        result = sensor._parse_output(WINDOWS_PING_OK)
        assert result["packet_loss_percent"] == 0.0
        assert result["avg_ms"] == 2.0
        assert result["min_ms"] == 1.0
        assert result["max_ms"] == 3.0

    def test_parse_windows_offline(self):
        sensor = ICMPSensor("192.168.1.99")
        sensor._is_windows = True
        result = sensor._parse_output(WINDOWS_PING_OFFLINE)
        assert result["packet_loss_percent"] == 100.0

    def test_parse_windows_partial_loss(self):
        sensor = ICMPSensor("192.168.1.1")
        sensor._is_windows = True
        result = sensor._parse_output(WINDOWS_PING_PARTIAL_LOSS)
        assert result["packet_loss_percent"] == 50.0

    def test_parse_linux_ok(self):
        sensor = ICMPSensor("192.168.1.1")
        sensor._is_windows = False
        result = sensor._parse_output(LINUX_PING_OK)
        assert result["packet_loss_percent"] == 0.0
        assert result["avg_ms"] == pytest.approx(0.489, abs=0.01)

    def test_parse_linux_offline(self):
        sensor = ICMPSensor("10.0.0.99")
        sensor._is_windows = False
        result = sensor._parse_output(LINUX_PING_OFFLINE)
        assert result["packet_loss_percent"] == 100.0

    def test_parse_linux_high_latency(self):
        sensor = ICMPSensor("10.0.0.1")
        sensor._is_windows = False
        result = sensor._parse_output(LINUX_PING_HIGH_LATENCY)
        assert result["avg_ms"] == pytest.approx(284.0, abs=1.0)
        assert result["packet_loss_percent"] == 0.0


# ─── Testes de status ────────────────────────────────────────────────────────

class TestICMPSensorStatus:

    def test_ok_status(self):
        sensor = ICMPSensor("host", warning_latency_ms=100, critical_latency_ms=500)
        assert sensor._determine_status(50.0, 0.0) == "ok"

    def test_warning_latency(self):
        sensor = ICMPSensor("host", warning_latency_ms=100, critical_latency_ms=500)
        assert sensor._determine_status(150.0, 0.0) == "warning"

    def test_critical_latency(self):
        sensor = ICMPSensor("host", warning_latency_ms=100, critical_latency_ms=500)
        assert sensor._determine_status(600.0, 0.0) == "critical"

    def test_warning_packet_loss(self):
        sensor = ICMPSensor("host", warning_loss_pct=10.0, critical_loss_pct=50.0)
        assert sensor._determine_status(10.0, 25.0) == "warning"

    def test_critical_packet_loss(self):
        sensor = ICMPSensor("host", warning_loss_pct=10.0, critical_loss_pct=50.0)
        assert sensor._determine_status(10.0, 100.0) == "critical"


# ─── Testes de collect (mock subprocess) ─────────────────────────────────────

class TestICMPSensorCollect:

    def test_collect_host_online_linux(self):
        sensor = ICMPSensor("192.168.1.1")
        sensor._is_windows = False

        with patch("subprocess.run", return_value=make_proc(LINUX_PING_OK, 0)):
            result = sensor.collect()

        assert result["status"] == "ok"
        assert result["is_online"] is True
        assert result["packet_loss_percent"] == 0.0
        assert result["type"] == "icmp_ping"
        assert result["unit"] == "ms"

    def test_collect_host_offline_linux(self):
        sensor = ICMPSensor("10.0.0.99", retries=0)
        sensor._is_windows = False

        with patch("subprocess.run", return_value=make_proc(LINUX_PING_OFFLINE, 1)):
            result = sensor.collect()

        assert result["status"] == "critical"
        assert result["is_online"] is False
        assert result["packet_loss_percent"] == 100.0

    def test_collect_host_online_windows(self):
        sensor = ICMPSensor("192.168.1.1")
        sensor._is_windows = True

        with patch("subprocess.run", return_value=make_proc(WINDOWS_PING_OK, 0)):
            result = sensor.collect()

        assert result["status"] == "ok"
        assert result["is_online"] is True
        assert result["latency_ms"] == 2.0

    def test_collect_timeout(self):
        sensor = ICMPSensor("10.0.0.1", retries=0)

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ping", 5)):
            result = sensor.collect()

        assert result["status"] == "critical"
        assert result["is_online"] is False

    def test_collect_result_structure(self):
        sensor = ICMPSensor("192.168.1.1")
        sensor._is_windows = False

        with patch("subprocess.run", return_value=make_proc(LINUX_PING_OK, 0)):
            result = sensor.collect()

        required = ["type", "name", "host", "status", "latency_ms",
                    "packet_loss_percent", "is_online", "value", "unit", "metadata"]
        for field in required:
            assert field in result, f"Campo '{field}' ausente"

    def test_collect_high_latency_warning(self):
        sensor = ICMPSensor("10.0.0.1", warning_latency_ms=200, critical_latency_ms=500)
        sensor._is_windows = False

        with patch("subprocess.run", return_value=make_proc(LINUX_PING_HIGH_LATENCY, 0)):
            result = sensor.collect()

        assert result["status"] == "warning"
        assert result["latency_ms"] > 200
