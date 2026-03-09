"""
WMI Remote Collector - Coleta métricas de servidores Windows remotos via WMI
Requer credenciais de administrador no servidor remoto
"""
import logging
from typing import List, Dict, Any, Optional
import subprocess
import json

logger = logging.getLogger(__name__)

class WMIRemoteCollector:
    """
    Coletor de métricas via WMI remoto (agentless)
    
    Requisitos no servidor remoto:
    - WMI habilitado
    - Firewall liberado (portas 135, 445)
    - Usuário com permissões de administrador
    - Compartilhamento administrativo habilitado
    """
    
    def __init__(self, hostname: str, username: str, password: str, domain: str = ""):
        """
        Args:
            hostname: Nome ou IP do servidor remoto
            username: Usuário administrador (ex: Administrator ou DOMAIN\\user)
            password: Senha do usuário
            domain: Domínio (opcional, pode estar no username)
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.domain = domain
        
        # Formatar credenciais
        if domain and '\\' not in username:
            self.full_username = f"{domain}\\{username}"
        else:
            self.full_username = username
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Testa conexão WMI com o servidor remoto
        Returns: (sucesso, mensagem)
        """
        try:
            result = self._execute_wmi_query(
                "SELECT Caption FROM Win32_OperatingSystem"
            )
            if result:
                return True, f"Conexão OK: {result[0].get('Caption', 'Unknown')}"
            return False, "Sem resposta do servidor"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
    
    def collect_cpu(self) -> List[Dict[str, Any]]:
        """Coleta métricas de CPU via WMI"""
        try:
            # Query WMI para CPU
            query = "SELECT LoadPercentage, NumberOfLogicalProcessors FROM Win32_Processor"
            results = self._execute_wmi_query(query)
            
            if not results:
                return []
            
            # Calcular média de uso de CPU
            total_load = sum(float(r.get('LoadPercentage', 0)) for r in results)
            avg_load = total_load / len(results) if results else 0
            cpu_count = results[0].get('NumberOfLogicalProcessors', 0)
            
            return [{
                "type": "cpu",
                "name": "cpu_usage",
                "value": avg_load,
                "unit": "percent",
                "status": self._get_status(avg_load, 80, 95),
                "metadata": {
                    "cpu_count": cpu_count,
                    "collection_method": "wmi_remote"
                }
            }]
        except Exception as e:
            logger.error(f"Erro ao coletar CPU via WMI: {e}")
            return []
    
    def collect_memory(self) -> List[Dict[str, Any]]:
        """Coleta métricas de memória via WMI"""
        try:
            # Query WMI para memória
            query = "SELECT TotalVisibleMemorySize, FreePhysicalMemory FROM Win32_OperatingSystem"
            results = self._execute_wmi_query(query)
            
            if not results or not results[0]:
                return []
            
            data = results[0]
            total_kb = float(data.get('TotalVisibleMemorySize', 0))
            free_kb = float(data.get('FreePhysicalMemory', 0))
            
            if total_kb == 0:
                return []
            
            used_kb = total_kb - free_kb
            usage_percent = (used_kb / total_kb) * 100
            
            return [{
                "type": "memory",
                "name": "memory_usage",
                "value": usage_percent,
                "unit": "percent",
                "status": self._get_status(usage_percent, 80, 95),
                "metadata": {
                    "total_mb": total_kb / 1024,
                    "used_mb": used_kb / 1024,
                    "free_mb": free_kb / 1024,
                    "collection_method": "wmi_remote"
                }
            }]
        except Exception as e:
            logger.error(f"Erro ao coletar memória via WMI: {e}")
            return []
    
    def collect_disk(self) -> List[Dict[str, Any]]:
        """Coleta métricas de disco via WMI"""
        try:
            # Query WMI para discos
            query = "SELECT DeviceID, Size, FreeSpace FROM Win32_LogicalDisk WHERE DriveType=3"
            results = self._execute_wmi_query(query)
            
            if not results:
                return []
            
            metrics = []
            for disk in results:
                device_id = disk.get('DeviceID', 'Unknown')
                size = float(disk.get('Size', 0))
                free = float(disk.get('FreeSpace', 0))
                
                if size == 0:
                    continue
                
                used = size - free
                usage_percent = (used / size) * 100
                
                metrics.append({
                    "type": "disk",
                    "name": f"disk_{device_id.replace(':', '')}",
                    "value": usage_percent,
                    "unit": "percent",
                    "status": self._get_status(usage_percent, 80, 95),
                    "metadata": {
                        "device": device_id,
                        "total_gb": size / (1024**3),
                        "used_gb": used / (1024**3),
                        "free_gb": free / (1024**3),
                        "collection_method": "wmi_remote"
                    }
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao coletar disco via WMI: {e}")
            return []
    
    def collect_services(self, service_names: List[str]) -> List[Dict[str, Any]]:
        """Coleta status de serviços via WMI"""
        try:
            if not service_names:
                return []
            
            # Criar filtro para serviços específicos
            service_filter = " OR ".join([f"Name='{name}'" for name in service_names])
            query = f"SELECT Name, State, Status FROM Win32_Service WHERE {service_filter}"
            results = self._execute_wmi_query(query)
            
            if not results:
                return []
            
            metrics = []
            for service in results:
                name = service.get('Name', 'Unknown')
                state = service.get('State', 'Unknown')
                status = service.get('Status', 'Unknown')
                
                # State: Running, Stopped, Paused, etc
                # Status: OK, Degraded, Error, etc
                is_running = state.lower() == 'running'
                
                metrics.append({
                    "type": "service",
                    "name": f"service_{name}",
                    "value": 1 if is_running else 0,
                    "unit": "status",
                    "status": "ok" if is_running else "critical",
                    "metadata": {
                        "service_name": name,
                        "state": state,
                        "status": status,
                        "collection_method": "wmi_remote"
                    }
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao coletar serviços via WMI: {e}")
            return []
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Coleta informações do sistema via WMI"""
        try:
            # Sistema operacional
            os_query = "SELECT Caption, Version, OSArchitecture FROM Win32_OperatingSystem"
            os_results = self._execute_wmi_query(os_query)
            
            # Computador
            cs_query = "SELECT Name, Domain FROM Win32_ComputerSystem"
            cs_results = self._execute_wmi_query(cs_query)
            
            info = {}
            if os_results and os_results[0]:
                info['os_name'] = os_results[0].get('Caption', 'Unknown')
                info['os_version'] = os_results[0].get('Version', 'Unknown')
                info['os_architecture'] = os_results[0].get('OSArchitecture', 'Unknown')
            
            if cs_results and cs_results[0]:
                info['hostname'] = cs_results[0].get('Name', 'Unknown')
                info['domain'] = cs_results[0].get('Domain', 'WORKGROUP')
            
            return info
        except Exception as e:
            logger.error(f"Erro ao coletar info do sistema via WMI: {e}")
            return {}
    
    def discover_services(self) -> List[Dict[str, Any]]:
        """
        Descobre TODOS os serviços Windows no servidor remoto
        Retorna lista completa com nome, display name, status e tipo de inicialização
        """
        try:
            query = "SELECT Name, DisplayName, State, StartMode FROM Win32_Service"
            results = self._execute_wmi_query(query)
            
            if not results:
                logger.warning(f"Nenhum serviço encontrado em {self.hostname}")
                return []
            
            services = []
            for service in results:
                name = service.get('Name', '').strip()
                display_name = service.get('DisplayName', name).strip()
                state = service.get('State', 'Unknown').strip()
                start_mode = service.get('StartMode', 'Unknown').strip()
                
                if not name:
                    continue
                
                services.append({
                    "name": name,
                    "display_name": display_name,
                    "status": state.lower(),  # running, stopped, paused
                    "start_type": start_mode.lower()  # auto, manual, disabled
                })
            
            # Ordenar por display name
            services.sort(key=lambda x: x['display_name'].lower())
            
            logger.info(f"Descobertos {len(services)} serviços em {self.hostname}")
            return services
            
        except Exception as e:
            logger.error(f"Erro ao descobrir serviços via WMI: {e}")
            return []
    
    def discover_disks(self) -> List[Dict[str, Any]]:
        """
        Descobre TODOS os discos no servidor remoto
        Retorna lista completa com letra, nome, tamanho e uso
        """
        try:
            query = "SELECT DeviceID, VolumeName, Size, FreeSpace FROM Win32_LogicalDisk WHERE DriveType=3"
            results = self._execute_wmi_query(query)
            
            if not results:
                logger.warning(f"Nenhum disco encontrado em {self.hostname}")
                return []
            
            disks = []
            for disk in results:
                device_id = disk.get('DeviceID', '').strip()
                volume_name = disk.get('VolumeName', '').strip()
                size = float(disk.get('Size', 0))
                free = float(disk.get('FreeSpace', 0))
                
                if not device_id or size == 0:
                    continue
                
                used = size - free
                percent_used = (used / size) * 100
                
                # Nome amigável
                if volume_name:
                    display_name = f"{volume_name} ({device_id})"
                else:
                    display_name = f"Disco Local ({device_id})"
                
                disks.append({
                    "name": device_id,
                    "display_name": display_name,
                    "total_gb": round(size / (1024**3), 2),
                    "used_gb": round(used / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "percent_used": round(percent_used, 1)
                })
            
            # Ordenar por letra
            disks.sort(key=lambda x: x['name'])
            
            logger.info(f"Descobertos {len(disks)} discos em {self.hostname}")
            return disks
            
        except Exception as e:
            logger.error(f"Erro ao descobrir discos via WMI: {e}")
            return []
    
    def _execute_wmi_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executa query WMI usando wmic.exe (Windows) ou wmi-client (Linux)
        
        IMPORTANTE: Esta é uma implementação básica usando wmic.exe
        Para produção, considere usar bibliotecas como:
        - pypsrp (PowerShell Remoting)
        - wmi-client-wrapper (Linux)
        - impacket (Cross-platform)
        """
        try:
            # Comando wmic para Windows
            # Formato: wmic /node:hostname /user:username /password:password query
            cmd = [
                'wmic',
                f'/node:{self.hostname}',
                f'/user:{self.full_username}',
                f'/password:{self.password}',
                query,
                '/format:csv'
            ]
            
            # Executar comando
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Erro wmic: {result.stderr}")
                return []
            
            # Parse CSV output
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []
            
            # Primeira linha é o header
            headers = lines[0].split(',')
            
            # Linhas seguintes são os dados
            results = []
            for line in lines[1:]:
                if not line.strip():
                    continue
                values = line.split(',')
                row = dict(zip(headers, values))
                results.append(row)
            
            return results
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao executar WMI query no host {self.hostname}")
            return []
        except Exception as e:
            logger.error(f"Erro ao executar WMI query: {e}")
            return []
    
    def _get_status(self, value: float, warning: float, critical: float) -> str:
        """Determina status baseado em thresholds"""
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
