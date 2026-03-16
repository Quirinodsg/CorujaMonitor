"""
Remote Registry Collector - Coleta métricas via Remote Registry
Alternativa ao WMI para coletar dados de performance sem executar queries WMI.
Usa winreg para acessar HKLM remotamente via RPC.

Chaves utilizadas:
  HKLM\SYSTEM\CurrentControlSet\Services  → status de serviços
  HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Perflib → contadores de perf
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Chaves de registro relevantes
REG_SERVICES_KEY = r"SYSTEM\CurrentControlSet\Services"
REG_PERFLIB_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Perflib"
REG_OS_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
REG_PERF_DATA = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Perflib\009"


class RemoteRegistryCollector:
    """
    Coleta métricas via Remote Registry (winreg).
    Mais leve que WMI para dados simples como versão do OS e status de serviços.
    
    Requer:
    - Serviço "Remote Registry" ativo no host alvo
    - Permissão de leitura no registro remoto
    - Porta 445 (SMB) aberta
    """

    def __init__(self, hostname: str, username: str = None, password: str = None, domain: str = None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.domain = domain
        self._reg = None

    def _connect(self) -> bool:
        """Conecta ao registro remoto via winreg"""
        try:
            import winreg
            self._winreg = winreg

            # winreg.ConnectRegistry usa credenciais do processo atual (conta de serviço)
            # Para credenciais explícitas, precisaria de win32api.LogonUser primeiro
            self._reg = winreg.ConnectRegistry(self.hostname, winreg.HKEY_LOCAL_MACHINE)
            logger.info(f"✅ Remote Registry conectado em {self.hostname}")
            return True

        except ImportError:
            logger.warning("winreg não disponível (não é Windows)")
            return False
        except Exception as e:
            logger.error(f"❌ Falha ao conectar Remote Registry em {self.hostname}: {e}")
            return False

    def collect_os_info(self) -> Dict[str, Any]:
        """Coleta informações do OS via registro"""
        if not self._reg and not self._connect():
            return {}

        try:
            key = self._winreg.OpenKey(self._reg, REG_OS_KEY)
            info = {}

            fields = [
                ("ProductName", "os_name"),
                ("CurrentBuildNumber", "build_number"),
                ("ReleaseId", "release_id"),
                ("DisplayVersion", "display_version"),
                ("CurrentVersion", "os_version"),
            ]

            for reg_name, field_name in fields:
                try:
                    value, _ = self._winreg.QueryValueEx(key, reg_name)
                    info[field_name] = value
                except FileNotFoundError:
                    pass

            self._winreg.CloseKey(key)
            return info

        except Exception as e:
            logger.error(f"Erro ao coletar OS info via registry: {e}")
            return {}

    def collect_service_status(self, service_names: List[str]) -> List[Dict[str, Any]]:
        """
        Coleta status de serviços específicos via registro.
        Mais rápido que WMI Win32_Service para verificações simples.
        """
        if not self._reg and not self._connect():
            return []

        metrics = []

        for svc_name in service_names:
            try:
                key_path = f"{REG_SERVICES_KEY}\\{svc_name}"
                key = self._winreg.OpenKey(self._reg, key_path)

                # Start type: 0=Boot, 1=System, 2=Auto, 3=Manual, 4=Disabled
                try:
                    start_type, _ = self._winreg.QueryValueEx(key, "Start")
                except FileNotFoundError:
                    start_type = -1

                # ImagePath para confirmar que serviço existe
                try:
                    image_path, _ = self._winreg.QueryValueEx(key, "ImagePath")
                    exists = True
                except FileNotFoundError:
                    image_path = ""
                    exists = False

                self._winreg.CloseKey(key)

                start_type_map = {0: "Boot", 1: "System", 2: "Auto", 3: "Manual", 4: "Disabled"}

                metrics.append({
                    "type": "registry_service",
                    "name": f"Service {svc_name}",
                    "host": self.hostname,
                    "value": 1 if exists else 0,
                    "unit": "state",
                    "status": "ok" if exists and start_type != 4 else "warning",
                    "metadata": {
                        "service_name": svc_name,
                        "start_type": start_type_map.get(start_type, "Unknown"),
                        "image_path": image_path,
                        "collection_method": "remote_registry",
                    },
                })

            except FileNotFoundError:
                metrics.append({
                    "type": "registry_service",
                    "name": f"Service {svc_name}",
                    "host": self.hostname,
                    "value": 0,
                    "unit": "state",
                    "status": "critical",
                    "metadata": {
                        "service_name": svc_name,
                        "error": "service_not_found",
                        "collection_method": "remote_registry",
                    },
                })
            except Exception as e:
                logger.error(f"Erro ao coletar serviço {svc_name} via registry: {e}")

        return metrics

    def collect_perflib_counters(self) -> Dict[str, Any]:
        """
        Lê contadores de performance via Perflib no registro.
        Alternativa leve ao WMI para dados de CPU/Memória.
        """
        if not self._reg and not self._connect():
            return {}

        try:
            # Perflib\009 contém os nomes dos contadores em inglês
            key = self._winreg.OpenKey(self._reg, REG_PERF_DATA)
            try:
                counter_names, _ = self._winreg.QueryValueEx(key, "Counter")
                # counter_names é uma lista alternada: [id, name, id, name, ...]
                counters = {}
                if isinstance(counter_names, (list, tuple)):
                    for i in range(0, len(counter_names) - 1, 2):
                        counters[counter_names[i]] = counter_names[i + 1]
                return {"perflib_counters_available": True, "counter_count": len(counters)}
            finally:
                self._winreg.CloseKey(key)

        except Exception as e:
            logger.debug(f"Perflib não acessível via registry: {e}")
            return {"perflib_counters_available": False}

    def close(self):
        if self._reg:
            try:
                self._winreg.CloseKey(self._reg)
            except Exception:
                pass
            self._reg = None
