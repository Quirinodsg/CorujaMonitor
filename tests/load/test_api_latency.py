"""
Load: API Latency Tests — Coruja Monitor v3.0
Tests: API response latency <200ms.
Requirements: 13.3, 13.4
"""
import sys
import os
import pytest
import time
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from api.routers.observability import router as observability_router


@pytest.mark.load
class TestAPILatency:
    """Req 13.3 — API latency <200ms."""

    def test_health_score_latency(self):
        """Health score endpoint responds within 200ms."""
        app = FastAPI()
        app.include_router(observability_router)
        mock_db = MagicMock()
        row = MagicMock()
        row.total = 100
        row.ok_count = 90
        row.warning_count = 8
        row.critical_count = 2
        row.unknown_count = 0
        mock_db.execute.return_value.fetchone.return_value = row
        mock_db.execute.return_value.scalar.return_value = 0
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)

        start = time.monotonic()
        resp = client.get("/api/v1/observability/health-score")
        latency_ms = (time.monotonic() - start) * 1000
        assert resp.status_code == 200
        assert latency_ms < 200

    def test_alerts_endpoint_latency(self):
        """Alerts endpoint responds within 200ms."""
        app = FastAPI()
        app.include_router(observability_router)
        mock_db = MagicMock()
        mock_db.execute.return_value.fetchall.return_value = []
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)

        start = time.monotonic()
        resp = client.get("/api/v1/alerts/intelligent")
        latency_ms = (time.monotonic() - start) * 1000
        assert resp.status_code == 200
        assert latency_ms < 200
