"""
Connection Pool Tests — Coruja Monitor v3.0
Tests: pool acquire/release/timeout for WMI, SNMP, TCP pools.
Requirements: 2.4, 2.5
"""
import pytest
import time
from unittest.mock import MagicMock, patch

from probe.connection_pool.snmp_pool import SNMPConnectionPool, SNMPConnection
from probe.connection_pool.tcp_pool import TCPConnectionPool, TCPConnection
from probe.engine.wmi_pool import WMIConnectionPool, PooledConnection


@pytest.mark.unit
class TestSNMPConnectionPool:
    """Req 2.4 — SNMP connection pool acquire/release/limit."""

    def test_acquire_creates_new_connection(self):
        pool = SNMPConnectionPool(max_per_host=5)
        conn = pool.acquire("192.168.1.1", community="public", port=161, version="2c")
        assert conn is not None
        assert conn.in_use is True
        assert conn.host == "192.168.1.1"

    def test_release_makes_connection_available(self):
        pool = SNMPConnectionPool(max_per_host=5)
        conn = pool.acquire("192.168.1.1")
        pool.release("192.168.1.1", conn)
        assert conn.in_use is False

    def test_reuse_idle_connection(self):
        pool = SNMPConnectionPool(max_per_host=5)
        conn1 = pool.acquire("192.168.1.1")
        pool.release("192.168.1.1", conn1)
        conn2 = pool.acquire("192.168.1.1")
        assert conn2 is conn1

    def test_max_connections_per_host(self):
        pool = SNMPConnectionPool(max_per_host=2)
        c1 = pool.acquire("192.168.1.1")
        c2 = pool.acquire("192.168.1.1")
        c3 = pool.acquire("192.168.1.1")
        assert c1 is not None
        assert c2 is not None
        assert c3 is None  # limit reached

    def test_invalidate_removes_connection(self):
        pool = SNMPConnectionPool(max_per_host=5)
        conn = pool.acquire("192.168.1.1")
        pool.invalidate("192.168.1.1", conn)
        stats = pool.stats()
        assert stats.get("192.168.1.1", {}).get("total", 0) == 0

    def test_stats_reports_in_use_and_idle(self):
        pool = SNMPConnectionPool(max_per_host=5)
        c1 = pool.acquire("192.168.1.1")
        c2 = pool.acquire("192.168.1.1")
        pool.release("192.168.1.1", c1)
        stats = pool.stats()["192.168.1.1"]
        assert stats["total"] == 2
        assert stats["in_use"] == 1
        assert stats["idle"] == 1


@pytest.mark.unit
class TestTCPConnectionPool:
    """Req 2.4 — TCP connection pool acquire/release/limit."""

    @patch("socket.socket")
    def test_acquire_creates_tcp_connection(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        pool = TCPConnectionPool(max_per_host=10, connect_timeout=5.0)
        conn = pool.acquire("192.168.1.1", 80)
        assert conn is not None
        assert conn.in_use is True

    @patch("socket.socket")
    def test_release_tcp_connection(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        pool = TCPConnectionPool(max_per_host=10)
        conn = pool.acquire("192.168.1.1", 80)
        pool.release("192.168.1.1", 80, conn)
        assert conn.in_use is False

    @patch("socket.socket")
    def test_tcp_max_connections(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        pool = TCPConnectionPool(max_per_host=2)
        c1 = pool.acquire("192.168.1.1", 80)
        c2 = pool.acquire("192.168.1.1", 80)
        c3 = pool.acquire("192.168.1.1", 80)
        assert c1 is not None
        assert c2 is not None
        assert c3 is None

    @patch("socket.socket")
    def test_tcp_invalidate_closes_socket(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        pool = TCPConnectionPool(max_per_host=10)
        conn = pool.acquire("192.168.1.1", 80)
        pool.invalidate("192.168.1.1", 80, conn)
        mock_sock.close.assert_called()


@pytest.mark.unit
class TestWMIConnectionPool:
    """Req 2.4 — WMI connection pool acquire/release/backoff."""

    def test_wmi_pool_init(self):
        pool = WMIConnectionPool(max_per_host=3)
        assert pool.max_per_host == 3

    def test_wmi_pool_stats_empty(self):
        pool = WMIConnectionPool(max_per_host=3)
        assert pool.stats() == {}

    def test_wmi_pool_backoff_tracking(self):
        pool = WMIConnectionPool(max_per_host=3)
        pool._record_auth_failure("SERVER01")
        assert pool._is_in_backoff("SERVER01") is True

    def test_wmi_pool_clear_auth_failure(self):
        pool = WMIConnectionPool(max_per_host=3)
        pool._record_auth_failure("SERVER01")
        pool._clear_auth_failure("SERVER01")
        assert pool._is_in_backoff("SERVER01") is False
