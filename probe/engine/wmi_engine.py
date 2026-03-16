"""
WMI Engine - Engine WMI otimizada com WQL queries padrão
Equivalente ao motor WMI interno do PRTG

WQL Queries implementadas:
  CPU:     SELECT LoadPercentage FROM Win32_Processor
  Memory:  SELECT FreePhysicalMemory,TotalVisibleMemorySize FROM Win32_OperatingSystem
  Disk:    SELECT DeviceID,FreeSpace,Size FROM Win32_LogicalDisk WHERE DriveType=3
  Service: SELECT Name,State,StartMode FROM Win32_Service
  Process: SELECT Name,ProcessId,WorkingSetSize FROM Win32_Process
"""
import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# WQL Queries padrão (como PRTG usa internamente)
WQL_CPU = "SELECT Name,LoadPercentage,NumberOfLogicalProcessors FROM Win32_Processor"
WQL_MEMORY = "SELECT FreePhysicalMemory,TotalVisibleMemorySize,FreeVirtualMemory,TotalVirtualMemorySize FROM Win32_OperatingSystem"
WQL_DISK = "SELECT DeviceID,FreeSpace,Size,VolumeName,DriveType FROM Win32_LogicalDisk WHERE DriveType=3"
WQL_SERVICE = "SELECT Name,State,StartMode,DisplayName FROM Win32_Service"
WQL_PROCESS = "SELECT Name,ProcessId,WorkingSetSize,PercentProcessorTime FROM Win32_Process"
WQL_OS = "SELECT Caption,Version,BuildNumber,LastBootUpTime,NumberOfProcesses FROM Win32_OperatingSystem"
WQL_NETWORK = "SELECT Name,BytesReceivedPerSec,BytesSentPerSec,CurrentBandwidth FROM Win32_PerfFormattedData_Tcpip_NetworkInterface"
WQL_PERF_CPU = "SELECT PercentProcessorTime FROM Win32_PerfFormattedData_PerfOS_Processor WHERE Name='_Total'"


