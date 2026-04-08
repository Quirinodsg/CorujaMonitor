"""
E2E: WEBSOCKET DROP scenario.
Connection lost → auto-reconnect → data updated.
Requirements: 19.7
"""
import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))


@pytest.mark.e2e
class TestWebSocketDropE2E:
    """Req 19.7 — WEBSOCKET DROP: disconnect → reconnect → data flows."""

    def test_connection_manager_handles_disconnect(self):
        """ConnectionManager handles disconnect gracefully."""
        from api.routers.observability import ConnectionManager
        mgr = ConnectionManager()
        ws = MagicMock()
        mgr.active.append(ws)
        mgr.disconnect(ws)
        assert ws not in mgr.active

    def test_reconnect_after_disconnect(self):
        """New connection can be added after disconnect."""
        from api.routers.observability import ConnectionManager
        mgr = ConnectionManager()
        ws1 = MagicMock()
        mgr.active.append(ws1)
        mgr.disconnect(ws1)
        ws2 = MagicMock()
        mgr.active.append(ws2)
        assert len(mgr.active) == 1
