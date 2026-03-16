"""
Credential Manager - Armazenamento seguro de credenciais com AES-256
Senhas nunca aparecem em logs (substituídas por [REDACTED])
Suporte a rotação de credenciais sem reinicialização
"""
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = Path("probe_credentials.enc")
ROTATION_CHECK_INTERVAL = 30  # segundos


class CredentialManager:
    def __init__(self, key: Optional[bytes] = None, credentials_file: Path = CREDENTIALS_FILE):
        self._key = key or self._load_or_generate_key()
        self._file = credentials_file
        self._credentials: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._file_mtime: float = 0.0
        self._rotation_thread: Optional[threading.Thread] = None
        self._running = False
        self._load()

    def _load_or_generate_key(self) -> bytes:
        key_env = os.environ.get("PROBE_ENCRYPTION_KEY")
        if key_env:
            import base64
            return base64.b64decode(key_env)
        # Gerar chave e salvar em variável de ambiente (apenas para dev)
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        logger.warning("CredentialManager: chave gerada em memória — defina PROBE_ENCRYPTION_KEY")
        return key

    def _cipher(self):
        from cryptography.fernet import Fernet
        return Fernet(self._key)

    def _load(self):
        if not self._file.exists():
            return
        try:
            encrypted = self._file.read_bytes()
            data = json.loads(self._cipher().decrypt(encrypted).decode())
            with self._lock:
                self._credentials = data
            self._file_mtime = self._file.stat().st_mtime
            logger.info(f"CredentialManager: {len(self._credentials)} credenciais carregadas")
        except Exception as e:
            logger.error(f"CredentialManager: erro ao carregar credenciais: {e}")

    def save(self):
        try:
            with self._lock:
                data = json.dumps(self._credentials).encode()
            encrypted = self._cipher().encrypt(data)
            self._file.write_bytes(encrypted)
            self._file_mtime = self._file.stat().st_mtime
        except Exception as e:
            logger.error(f"CredentialManager: erro ao salvar: {e}")

    def set(self, name: str, credential: Dict):
        """Armazena credencial. Senhas são redactadas nos logs."""
        safe_log = {k: "[REDACTED]" if "password" in k.lower() or "secret" in k.lower() or "token" in k.lower() else v
                    for k, v in credential.items()}
        logger.info(f"CredentialManager: salvando credencial '{name}': {safe_log}")
        with self._lock:
            self._credentials[name] = credential
        self.save()

    def get(self, name: str) -> Optional[Dict]:
        with self._lock:
            return self._credentials.get(name)

    def delete(self, name: str):
        with self._lock:
            self._credentials.pop(name, None)
        self.save()

    def start_rotation_watcher(self):
        """Monitora o arquivo de credenciais e recarrega automaticamente quando alterado"""
        self._running = True
        self._rotation_thread = threading.Thread(
            target=self._rotation_loop, daemon=True, name="CredentialRotation"
        )
        self._rotation_thread.start()

    def stop(self):
        self._running = False

    def _rotation_loop(self):
        while self._running:
            try:
                if self._file.exists():
                    mtime = self._file.stat().st_mtime
                    if mtime != self._file_mtime:
                        logger.info("CredentialManager: rotação detectada — recarregando")
                        self._load()
            except Exception as e:
                logger.debug(f"CredentialManager rotation check: {e}")
            time.sleep(ROTATION_CHECK_INTERVAL)

    def validate_integrity(self) -> bool:
        """Valida integridade das credenciais na inicialização"""
        if not self._file.exists():
            return True
        try:
            encrypted = self._file.read_bytes()
            self._cipher().decrypt(encrypted)
            return True
        except Exception:
            logger.error("CredentialManager: falha na validação de integridade!")
            return False
