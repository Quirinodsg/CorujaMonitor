"""
Security - Gerenciamento seguro de credenciais
AES-256 local + HashiCorp Vault + Azure Key Vault
"""
from .credential_manager import CredentialManager
from .vault_client import VaultClient

__all__ = ["CredentialManager", "VaultClient"]
