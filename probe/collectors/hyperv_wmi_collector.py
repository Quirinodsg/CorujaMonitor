"""
Hyper-V WMI Collector — Coruja Monitor v3.5

Coleta métricas de hosts Hyper-V via WMI (Msvm_ComputerSystem, Msvm_SummaryInformation,
Win32_ComputerSystem) e envia para a API /api/v1/hyperv/ via httpx.

Usa o WMI pool existente para reutilizar conexões.
Pré-configurado para SRVHVSPRD010 e SRVHVSPRD011.

Requirements: 1.1-1.7, 12.1-12.4
"""
import logging
import time
import subprocess
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HyperVWMICollector:
    """Collects Hyper-V metrics via WMI/PowerShell from configured hosts."""

    def __init__(self, api_url: str = "", probe_token: str = ""):
        self.api_url = api_url
        self.probe_token = probe_token

    def collect_host(self, hostname: str, ip: str) -> Optional[Dict[str, Any]]:
        """Collect all Hyper-V metrics for a single host.

        Uses PowerShell remoting (Invoke-Command) to query Hyper-V data.
        Timeout: 10s per host.

        Returns structured payload or None on failure.
        """
        start = time.monotonic()
        try:
            # 1. Get host info (CPUs, memory)
            host_info = self._query_host_info(hostname)
            if not host_info:
                logger.warning(f"HyperV: host info failed for {hostname}")
                return self._error_payload(hostname, ip, start)

            # 2. Get VM list with states and resource usage
            vms = self._query_vms(hostname)

            # 3. Build payload
            elapsed_ms = (time.monotonic() - start) * 1000
            running = sum(1 for v in vms if v.get("state") == "Running")

            # Aggregate CPU/memory from VMs
            total_vm_cpu = sum(v.get("cpu_percent", 0) for v in vms) if vms else 0
            avg_cpu = total_vm_cpu / len(vms) if vms else 0

            payload = {
                "type": "hyperv",
                "hostname": hostname,
                "ip": ip,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "host": {
                    "total_cpus": host_info.get("total_cpus", 0),
                    "total_memory_gb": host_info.get("total_memory_gb", 0),
                    "total_storage_gb": host_info.get("total_storage_gb", 0),
                    "cpu_percent": round(avg_cpu, 1),
                    "memory_percent": host_info.get("memory_percent", 0),
                    "storage_percent": host_info.get("storage_percent", 0),
                    "vm_count": len(vms),
                    "running_vm_count": running,
                    "wmi_latency_ms": round(elapsed_ms, 1),
                    "status": "online",
                },
                "vms": vms,
            }

            logger.info(
                f"HyperV: {hostname} — {len(vms)} VMs ({running} running), "
                f"CPU {avg_cpu:.1f}%, latency {elapsed_ms:.0f}ms"
            )
            return payload

        except Exception as e:
            logger.error(f"HyperV: collect failed for {hostname}: {e}")
            return self._error_payload(hostname, ip, start)

    def collect_all(self, hosts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Collect from all configured hosts. Continues on failure."""
        results = []
        for h in hosts:
            payload = self.collect_host(h["hostname"], h["ip"])
            if payload:
                results.append(payload)
        return results

    def send_to_api(self, payloads: List[Dict[str, Any]]):
        """Send collected payloads to the Hyper-V API for persistence."""
        if not self.api_url or not payloads:
            return

        import httpx

        for payload in payloads:
            try:
                with httpx.Client(timeout=10.0, verify=False) as client:
                    # Upsert host
                    host_data = payload.get("host", {})
                    resp = client.post(
                        f"{self.api_url}/api/v1/hyperv/ingest",
                        json=payload,
                        params={"probe_token": self.probe_token},
                    )
                    if resp.status_code < 300:
                        logger.debug(f"HyperV: sent data for {payload['hostname']}")
                    else:
                        logger.warning(f"HyperV: API returned {resp.status_code} for {payload['hostname']}")
            except Exception as e:
                logger.warning(f"HyperV: failed to send data for {payload.get('hostname')}: {e}")

    # ── Private: PowerShell queries ──────────────────────────────────────

    def _query_host_info(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Query Win32_ComputerSystem + Win32_OperatingSystem for host resources."""
        ps_script = f"""
$cs = Get-CimInstance -ComputerName {hostname} -ClassName Win32_ComputerSystem -ErrorAction Stop
$os = Get-CimInstance -ComputerName {hostname} -ClassName Win32_OperatingSystem -ErrorAction Stop
$disk = Get-CimInstance -ComputerName {hostname} -ClassName Win32_LogicalDisk -Filter "DriveType=3" -ErrorAction SilentlyContinue
$totalDiskGB = ($disk | Measure-Object -Property Size -Sum).Sum / 1GB
$freeDiskGB = ($disk | Measure-Object -Property FreeSpace -Sum).Sum / 1GB
$usedPct = if ($totalDiskGB -gt 0) {{ [math]::Round((($totalDiskGB - $freeDiskGB) / $totalDiskGB) * 100, 1) }} else {{ 0 }}
$memPct = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 1)
@{{
    total_cpus = $cs.NumberOfLogicalProcessors
    total_memory_gb = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
    total_storage_gb = [math]::Round($totalDiskGB, 1)
    memory_percent = $memPct
    storage_percent = $usedPct
}} | ConvertTo-Json
"""
        return self._run_ps(ps_script)

    def _query_vms(self, hostname: str) -> List[Dict[str, Any]]:
        """Query Hyper-V VMs with CPU, memory, state via Get-VM."""
        ps_script = f"""
$vms = Get-VM -ComputerName {hostname} -ErrorAction Stop
$result = @()
foreach ($vm in $vms) {{
    $cpu = (Get-VMProcessor -VM $vm -ErrorAction SilentlyContinue)
    $mem = (Get-VMMemory -VM $vm -ErrorAction SilentlyContinue)
    $cpuUsage = 0
    try {{
        $cpuUsage = (Measure-VM -VM $vm -ErrorAction SilentlyContinue).AvgCPUUsage
    }} catch {{ }}
    $result += @{{
        name = $vm.Name
        state = $vm.State.ToString()
        vcpus = if ($cpu) {{ $cpu.Count }} else {{ 0 }}
        memory_mb = [math]::Round($vm.MemoryAssigned / 1MB)
        cpu_percent = $cpuUsage
        disk_bytes = 0
        uptime_seconds = if ($vm.Uptime) {{ [int]$vm.Uptime.TotalSeconds }} else {{ 0 }}
    }}
}}
$result | ConvertTo-Json -Depth 3
"""
        data = self._run_ps(ps_script)
        if data is None:
            return []
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
        return []

    def _run_ps(self, script: str) -> Any:
        """Execute PowerShell script and parse JSON output."""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                logger.debug(f"PS error: {result.stderr[:200]}")
                return None
            if not result.stdout.strip():
                return None
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            logger.warning("PS timeout (10s)")
            return None
        except json.JSONDecodeError as e:
            logger.debug(f"PS JSON parse error: {e}")
            return None
        except Exception as e:
            logger.debug(f"PS exec error: {e}")
            return None

    def _error_payload(self, hostname: str, ip: str, start: float) -> Dict[str, Any]:
        """Build an error/unreachable payload."""
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "type": "hyperv",
            "hostname": hostname,
            "ip": ip,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "host": {
                "total_cpus": 0,
                "total_memory_gb": 0,
                "total_storage_gb": 0,
                "cpu_percent": 0,
                "memory_percent": 0,
                "storage_percent": 0,
                "vm_count": 0,
                "running_vm_count": 0,
                "wmi_latency_ms": round(elapsed_ms, 1),
                "status": "unreachable",
            },
            "vms": [],
        }
