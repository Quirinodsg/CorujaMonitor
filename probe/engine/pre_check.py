"""
Pre-Check de Conectividade - Valida host antes de coletar métricas
Cache TTL 30s para evitar verificações repetidas
"""
import socket
import subprocess
import time
import threading
import platform
from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PreCheckResult:
    passed: bool
    host: str
    error: Optional[str] = None
    latency_ms: float = 0.0


class ConnectivityPreCheck:
    CACHE_TTL = 30  # segundos

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (result, timestamp)
        self._lock = threading.Lock()

    def check_wmi(self, host: str) -> PreCheckResult:
        cached = self._get_cached(f"wmi:{host}")
        if cached:
            return cached

        ping_ok, latency = self._ping(host, timeout=2)
        if not ping_ok:
            result = PreCheckResult(passed=False, host=host, error="host_unreachable")
            self._set_cache(f"wmi:{host}", result)
            return result

        tcp_ok, _ = self._tcp_check(host, 135, timeout=2)
        if not tcp_ok:
            result = PreCheckResult(passed=False, host=host, error="port_unreachable", latency_ms=latency)
            self._set_cache(f"wmi:{host}", result)
            return result

        result = PreCheckResult(passed=True, host=host, latency_ms=latency)
        self._set_cache(f"wmi:{host}", result)
        return result

    def check_snmp(self, host: str) -> PreCheckResult:
        cached = self._get_cached(f"snmp:{host}")
        if cached:
            return cached

        ping_ok, latency = self._ping(host, timeout=2)
        if not ping_ok:
            result = PreCheckResult(passed=False, host=host, error="host_unreachable")
            self._set_cache(f"snmp:{host}", result)
            return result

        udp_ok = self._udp_check(host, 161, timeout=2)
        if not udp_ok:
            result = PreCheckResult(passed=False, host=host, error="port_unreachable", latency_ms=latency)
            self._set_cache(f"snmp:{host}", result)
            return result

        result = PreCheckResult(passed=True, host=host, latency_ms=latency)
        self._set_cache(f"snmp:{host}", result)
        return result

    def check_tcp(self, host: str, port: int) -> PreCheckResult:
        cached = self._get_cached(f"tcp:{host}:{port}")
        if cached:
            return cached

        ping_ok, latency = self._ping(host, timeout=2)
        if not ping_ok:
            result = PreCheckResult(passed=False, host=host, error="host_unreachable")
            self._set_cache(f"tcp:{host}:{port}", result)
            return result

        tcp_ok, _ = self._tcp_check(host, port, timeout=2)
        if not tcp_ok:
            result = PreCheckResult(passed=False, host=host, error="port_unreachable", latency_ms=latency)
            self._set_cache(f"tcp:{host}:{port}", result)
            return result

        result = PreCheckResult(passed=True, host=host, latency_ms=latency)
        self._set_cache(f"tcp:{host}:{port}", result)
        return result

    def _ping(self, host: str, timeout: int = 2):
        start = time.monotonic()
        try:
            is_windows = platform.system().lower() == "windows"
            param = "-n" if is_windows else "-c"
            timeout_param = "-w" if is_windows else "-W"
            timeout_val = str(timeout * 1000) if is_windows else str(timeout)
            result = subprocess.run(
                ["ping", param, "1", timeout_param, timeout_val, host],
                capture_output=True, timeout=timeout + 1
            )
            latency = (time.monotonic() - start) * 1000
            return result.returncode == 0, latency
        except Exception:
            return False, 0.0

    def _tcp_check(self, host: str, port: int, timeout: int = 2):
        start = time.monotonic()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            latency = (time.monotonic() - start) * 1000
            return result == 0, latency
        except Exception:
            return False, 0.0

    def _udp_check(self, host: str, port: int, timeout: int = 2):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(b"", (host, port))
            sock.close()
            return True
        except Exception:
            return False

    def _get_cached(self, key: str) -> Optional[PreCheckResult]:
        with self._lock:
            entry = self._cache.get(key)
            if entry and (time.monotonic() - entry[1]) < self.CACHE_TTL:
                return entry[0]
        return None

    def _set_cache(self, key: str, result: PreCheckResult):
        with self._lock:
            self._cache[key] = (result, time.monotonic())
