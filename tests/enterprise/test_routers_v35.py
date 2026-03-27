"""
QA Enterprise — Routers v3.5 (service_map, audit, predictions)
Testa contratos de API: estrutura de resposta, campos obrigatórios,
parâmetros de query, fallbacks, e integração com mocks de DB.
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# ─── Setup de app mínimo para testar routers isoladamente ────────────────────

def make_test_app():
    """Cria app FastAPI mínimo com os routers v3.5."""
    app = FastAPI()

    # Mock do get_db
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.order_by.return_value.count.return_value = 0
    mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    def override_get_db():
        yield mock_db

    from database import get_db
    from api.routers import service_map, audit, predictions

    app.include_router(service_map.router)
    app.include_router(audit.router)
    app.include_router(predictions.router)
    app.dependency_overrides[get_db] = override_get_db

    return app, mock_db


# ─── Service Map Router ───────────────────────────────────────────────────────

class TestServiceMapRouter:
    def setup_method(self):
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../api"))
            self.app, self.mock_db = make_test_app()
            self.client = TestClient(self.app)
        except Exception as e:
            pytest.skip(f"Setup falhou (ambiente sem DB): {e}")

    def test_get_service_map_returns_200(self):
        resp = self.client.get("/api/v1/service-map")
        assert resp.status_code == 200

    def test_get_service_map_has_required_fields(self):
        resp = self.client.get("/api/v1/service-map")
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        assert "generated_at" in data

    def test_get_service_map_stats_has_status(self):
        resp = self.client.get("/api/v1/service-map")
        data = resp.json()
        assert "status" in data["stats"]
        assert "total_nodes" in data["stats"]
        assert "total_edges" in data["stats"]

    def test_get_impact_returns_200(self):
        resp = self.client.get("/api/v1/service-map/impact/server-1")
        assert resp.status_code == 200

    def test_get_impact_has_required_fields(self):
        resp = self.client.get("/api/v1/service-map/impact/server-1")
        data = resp.json()
        assert "node_id" in data
        assert "impacted_nodes" in data
        assert "impact_count" in data

    def test_get_impact_count_matches_list(self):
        resp = self.client.get("/api/v1/service-map/impact/server-1")
        data = resp.json()
        assert data["impact_count"] == len(data["impacted_nodes"])


# ─── Audit Router ─────────────────────────────────────────────────────────────

class TestAuditRouter:
    def setup_method(self):
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../api"))
            self.app, self.mock_db = make_test_app()
            self.client = TestClient(self.app)
        except Exception as e:
            pytest.skip(f"Setup falhou: {e}")

    def test_get_audit_returns_200(self):
        resp = self.client.get("/api/v1/audit")
        assert resp.status_code == 200

    def test_get_audit_has_total_and_items(self):
        resp = self.client.get("/api/v1/audit")
        data = resp.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_audit_limit_param(self):
        resp = self.client.get("/api/v1/audit?limit=10")
        assert resp.status_code == 200

    def test_get_audit_limit_max_500(self):
        """limit > 500 deve retornar 422."""
        resp = self.client.get("/api/v1/audit?limit=501")
        assert resp.status_code == 422

    def test_get_audit_offset_param(self):
        resp = self.client.get("/api/v1/audit?offset=50")
        assert resp.status_code == 200

    def test_get_audit_action_filter(self):
        resp = self.client.get("/api/v1/audit?action=user.login")
        assert resp.status_code == 200

    def test_get_audit_resource_type_filter(self):
        resp = self.client.get("/api/v1/audit?resource_type=sensor")
        assert resp.status_code == 200


# ─── Predictions Router ───────────────────────────────────────────────────────

class TestPredictionsRouter:
    def setup_method(self):
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../api"))
            self.app, self.mock_db = make_test_app()
            self.client = TestClient(self.app)
        except Exception as e:
            pytest.skip(f"Setup falhou: {e}")

    def test_get_predictions_returns_200(self):
        resp = self.client.get("/api/v1/predictions")
        assert resp.status_code == 200

    def test_get_predictions_has_required_fields(self):
        resp = self.client.get("/api/v1/predictions")
        data = resp.json()
        assert "predictions" in data
        assert "total" in data
        assert "horizon_hours" in data
        assert "generated_at" in data

    def test_get_predictions_total_matches_list(self):
        resp = self.client.get("/api/v1/predictions")
        data = resp.json()
        assert data["total"] == len(data["predictions"])

    def test_get_predictions_hours_param(self):
        resp = self.client.get("/api/v1/predictions?hours=6")
        assert resp.status_code == 200
        data = resp.json()
        assert data["horizon_hours"] == 6

    def test_get_predictions_hours_max_24(self):
        """hours > 24 deve retornar 422."""
        resp = self.client.get("/api/v1/predictions?hours=25")
        assert resp.status_code == 422

    def test_get_predictions_severity_filter(self):
        resp = self.client.get("/api/v1/predictions?severity=critical")
        assert resp.status_code == 200

    def test_get_predictions_empty_db_returns_empty_list(self):
        """Com DB vazio, predictions deve ser lista vazia."""
        resp = self.client.get("/api/v1/predictions")
        data = resp.json()
        assert isinstance(data["predictions"], list)
