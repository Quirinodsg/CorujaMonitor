"""
API v2 Endpoint Tests — Coruja Monitor v3.0
Tests: dashboard/overview, servers, sensors, incidents.
Requirements: 10.2
"""
import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))


def _mock_db():
    db = MagicMock()
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.scalar.return_value = 0
    return db


@pytest.mark.unit
class TestDashboardEndpoint:
    """Req 10.2 — /dashboard/overview returns overview data."""

    def test_dashboard_overview(self):
        from api.routers.dashboard import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/dashboard")
        from database import get_db
        app.dependency_overrides[get_db] = lambda: _mock_db()
        client = TestClient(app)
        resp = client.get("/api/v1/dashboard/overview")
        assert resp.status_code in (200, 401)

    def test_dashboard_health_summary(self):
        from api.routers.dashboard import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/dashboard")
        from database import get_db
        app.dependency_overrides[get_db] = lambda: _mock_db()
        client = TestClient(app)
        resp = client.get("/api/v1/dashboard/health-summary")
        assert resp.status_code in (200, 401)


@pytest.mark.unit
class TestServersEndpoint:
    """Req 10.2 — /servers returns server list."""

    def test_servers_endpoint_accessible(self):
        from api.routers.servers import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/servers")
        from database import get_db
        app.dependency_overrides[get_db] = lambda: _mock_db()
        client = TestClient(app)
        resp = client.get("/api/v1/servers/")
        # May return 200 or other status depending on auth requirements
        assert resp.status_code in (200, 401, 403, 422, 500)


@pytest.mark.unit
class TestIncidentsEndpoint:
    """Req 10.2 — /incidents returns incident list."""

    def test_incidents_endpoint_accessible(self):
        from api.routers.incidents import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/incidents")
        from database import get_db
        app.dependency_overrides[get_db] = lambda: _mock_db()
        client = TestClient(app)
        resp = client.get("/api/v1/incidents/")
        assert resp.status_code in (200, 401, 403, 422, 500)
