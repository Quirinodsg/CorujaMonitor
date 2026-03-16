"""
WMI Remote Collector - Versão PowerShell (Moderna)
Coleta métricas de servidores Windows remotos via PowerShell Remoting
"""
import logging
from typing import List, Dict, Any
import subprocess
import json
import base64

logger = logging.getLogger(__name__)

class WMIRemoteCollector:
    """
    Coletor de métricas via PowerShell Remoting (WinRM)
    
    Requisitos no servidor remoto:
    - WinRM habilitado (Enable-PSRemoting)
    - Firewall liberado (porta 5985 HTTP ou 5986 HTTPS)
    - Usuário com permissões de administrador
    """
    
    def __init__(self, hostname: str, username: str, password: str, domain: str = ""):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.domain = domain
        
        # Formatar credenciais
        if domain and '\\' not in username:
            self.full_username = f"{domain}\\{username}"
        else:
            self.full_username = username
    
    def collect_cpu(self) -> List[Dict[str, Any]]:
        """Coleta métricas de CPU via PowerShell"""
        try:
            script = """
            $cpu = Get-WmiObject Win32_Processor
            $load = ($cpu | Measure-Object -Property LoadPercentage -Average).Average
            $cores = $cpu[0].NumberOfLogicalProcessors
            @{
                LoadPercentage = $load
                Cores = $cores
            } | ConvertTo-Json
            """
            
            result = self._execute_powershell(script)
            if not result:
                return []
            
            data = json.loads(result)
            avg_load = float(data.get('LoadPercentage', 0))
            cpu_count = int(data.get('Cores', 0))
            
            return [{
                "type": "cpu",
                "name": "cpu_usage",
                "value": avg_load,
                "unit": "percent",
                "status": self._get_status(avg_load, 80, 95),
                "metadata": {
                    "cpu_count": cpu_count,
                    "collection_method": "powershell_remote"
                }
            }]
        except Exception as e:
            logger.error(f"Erro ao coletar CPU via PowerShell: {e}")
            return []
    
    def collect_memory(self) -> List[Dict[str, Any]]:
        """Coleta métricas de memória via PowerShell"""
        try:
            script = """
            $os = Get-WmiObject Win32_OperatingSystem
            $total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
            $free = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
            $used = $total - $free
            $percent = [math]::Round(($used / $total) * 100, 2)
            @{
                TotalGB = $total
                UsedGB = $used
                FreeGB = $free
                PercentUsed = $percent
            } | ConvertTo-Json
            """
            
            result = self._execute_powershell(script)
            if not result:
                return []
            
            data = json.loads(result)
            percent_used = float(data.get('PercentUsed', 0))
            
            return [{
                "type": "memory",
                "name": "memory_usage",
                "value": percent_used,
                "unit": "percent",
                "status": self._get_status(percent_used, 80, 95),
                "metadata": {
                    "total_gb": data.get('TotalGB', 0),
                    "used_gb": data.get('UsedGB', 0),
                    "free_gb": data.get('FreeGB', 0),
                    "collection_method": "powershell_remote"
                }
            }]
        except Exception as e:
            logger.error(f"Erro ao coletar memória via PowerShell: {e}")
            return []
    
    def collect_disk(self, drive_letter: str = None) -> List[Dict[str, Any]]:
        """Coleta métricas de disco via PowerShell"""
        try:
            if drive_letter:
                filter_clause = f"WHERE DeviceID='{drive_letter}'"
            else:
                filter_clause = "WHERE DriveType=3"
            
            script = f"""
            $disks = Get-WmiObject Win32_LogicalDisk {filter_clause}
            $disks | ForEach-Object {{
                @{{
                    DeviceID = $_.DeviceID
                    VolumeName = $_.VolumeName
                    SizeGB = [math]::Round($_.Size / 1GB, 2)
                    FreeGB = [math]::Round($_.FreeSpace / 1GB, 2)
                    UsedGB = [math]::Round(($_.Size - $_.FreeSpace) / 1GB, 2)
                    PercentUsed = [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 2)
                }}
            }} | ConvertTo-Json
            """
            
            result = self._execute_powershell(script)
            if not result:
                return []
            
            # Parse JSON (pode ser array ou objeto único)
            data = json.loads(result)
            if not isinstance(data, list):
                data = [data]
            
            metrics = []
            for disk in data:
                device_id = disk.get('DeviceID', '')
                percent_used = float(disk.get('PercentUsed', 0))
                
                metrics.append({
                    "type": "disk",
                    "name": f"disk_{device_id.replace(':', '')}",
                    "value": percent_used,
                    "unit": "percent",
                    "status": self._get_status(percent_used, 80, 95),
                    "metadata": {
                        "device": device_id,
                        "volume_name": disk.get('VolumeName', ''),
                        "total_gb": disk.get('SizeGB', 0),
                        "used_gb": disk.get('UsedGB', 0),
                        "free_gb": disk.get('FreeGB', 0),
                        "collection_method": "powershell_remote"
                    }
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao coletar disco via PowerShell: {e}")
            return []
    
    def collect_uptime(self) -> List[Dict[str, Any]]:
        """Coleta uptime via PowerShell"""
        try:
            script = """
            $os = Get-WmiObject Win32_OperatingSystem
            $uptime = (Get-Date) - $os.ConvertToDateTime($os.LastBootUpTime)
            @{
                UptimeDays = [math]::Round($uptime.TotalDays, 2)
                UptimeHours = [math]::Round($uptime.TotalHours, 2)
                LastBootTime = $os.ConvertToDateTime($os.LastBootUpTime).ToString('yyyy-MM-dd HH:mm:ss')
            } | ConvertTo-Json
            """
            
            result = self._execute_powershell(script)
            if not result:
                return []
            
            data = json.loads(result)
            uptime_days = float(data.get('UptimeDays', 0))
            
            return [{
                "type": "uptime",
                "name": "uptime",
                "value": uptime_days,
                "unit": "days",
                "status": "ok",
                "metadata": {
                    "uptime_hours": data.get('UptimeHours', 0),
                    "last_boot": data.get('LastBootTime', ''),
                    "collection_method": "powershell_remote"
                }
            }]
        except Exception as e:
            logger.error(f"Erro ao coletar uptime via PowerShell: {e}")
            return []
    
    def collect_network(self) -> List[Dict[str, Any]]:
        """Coleta métricas de rede via PowerShell"""
        try:
            script = """
            $adapters = Get-WmiObject Win32_PerfFormattedData_Tcpip_NetworkInterface | Where-Object {$_.BytesTotalPersec -gt 0}
            $adapters | ForEach-Object {
                @{
                    Name = $_.Name
                    BytesReceivedPerSec = $_.BytesReceivedPerSec
                    BytesSentPerSec = $_.BytesSentPerSec
                    BytesTotalPerSec = $_.BytesTotalPersec
                }
            } | ConvertTo-Json
            """
            
            result = self._execute_powershell(script)
            if not result:
                return []
            
            data = json.loads(result)
            if not isinstance(data, list):
                data = [data]
            
            metrics = []
            for adapter in data:
                name = adapter.get('Name', 'Unknown')
                bytes_in = float(adapter.get('BytesReceivedPerSec', 0))
                bytes_out = float(adapter.get('BytesSentPerSec', 0))
                
                # Converter para Mbps
                mbps_in = (bytes_in * 8) / 1_000_000
                mbps_out = (bytes_out * 8) / 1_000_000
                
                metrics.extend([
                    {
                        "type": "network",
                        "name": f"network_in_{name}",
                        "value": mbps_in,
                        "unit": "mbps",
                        "status": "ok",
                        "metadata": {
                            "adapter": name,
                            "direction": "in",
                            "collection_method": "powershell_remote"
                        }
                    },
                    {
                        "type": "network",
                        "name": f"network_out_{name}",
                        "value": mbps_out,
                        "unit": "mbps",
                        "status": "ok",
                        "metadata": {
                            "adapter": name,
                            "direction": "out",
                            "collection_method": "powershell_remote"
                        }
                    }
                ])
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao coletar rede via PowerShell: {e}")
            return []
    
    def _execute_powershell(self, script: str) -> str:
        """
        Executa script PowerShell remoto via Invoke-Command
        """
        try:
            # Escapar aspas no script
            script_escaped = script.replace('"', '`"').replace("'", "''")
            
            # Comando PowerShell para execução remota
            ps_command = f"""
            $password = ConvertTo-SecureString '{self.password}' -AsPlainText -Force
            $credential = New-Object System.Management.Automation.PSCredential('{self.full_username}', $password)
            Invoke-Command -ComputerName {self.hostname} -Credential $credential -ScriptBlock {{
                {script}
            }}
            """
            
            # Executar via powershell.exe
            cmd = ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', ps_command]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Erro PowerShell: {result.stderr}")
                return ""
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao executar PowerShell no host {self.hostname}")
            return ""
        except Exception as e:
            logger.error(f"Erro ao executar PowerShell: {e}")
            return ""
    
    def _get_status(self, value: float, warning: float, critical: float) -> str:
        """Determina status baseado em thresholds"""
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
