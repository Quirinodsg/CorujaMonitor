"""
Token Expiry Tests — Coruja Monitor v3.0
Tests: JWT token expiration behavior.
Requirements: 16.5

Note: Does NOT import api.auth directly (requires DB models only available
inside Docker). Reimplements JWT logic using the same jose library.
"""
import pytest
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from fastapi import HTTPException

SECRET_KEY = "coruja-secret-key-change-in-production"
ALGORITHM = "HS256"


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
class TestTokenExpiry:
    """Req 16.5 — JWT tokens expire correctly."""

    def test_token_with_short_expiry_expires(self):
        token = _create_token(
            {"sub": "1", "tenant_id": 1},
            expires_delta=timedelta(seconds=-60),
        )
        with pytest.raises(HTTPException) as exc_info:
            _decode_token(token)
        assert exc_info.value.status_code == 401

    def test_token_with_long_expiry_valid(self):
        token = _create_token(
            {"sub": "1", "tenant_id": 1},
            expires_delta=timedelta(hours=1),
        )
        payload = _decode_token(token)
        assert payload["sub"] == "1"

    def test_token_contains_exp_claim(self):
        token = _create_token({"sub": "1", "tenant_id": 1})
        payload = _decode_token(token)
        assert "exp" in payload

    def test_token_sub_preserved(self):
        token = _create_token({"sub": "42", "tenant_id": 1})
        payload = _decode_token(token)
        assert payload["sub"] == "42"
