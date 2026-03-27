"""
Hyper-V WMI Collector — Coruja Monitor v3.5

Coleta métricas de hosts Hyper-V via PowerShell Remoting (Invoke-Command)
e envia para a API /api/v1/hyperv/ingest via httpx.

Usa Invoke-Command para executar Get-VM no host remoto — NÃO requer
módulo Hyper-V instalado na sonda, apenas WinRM habilitado nos hosts.

Pré-configurado para SRVHVSPRD010 e SRVHVSPRD011.
"""
import logging
import time
import subprocess
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HyperVWMICollector:
    """Collects Hyper-V metrics via PowerShell Remoting from configured hosts."""

    def __init__(self, api_url: str = "", probe_token: str = ""):
        self.api_url = api_url
        self.probe_token = probe_token

    def collect_host(self, hostname: str, ip: str) -> Optional[Dict[str, Any]]:
        """Collect all Hyper-V metrics for a single host via Invoke-Command."""
        start = time.monotonic()
        try:
            logger.info(f"HyperV: collecting from {hostname} ({ip})...")

            # Single Invoke-Command that runs everything on the remote host
            payload = self._query_remote(hostname)
            if not payload:
                logger.warning(f"HyperV: no data from {hostname}")
                return self._error_payload(hostname, ip, start)

            elapsed_ms = (time.monotonic() - start) * 1000
            # Enrich payload
            payload["hostname"] = hostname
            payload["ip"] = ip
            payload["type"] = "hyperv"
            payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
            if "host" in payload:
                payload["host"]["wmi_latency_ms"] = round(elapsed_ms, 1)
                payload["host"]["status"] = "online"

            vm_count = len(payload.get("vms", []))
            running = sum(1 for v in payload.get("vms", []) if v.get("state") == "Running")
            logger.info(
                f"HyperV: {hostname} — {vm_count} VMs ({running} running), "
                f"latency {elapsed_ms:.0f}ms"
            )
            return payload

        except Exception as e:
            logger.error(f"HyperV: collect failed for {hostname}: {e}", exc_info=True)
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
        """Send collected payloads to the Hyper-V ingest API."""
        if not self.api_url or not payloads:
            return

        import httpx

        for payload in payloads:
            try:
                with httpx.Client(timeout=10.0, verify=False) as client:
                    resp = client.post(
                        f"{self.api_url}/api/v1/hyperv/ingest",
                        json=payload,
                        params={"probe_token": self.probe_token},
                    )
                    if resp.status_code < 300:
                        logger.info(f"HyperV: sent data for {payload['hostname']} OK")
                    else:
                        logger.warning(
                            f"HyperV: API returned {resp.status_code} for "
                            f"{payload['hostname']}: {resp.text[:200]}"
                        )
            except Exception as e:
                logger.warning(f"HyperV: failed to send {payload.get('hostname')}: {e}")

    # ── Private: PowerShell remoting ─────────────────────────────────────

    def _query_remote(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Run a single Invoke-Command on the remote host to collect everything."""
        # This script runs ENTIRELY on the remote host via Invoke-Command.
        # The sonda does NOT need the Hyper-V PowerShell module installed.
        remote_script = r"""
$ErrorActionPreference = 'Stop'
try {
    # ── Host hardware identity ──
    $cs = Get-CimInstance Win32_ComputerSystem
    $os = Get-CimInstance Win32_OperatingSystem
    $bios = Get-CimInstance Win32_BIOS -ErrorAction SilentlyContinue
    $procs = Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue
    $procName = if ($procs) { ($procs | Select-Object -First 1).Name } else { '' }
    $procSockets = if ($procs) { ($procs | Measure-Object).Count } else { 0 }
    $procCoresPerSocket = if ($procs) { ($procs | Select-Object -First 1).NumberOfCores } else { 0 }

    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" -ErrorAction SilentlyContinue
    $totalDiskGB = if ($disk) { [math]::Round(($disk | Measure-Object -Property Size -Sum).Sum / 1GB, 1) } else { 0 }
    $freeDiskGB  = if ($disk) { [math]::Round(($disk | Measure-Object -Property FreeSpace -Sum).Sum / 1GB, 1) } else { 0 }
    $storagePct  = if ($totalDiskGB -gt 0) { [math]::Round((($totalDiskGB - $freeDiskGB) / $totalDiskGB) * 100, 1) } else { 0 }
    $memPct      = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize * 100, 1)

    # ── Host CPU usage ──
    $hostCpu = 0
    try {
        if ($procs) {
            $hostCpu = [math]::Round(($procs | Measure-Object -Property LoadPercentage -Average).Average, 1)
        }
    } catch {}

    # ── VMs ──
    $vms = Get-VM -ErrorAction Stop
    $totalMemGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
    $hostLogicalCPUs = $cs.NumberOfLogicalProcessors

    # ── VM CPU via Get-Counter (Guest Run Time = what Task Manager shows inside VM) ──
    $vmCpuMap = @{}
    try {
        $samples = (Get-Counter '\Hyper-V Hypervisor Virtual Processor(*)\% Guest Run Time' -ErrorAction Stop).CounterSamples
        foreach ($s in $samples) {
            $inst = $s.InstanceName
            if ($inst -like '*_total*') { continue }
            $parts = $inst -split ':'
            if ($parts.Count -ge 1) {
                $vmName = $parts[0].Trim()
                if (-not $vmCpuMap.ContainsKey($vmName)) { $vmCpuMap[$vmName] = @() }
                $vmCpuMap[$vmName] += $s.CookedValue
            }
        }
    } catch {}

    # ── VM Memory via Get-Counter (Current Pressure = real memory usage %) ──
    $vmMemPressure = @{}
    try {
        $memSamples = (Get-Counter '\Hyper-V Dynamic Memory VM(*)\Current Pressure' -ErrorAction Stop).CounterSamples
        foreach ($ms in $memSamples) {
            $vmMemPressure[$ms.InstanceName.Trim()] = $ms.CookedValue
        }
    } catch {}

    $vmList = @()
    foreach ($vm in $vms) {
        # CPU: sum Guest Run Time / vCPU count = what Task Manager shows inside the VM
        $cpuUsage = 0
        $vmNameLower = $vm.Name.ToLower()
        $vcpuCount = $vm.ProcessorCount
        if ($vcpuCount -lt 1) { $vcpuCount = 1 }
        if ($vmCpuMap.ContainsKey($vmNameLower) -and $vmCpuMap[$vmNameLower].Count -gt 0) {
            $sumCpu = ($vmCpuMap[$vmNameLower] | Measure-Object -Sum).Sum
            $cpuUsage = [math]::Round($sumCpu / $vcpuCount, 1)
        } elseif ($vmCpuMap.ContainsKey($vm.Name) -and $vmCpuMap[$vm.Name].Count -gt 0) {
            $sumCpu = ($vmCpuMap[$vm.Name] | Measure-Object -Sum).Sum
            $cpuUsage = [math]::Round($sumCpu / $vcpuCount, 1)
        }

        # Memory: use Current Pressure from Get-Counter (same logic as CPU)
        $memPressure = 0
        if ($vmMemPressure.ContainsKey($vmNameLower)) {
            $memPressure = [math]::Round($vmMemPressure[$vmNameLower], 1)
        } elseif ($vmMemPressure.ContainsKey($vm.Name)) {
            $memPressure = [math]::Round($vmMemPressure[$vm.Name], 1)
        }

        # Memory assigned (what the host allocated to this VM)
        $memAssignedMB = [math]::Round($vm.MemoryAssigned / 1MB)
        # Memory demand (actual RAM usage inside the VM via Integration Services)
        $memDemandMB = 0
        try { if ($vm.MemoryDemand -gt 0) { $memDemandMB = [math]::Round($vm.MemoryDemand / 1MB) } } catch {}
        # % of host memory this VM consumes (based on assigned)
        $memPctOfHost = if ($totalMemGB -gt 0) { [math]::Round(($memAssignedMB / 1024) / $totalMemGB * 100, 1) } else { 0 }

        # VHD: FileSize = actual used on disk, Size = provisioned max capacity
        $diskUsedBytes = [long]0
        $diskMaxBytes  = [long]0
        try {
            $hdds = Get-VMHardDiskDrive -VM $vm -ErrorAction SilentlyContinue
            foreach ($hdd in $hdds) {
                if ($hdd.Path) {
                    $vhd = Get-VHD -Path $hdd.Path -ErrorAction SilentlyContinue
                    if ($vhd) {
                        $diskUsedBytes += $vhd.FileSize
                        $diskMaxBytes  += $vhd.Size
                    }
                }
            }
        } catch {}

        $vmList += @{
            name            = $vm.Name
            state           = $vm.State.ToString()
            vcpus           = $vm.ProcessorCount
            memory_mb       = $memAssignedMB
            memory_demand_mb = $memDemandMB
            cpu_percent     = $cpuUsage
            memory_percent  = $memPctOfHost
            disk_bytes      = $diskUsedBytes
            disk_max_bytes  = $diskMaxBytes
            uptime_seconds  = if ($vm.Uptime) { [int]$vm.Uptime.TotalSeconds } else { 0 }
        }
    }

    $running = ($vms | Where-Object { $_.State -eq 'Running' }).Count

    @{
        host = @{
            total_cpus       = $cs.NumberOfLogicalProcessors
            total_memory_gb  = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
            total_storage_gb = $totalDiskGB
            cpu_percent      = $hostCpu
            memory_percent   = $memPct
            storage_percent  = $storagePct
            vm_count         = $vms.Count
            running_vm_count = $running
            manufacturer     = $cs.Manufacturer
            model            = $cs.Model
            serial_number    = if ($bios) { $bios.SerialNumber } else { '' }
            bios_version     = if ($bios) { $bios.SMBIOSBIOSVersion } else { '' }
            os_version       = $os.Caption
            processor_name   = $procName
            processor_sockets = $procSockets
            cores_per_socket = $procCoresPerSocket
        }
        vms = $vmList
    } | ConvertTo-Json -Depth 4 -Compress
} catch {
    @{ error = $_.Exception.Message } | ConvertTo-Json -Compress
}
"""

        ps_command = (
            f'Invoke-Command -ComputerName {hostname} '
            f'-ScriptBlock {{ {remote_script} }}'
        )

        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip()[:300] if result.stderr else ""
                logger.warning(f"HyperV PS error for {hostname}: {stderr}")
                return None

            stdout = result.stdout.strip()
            if not stdout:
                logger.warning(f"HyperV: empty output from {hostname}")
                return None

            data = json.loads(stdout)

            if "error" in data:
                logger.warning(f"HyperV remote error on {hostname}: {data['error']}")
                return None

            return data

        except subprocess.TimeoutExpired:
            logger.warning(f"HyperV: timeout (30s) for {hostname}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"HyperV: JSON parse error for {hostname}: {e}")
            return None
        except Exception as e:
            logger.warning(f"HyperV: exec error for {hostname}: {e}")
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
