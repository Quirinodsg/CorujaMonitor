"""
Credential Encryption Tests — Coruja Monitor v3.0
Tests: Fernet encryption round-trip.
Requirements: 16.3
"""
import pytest
import json
from pathlib import Path
from cryptography.fernet import Fernet

from probe.security.credential_manager import CredentialManager


@pytest.mark.security
class TestCredentialEncryption:
    """Req 16.3 — Fernet encryption round-trip for credentials."""

    def test_fernet_encrypt_decrypt_roundtrip(self):
        """Encrypt then decrypt returns original credential."""
        key = Fernet.generate_key()
        f = Fernet(key)
        original = "my_secret_password_123!"
        encrypted = f.encrypt(original.encode())
        decrypted = f.decrypt(encrypted).decode()
        assert decrypted == original

    def test_credential_manager_set_get(self, tmp_path):
        """CredentialManager stores and retrieves credentials."""
        key = Fernet.generate_key()
        cred_file = tmp_path / "creds.enc"
        mgr = CredentialManager(key=key, credentials_file=cred_file)
        mgr.set("db_server", {"username": "admin", "password": "secret123"})
        result = mgr.get("db_server")
        assert result["username"] == "admin"
        assert result["password"] == "secret123"

    def test_credential_manager_persistence(self, tmp_path):
        """Credentials persist across manager instances."""
        key = Fernet.generate_key()
        cred_file = tmp_path / "creds.enc"
        mgr1 = CredentialManager(key=key, credentials_file=cred_file)
        mgr1.set("wmi_host", {"user": "admin", "pass": "p@ss"})

        mgr2 = CredentialManager(key=key, credentials_file=cred_file)
        result = mgr2.get("wmi_host")
        assert result["user"] == "admin"

    def test_credential_manager_delete(self, tmp_path):
        """Deleted credentials are no longer retrievable."""
        key = Fernet.generate_key()
        cred_file = tmp_path / "creds.enc"
        mgr = CredentialManager(key=key, credentials_file=cred_file)
        mgr.set("temp", {"key": "value"})
        mgr.delete("temp")
        assert mgr.get("temp") is None

    def test_validate_integrity(self, tmp_path):
        """Integrity validation passes for valid encrypted file."""
        key = Fernet.generate_key()
        cred_file = tmp_path / "creds.enc"
        mgr = CredentialManager(key=key, credentials_file=cred_file)
        mgr.set("test", {"a": "b"})
        assert mgr.validate_integrity() is True
