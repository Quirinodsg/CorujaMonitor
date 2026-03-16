"""
Vault Client - Integração com HashiCorp Vault e Azure Key Vault
"""
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class VaultClient:
    """
    Cliente unificado para HashiCorp Vault e Azure Key Vault.
    Detecta automaticamente qual backend usar via variáveis de ambiente.
    """

    def __init__(self):
        self._backend = self._detect_backend()
        logger.info(f"VaultClient: backend={self._backend or 'none'}")

    def _detect_backend(self) -> Optional[str]:
        if os.environ.get("VAULT_ADDR"):
            return "hashicorp"
        if os.environ.get("AZURE_KEYVAULT_URL"):
            return "azure"
        return None

    def get_secret(self, path: str) -> Optional[str]:
        if self._backend == "hashicorp":
            return self._hashicorp_get(path)
        elif self._backend == "azure":
            return self._azure_get(path)
        return None

    def _hashicorp_get(self, path: str) -> Optional[str]:
        try:
            import hvac
            client = hvac.Client(
                url=os.environ["VAULT_ADDR"],
                token=os.environ.get("VAULT_TOKEN"),
            )
            secret = client.secrets.kv.v2.read_secret_version(path=path)
            data = secret["data"]["data"]
            return data.get("value") or data.get("password") or str(data)
        except ImportError:
            logger.warning("VaultClient: hvac não instalado")
        except Exception as e:
            logger.error(f"VaultClient HashiCorp erro: {e}")
        return None

    def _azure_get(self, secret_name: str) -> Optional[str]:
        try:
            from azure.keyvault.secrets import SecretClient
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            client = SecretClient(
                vault_url=os.environ["AZURE_KEYVAULT_URL"],
                credential=credential,
            )
            secret = client.get_secret(secret_name)
            return secret.value
        except ImportError:
            logger.warning("VaultClient: azure-keyvault-secrets não instalado")
        except Exception as e:
            logger.error(f"VaultClient Azure erro: {e}")
        return None

    def is_available(self) -> bool:
        return self._backend is not None
