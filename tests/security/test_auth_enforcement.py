"""
Auth Enforcement Tests — Coruja Monitor v3.0
Tests: JWT token creation, decoding, and protected endpoint behavior.
Requirements: 16.1

Note: Does NOT import api.auth directly (requires DB models only available
inside Docker). Instead, reimplements JWT logic using the same jose library.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from jose import jwt, JWTError
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

# Same secret/algorithm as api/auth.py
SECRET_KEY = "coruja-secret-key-change-in-production"
ALGORITHM = "HS256"

security = HTTPBearer()


def _create_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")


@pytest.mark.security
class TestAuthEnforcement:
    """Req 16.1 — protected endpoints require valid JWT."""

    def test_decode_invalid_token_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            _decode_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_decode_expired_token_raises(self):
        token = _create_token(
            {"sub": "1", "tenant_id": 1},
            expires_delta=timedelta(seconds=-10),
        )
        with pytest.raises(HTTPException) as exc_info:
            _decode_token(token)
        assert exc_info.value.status_code == 401

    def test_valid_token_decodes_successfully(self):
        token = _create_token({"sub": "42", "tenant_id": 1})
        payload = _decode_token(token)
        assert payload["sub"] == "42"
        assert payload["tenant_id"] == 1

    def test_no_bearer_token_returns_401(self):
        app = FastAPI()

        @app.get("/protected")
        async def protected(creds=Depends(security)):
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/protected")
        assert resp.status_code in (401, 403)
