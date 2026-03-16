"""
WMI Native Collector - Usa WMI nativo (DCOM/RPC) como PRTG
Funciona automaticamente no domínio sem configuração adicional
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class WMINativeCollector:
    """
    Coletor WMI nativo usando DCOM/RPC (igual ao PRTG)
    
    Vantagens:
    - Funciona automaticamente no domínio
    - Não precisa habilitar WinRM
    - Usa Kerberos automaticamente
    - Mesma tecnologia do PRTG
    
    Requisitos:
    - Probe no domínio
    - Usuário Domain Admin
    - Firewall liberado para WMI (porta 135 + dinâmicas)
    """
    
    def __init__(self, hostname: str, username: str, password: str, domain: str = ""):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.domain = domain
        
        # Formatar credenciais para WMI
        if domain and '\\' not in username:
            self.full_username = f"{domain}\\{username}"
        else:
            self.full_username = username
        
        self.connection = None
    
    def connect(self) -> bool:
        """Conecta ao servidor remoto via WMI"""
        try:
            import wmi
            from engine.wmi_pool import _init_thread_com

            # CRÍTICO: inicializar COM + CoInitializeSecurity para esta thread
            _init_thread_com()

            logger.info(f"🔌 Conectando via WMI nativo em {self.hostname}")

            self.connection = wmi.WMI(
                computer=self.hostname,
                user=self.full_username,
                password=self.password,
                namespace="root/cimv2"
            )

            logger.info(f"✅ WMI nativo conectado em {self.hostname}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao conectar WMI nativo em {self.hostname}: {e}")
            return False
    
    def collect_cpu(self) -> List[Dict[str, Any]]:
        """Coleta métricas de CPU via WMI nativo"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            # Query WMI para CPU
            processors = self.connection.Win32_Processor()
            
            if not processors:
                return []
            
            # Calcular média de uso (usar is not None para não filtrar valor 0 real)
            valid_processors = [p for p in processors if p.LoadPercentage is not None]
            total_load = sum(p.LoadPercentage for p in valid_processors)
            avg_load = total_load / len(valid_processors) if valid_processors else 0
            cpu_count = processors[0].NumberOfLogicalProcessors
            
            return [{
                "type": "cpu",
                "name": "cpu_usage",
                "value": float(avg_load),
                "unit": "percent",
                "status": self._get_status(avg_load, 80, 95),
                "metadata": {
                    "cpu_count": cpu_count,
                    "collection_method": "wmi_native"
                }
            }]
            
        except Exception as e:
            logger.error(f"Erro ao coletar CPU via WMI nativo: {e}")
            return []
    
    def collect_memory(self) -> List[Dict[str, Any]]:
        """Coleta métricas de memória via WMI nativo"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            # Query WMI para memória
            os_info = self.connection.Win32_OperatingSystem()[0]
            
            total_kb = int(os_info.TotalVisibleMemorySize)
            free_kb = int(os_info.FreePhysicalMemory)
            used_kb = total_kb - free_kb
            percent_used = (used_kb / total_kb) * 100 if total_kb > 0 else 0
            
            return [{
                "type": "memory",
                "name": "memory_usage",
                "value": round(percent_used, 2),
                "unit": "percent",
                "status": self._get_status(percent_used, 80, 95),
                "metadata": {
                    "total_gb": round(total_kb / 1024 / 1024, 2),
                    "used_gb": round(used_kb / 1024 / 1024, 2),
                    "free_gb": round(free_kb / 1024 / 1024, 2),
                    "collection_method": "wmi_native"
                }
            }]
            
        except Exception as e:
            logger.error(f"Erro ao coletar memória via WMI nativo: {e}")
            return []
    
    def collect_disk(self) -> List[Dict[str, Any]]:
        """Coleta métricas de disco via WMI nativo"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            metrics = []
            
            # Query WMI para discos
            disks = self.connection.Win32_LogicalDisk(DriveType=3)  # 3 = Local Disk
            
            for disk in disks:
                if not disk.Size:
                    continue
                
                total_bytes = int(disk.Size)
                free_bytes = int(disk.FreeSpace)
                used_bytes = total_bytes - free_bytes
                percent_used = (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                
                metrics.append({
                    "type": "disk",
                    "name": f"disk_{disk.DeviceID.replace(':', '')}",
                    "value": round(percent_used, 2),
                    "unit": "percent",
                    "status": self._get_status(percent_used, 80, 95),
                    "metadata": {
                        "device": disk.DeviceID,
                        "volume_name": disk.VolumeName or "",
                        "total_gb": round(total_bytes / 1024**3, 2),
                        "used_gb": round(used_bytes / 1024**3, 2),
                        "free_gb": round(free_bytes / 1024**3, 2),
                        "collection_method": "wmi_native"
                    }
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar disco via WMI nativo: {e}")
            return []
    
    def collect_services(self) -> List[Dict[str, Any]]:
        """Coleta status de serviços via WMI nativo"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            metrics = []
            
            # Query WMI para serviços críticos
            services = self.connection.Win32_Service(StartMode="Auto")
            
            for service in services:
                state = service.State
                status = "ok" if state == "Running" else "critical"
                
                metrics.append({
                    "type": "service",
                    "name": f"service_{service.Name}",
                    "value": 1 if state == "Running" else 0,
                    "unit": "state",
                    "status": status,
                    "metadata": {
                        "service_name": service.Name,
                        "display_name": service.DisplayName,
                        "state": state,
                        "start_mode": service.StartMode,
                        "collection_method": "wmi_native"
                    }
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar serviços via WMI nativo: {e}")
            return []
    
    def collect_all(self) -> List[Dict[str, Any]]:
        """Coleta todas as métricas"""
        metrics = []
        metrics.extend(self.collect_cpu())
        metrics.extend(self.collect_memory())
        metrics.extend(self.collect_disk())
        # Serviços podem gerar muitas métricas, comentado por padrão
        # metrics.extend(self.collect_services())
        return metrics
    
    def _get_status(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Determina o status baseado nos thresholds"""
        if value >= critical_threshold:
            return "critical"
        elif value >= warning_threshold:
            return "warning"
        else:
            return "ok"
    
    def close(self):
        """Fecha a conexão WMI"""
        if self.connection:
            self.connection = None
            logger.debug(f"Conexão WMI fechada para {self.hostname}")
