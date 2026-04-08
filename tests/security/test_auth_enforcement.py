"""
Auth Enforcement Tests — Coruja Monitor v3.0
Tests: protected endpoints return 401 without valid token.
Requirements: 16.1
"""
import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from api.auth import get_current_user, decode_token, create_access_token


@pytest.mark.security
class TestAuthEnforcement:
    """Req 16.1 — protected endpoints require valid JWT."""

    def test_decode_invalid_token_raises(self):
        """Invalid JWT raises HTTPException 401."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_decode_expired_token_raises(self):
        """Expired JWT raises HTTPException 401."""
        from datetime import timedelta
        from fastapi import HTTPException
        token = create_access_token(
            data={"sub": "1", "tenant_id": 1},
            expires_delta=timedelta(seconds=-10),
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_valid_token_decodes_successfully(self):
        """Valid JWT decodes to payload with sub claim."""
        token = create_access_token(data={"sub": "42", "tenant_id": 1})
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["tenant_id"] == 1

    def test_no_bearer_token_returns_401(self):
        """Endpoint with HTTPBearer dependency returns 401/403 without token."""
        from api.auth import security
        app = FastAPI()

        @app.get("/protected")
        async def protected(creds=Depends(security)):
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/protected")
        assert resp.status_code in (401, 403)