class WMIEngine:
    """
    Engine WMI otimizada.
    
    Diferencial vs WMINativeCollector básico:
    - Usa WQL queries diretas (mais rápido que atributos Python)
    - Suporte a Win32_PerfFormattedData (contadores de performance em tempo real)
    - Fallback automático: PerfCounter → WMI → Registry
    - Logging detalhado de cada query
    """

    def __init__(self, connection):
        """
        Args:
            connection: objeto wmi.WMI já conectado (vem do WMIConnectionPool)
        """
        self.conn = connection

    def _query(self, wql: str) -> List[Any]:
        """Executa WQL query com logging e tratamento de erro"""
        start = time.monotonic()
        try:
            result = self.conn.query(wql)
            elapsed = (time.monotonic() - start) * 1000
            logger.debug(f"WQL [{elapsed:.1f}ms] {wql[:80]}")
            return result
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(f"WQL FAILED [{elapsed:.1f}ms] {wql[:80]} → {e}")
            return []

    def collect_cpu(self) -> List[Dict[str, Any]]:
        """CPU via Win32_Processor WQL"""
        rows = self._query(WQL_CPU)
        if not rows:
            return []

        loads = [r.LoadPercentage for r in rows if r.LoadPercentage is not None]
        avg_load = sum(loads) / len(loads) if loads else 0.0
        logical_cpus = rows[0].NumberOfLogicalProcessors if rows else 0

        return [{
            "type": "cpu",
            "name": "CPU Usage",
            "value": round(float(avg_load), 2),
            "unit": "percent",
            "status": _threshold_status(avg_load, 80, 95),
            "metadata": {
                "logical_cpus": logical_cpus,
                "core_count": len(rows),
                "wql": WQL_CPU,
                "collection_method": "wmi_wql",
            },
        }]

    def collect_cpu_perf(self) -> List[Dict[str, Any]]:
        """
        CPU via Win32_PerfFormattedData_PerfOS_Processor.
        Mais preciso que Win32_Processor.LoadPercentage (atualizado em tempo real).
        Este é o método que PRTG usa por padrão.
        """
        rows = self._query(WQL_PERF_CPU)
        if not rows:
            # Fallback para Win32_Processor
            logger.debug("PerfFormattedData CPU não disponível, usando Win32_Processor")
            return self.collect_cpu()

        pct = float(rows[0].PercentProcessorTime)
        return [{
            "type": "cpu",
            "name": "CPU Usage (PerfCounter)",
            "value": round(pct, 2),
            "unit": "percent",
            "status": _threshold_status(pct, 80, 95),
            "metadata": {
                "wql": WQL_PERF_CPU,
                "collection_method": "wmi_perfcounter",
            },
        }]

    def collect_memory(self) -> List[Dict[str, Any]]:
        """Memória via Win32_OperatingSystem WQL"""
        rows = self._query(WQL_MEMORY)
        if not rows:
            return []

        row = rows[0]
        total_kb = int(row.TotalVisibleMemorySize)
        free_kb = int(row.FreePhysicalMemory)
        used_kb = total_kb - free_kb
        pct_used = (used_kb / total_kb * 100) if total_kb > 0 else 0.0

        return [{
            "type": "memory",
            "name": "Memory Usage",
            "value": round(pct_used, 2),
            "unit": "percent",
            "status": _threshold_status(pct_used, 80, 95),
            "metadata": {
                "total_gb": round(total_kb / 1024 / 1024, 2),
                "used_gb": round(used_kb / 1024 / 1024, 2),
                "free_gb": round(free_kb / 1024 / 1024, 2),
                "wql": WQL_MEMORY,
                "collection_method": "wmi_wql",
            },
        }]

    def collect_disk(self) -> List[Dict[str, Any]]:
        """Discos locais via Win32_LogicalDisk WQL (DriveType=3)"""
        rows = self._query(WQL_DISK)
        metrics = []

        for row in rows:
            if not row.Size:
                continue
            total = int(row.Size)
            free = int(row.FreeSpace)
            used = total - free
            pct = (used / total * 100) if total > 0 else 0.0
            drive = row.DeviceID.replace(":", "")

            metrics.append({
                "type": "disk",
                "name": f"Disk {row.DeviceID}",
                "value": round(pct, 2),
                "unit": "percent",
                "status": _threshold_status(pct, 80, 95),
                "metadata": {
                    "device": row.DeviceID,
                    "volume_name": row.VolumeName or "",
                    "total_gb": round(total / 1024 ** 3, 2),
                    "used_gb": round(used / 1024 ** 3, 2),
                    "free_gb": round(free / 1024 ** 3, 2),
                    "wql": WQL_DISK,
                    "collection_method": "wmi_wql",
                },
            })

        return metrics

    def collect_services(self, filter_auto_only: bool = True) -> List[Dict[str, Any]]:
        """
        Serviços via Win32_Service WQL.
        Por padrão filtra apenas serviços com StartMode=Auto.
        """
        wql = WQL_SERVICE
        if filter_auto_only:
            wql = "SELECT Name,State,StartMode,DisplayName FROM Win32_Service WHERE StartMode='Auto'"

        rows = self._query(wql)
        metrics = []

        for row in rows:
            is_running = row.State == "Running"
            metrics.append({
                "type": "service",
                "name": f"Service {row.Name}",
                "value": 1 if is_running else 0,
                "unit": "state",
                "status": "ok" if is_running else "critical",
                "metadata": {
                    "service_name": row.Name,
                    "display_name": row.DisplayName,
                    "state": row.State,
                    "start_mode": row.StartMode,
                    "wql": wql,
                    "collection_method": "wmi_wql",
                },
            })

        return metrics

    def collect_processes(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Top N processos por uso de memória via Win32_Process WQL.
        """
        rows = self._query(WQL_PROCESS)
        if not rows:
            return []

        # Ordenar por WorkingSetSize (memória)
        sorted_rows = sorted(
            rows,
            key=lambda r: int(r.WorkingSetSize) if r.WorkingSetSize else 0,
            reverse=True,
        )[:top_n]

        metrics = []
        for row in sorted_rows:
            mem_mb = int(row.WorkingSetSize) / 1024 / 1024 if row.WorkingSetSize else 0
            metrics.append({
                "type": "process",
                "name": f"Process {row.Name}",
                "value": round(mem_mb, 2),
                "unit": "MB",
                "status": "ok",
                "metadata": {
                    "process_name": row.Name,
                    "pid": row.ProcessId,
                    "memory_mb": round(mem_mb, 2),
                    "wql": WQL_PROCESS,
                    "collection_method": "wmi_wql",
                },
            })

        return metrics

    def collect_os_info(self) -> Dict[str, Any]:
        """Informações do OS via Win32_OperatingSystem"""
        rows = self._query(WQL_OS)
        if not rows:
            return {}

        row = rows[0]
        return {
            "os_name": row.Caption,
            "os_version": row.Version,
            "build_number": row.BuildNumber,
            "last_boot": str(row.LastBootUpTime),
            "process_count": row.NumberOfProcesses,
        }

    def collect_all(self, include_services: bool = False, include_processes: bool = False) -> List[Dict[str, Any]]:
        """Coleta todas as métricas principais"""
        metrics = []
        metrics.extend(self.collect_cpu_perf())  # PerfCounter primeiro, fallback para WQL
        metrics.extend(self.collect_memory())
        metrics.extend(self.collect_disk())
        if include_services:
            metrics.extend(self.collect_services())
        if include_processes:
            metrics.extend(self.collect_processes())
        return metrics


def _threshold_status(value: float, warning: float, critical: float) -> str:
    if value >= critical:
        return "critical"
    if value >= warning:
        return "warning"
    return "ok"
