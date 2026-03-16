"""
Registry Engine - Leitura de chaves Windows Registry via winreg
Retorna status=unknown com error="engine_unavailable" se winreg não disponível.
"""
import logging
from typing import Optional

from .base_engine import BaseProtocolEngine, EngineResult

logger = logging.getLogger(__name__)

try:
    import winreg
    _WINREG_AVAILABLE = True
except ImportError:
    _WINREG_AVAILABLE = False

# Mapeamento de hives
_HIVES = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE if _WINREG_AVAILABLE else None,
    "HKCU": winreg.HKEY_CURRENT_USER if _WINREG_AVAILABLE else None,
    "HKCR": winreg.HKEY_CLASSES_ROOT if _WINREG_AVAILABLE else None,
    "HKU":  winreg.HKEY_USERS if _WINREG_AVAILABLE else None,
} if _WINREG_AVAILABLE else {}


class RegistryEngine(BaseProtocolEngine):
    """
    Engine para leitura de chaves do Windows Registry.
    Suporta leitura local (winreg) e remota (via RegConnectRegistry).

    kwargs esperados em execute():
        key_path (str): caminho completo, ex: "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
        value_name (str): nome do valor a ler (None = valor padrão)
        remote_host (str): hostname para leitura remota (None = local)
    """

    def is_available(self) -> bool:
        return _WINREG_AVAILABLE

    def execute(self, host: str, **kwargs) -> EngineResult:
        if not _WINREG_AVAILABLE:
            return self._unavailable_result()

        key_path: str = kwargs.get("key_path", "")
        value_name: Optional[str] = kwargs.get("value_name", None)
        remote_host: Optional[str] = kwargs.get("remote_host", None) or (host if host not in ("localhost", "127.0.0.1", "") else None)

        if not key_path:
            return EngineResult(status="unknown", error="key_path_required")

        try:
            hive_name, subkey = self._split_key(key_path)
            hive = _HIVES.get(hive_name)
            if hive is None:
                return EngineResult(status="unknown", error=f"unknown_hive:{hive_name}")

            # Conexão remota se necessário
            if remote_host:
                reg_handle = winreg.ConnectRegistry(remote_host, hive)
            else:
                reg_handle = hive

            with winreg.OpenKey(reg_handle, subkey, 0, winreg.KEY_READ) as key:
                if value_name is not None:
                    data, reg_type = winreg.QueryValueEx(key, value_name)
                else:
                    data, reg_type = winreg.QueryValueEx(key, "")

            # Tentar converter para float para o campo value
            try:
                numeric_value = float(data)
            except (TypeError, ValueError):
                numeric_value = 1.0  # presente = 1

            return EngineResult(
                status="ok",
                value=numeric_value,
                unit="registry",
                metadata={
                    "key_path": key_path,
                    "value_name": value_name,
                    "data": str(data),
                    "reg_type": reg_type,
                    "host": host,
                },
            )

        except FileNotFoundError:
            return EngineResult(
                status="critical",
                error="key_not_found",
                metadata={"key_path": key_path, "value_name": value_name},
            )
        except PermissionError:
            return EngineResult(
                status="unknown",
                error="access_denied",
                metadata={"key_path": key_path},
            )
        except Exception as e:
            logger.warning(f"RegistryEngine error for {host}/{key_path}: {e}")
            return EngineResult(
                status="unknown",
                error=str(e),
                metadata={"key_path": key_path},
            )

    def _split_key(self, key_path: str):
        """Separa hive do subkey. Ex: 'HKLM\\SOFTWARE\\...' → ('HKLM', 'SOFTWARE\\...')"""
        parts = key_path.replace("/", "\\").split("\\", 1)
        hive = parts[0].upper()
        subkey = parts[1] if len(parts) > 1 else ""
        return hive, subkey
