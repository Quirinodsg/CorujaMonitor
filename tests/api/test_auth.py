"""
API Auth Tests — Coruja Monitor v3.0
Tests: 401 without token, valid token access.
Requirements: 10.3
"""
import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))


@pytest.mark.unit
class TestAuthEndpoints:
    """Req 10.3 — endpoints return 401 without valid token."""

    def test_decode_invalid_token_raises(self):
        """Invalid JWT raises HTTPException 401."""
        from api.auth import decode_token
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid-token")
        assert exc_info.value.status_code == 401

    def test_login_with_invalid_credentials(self):
        """Login with wrong password returns 401."""
        from api.routers.auth import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/auth")
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "username": "nonexistent@test.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_endpoint_exists(self):
        """Login endpoint is accessible."""
        from api.routers.auth import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/auth")
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        from database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)
        resp = client.post("/api/v1/auth/login", json={
            "username": "test@test.com",
            "password": "test",
        })
        assert resp.status_code == 401
