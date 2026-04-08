"""
Token Expiry Tests — Coruja Monitor v3.0
Tests: JWT token expiration.
Requirements: 16.5
"""
import sys
import os
import pytest
from datetime import timedelta
from fastapi import HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from api.auth import create_access_token, decode_token


@pytest.mark.security
class TestTokenExpiry:
    """Req 16.5 — JWT tokens expire correctly."""

    def test_token_with_short_expiry_expires(self):
        """Token with negative expiry is immediately expired."""
        token = create_access_token(
            data={"sub": "1", "tenant_id": 1},
            expires_delta=timedelta(seconds=-60),
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_token_with_long_expiry_valid(self):
        """Token with future expiry is valid."""
        token = create_access_token(
            data={"sub": "1", "tenant_id": 1},
            expires_delta=timedelta(hours=1),
        )
        payload = decode_token(token)
        assert payload["sub"] == "1"

    def test_token_contains_exp_claim(self):
        """Generated token contains exp claim."""
        token = create_access_token(data={"sub": "1", "tenant_id": 1})
        payload = decode_token(token)
        assert "exp" in payload

    def test_token_sub_is_string(self):
        """Token sub claim is always a string."""
        token = create_access_token(data={"sub": 42, "tenant_id": 1})
        payload = decode_token(token)
        assert isinstance(payload["sub"], str)
