"""
API v3 Endpoint Tests — Coruja Monitor v3.0
Tests: health-score, intelligent alerts, topology graph/impact.
Requirements: 10.1
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add api/ to path so that 'database', 'models', 'config', 'auth' can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from fastapi import FastAPI
from fastapi.testclient import TestClient


def _mock_db_session():
    """Create a mock DB session that returns plausible data."""
    session = MagicMock()
    sensor_row = MagicMock()
    sensor_row.total = 100
    sensor_row.ok_count = 80
    sensor_row.warning_count = 15
    sensor_row.critical_count = 5
    sensor_row.unknown_count = 0
    session.execute.return_value.fetchone.return_value = sensor_row
    session.execute.return_value.scalar.return_value = 2
    session.execute.return_value.fetchall.return_value = []
    return session


@pytest.mark.unit
class TestHealthScoreEndpoint:
    """Req 10.1 — /observability/health-score returns score 0-100."""

    def test_health_score_returns_json(self):
        from api.routers.observability import router as observability_router
        app = FastAPI()
        app.include_router(observability_router)
        mock_db = _mock_db_session()
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.get("/api/v1/observability/health-score")
        assert resp.status_code == 200
        data = resp.json()
        assert "score" in data
        assert "status" in data

    def test_health_score_error_handling(self):
        from api.routers.observability import router as observability_router
        app = FastAPI()
        app.include_router(observability_router)
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("DB error")
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.get("/api/v1/observability/health-score")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 0


@pytest.mark.unit
class TestIntelligentAlertsEndpoint:
    """Req 10.1 — /alerts/intelligent returns alert list."""

    def test_alerts_returns_list(self):
        from api.routers.observability import router as observability_router
        app = FastAPI()
        app.include_router(observability_router)
        mock_db = MagicMock()
        mock_db.execute.return_value.fetchall.return_value = []
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.get("/api/v1/alerts/intelligent")
        assert resp.status_code == 200
        data = resp.json()
        assert "alerts" in data


@pytest.mark.unit
class TestTopologyEndpoints:
    """Req 10.1 — /topology/graph and /topology/impact/{node_id}."""

    def test_topology_graph_returns_nodes_edges(self):
        from api.routers.topology import router as topology_router
        app = FastAPI()
        app.include_router(topology_router)
        mock_db = MagicMock()
        mock_db.execute.return_value.fetchall.return_value = []
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.get("/api/v1/topology/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data

    def test_topology_impact_returns_blast_radius(self):
        from api.routers.topology import router as topology_router
        app = FastAPI()
        app.include_router(topology_router)
        mock_db = MagicMock()
        mock_db.execute.return_value.fetchall.return_value = []
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.get("/api/v1/topology/impact/test-node-id")
        assert resp.status_code == 200
        data = resp.json()
        assert "node_id" in data
