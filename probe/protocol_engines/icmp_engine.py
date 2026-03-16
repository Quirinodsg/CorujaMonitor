"""
ICMP Engine - Ping via subprocess (compatível Windows/Linux)
"""
import platform
import re
import subprocess
import time
import logging
from typing import Tuple

from .base_engine import BaseProtocolEngine, EngineResult

logger = logging.getLogger(__name__)


class ICMPEngine(BaseProtocolEngine):
    """Engine ICMP usando subprocess ping. Retorna latência em ms."""

    def __init__(self, count: int = 1, timeout: int = 2, retries: int = 2):
        self._count = count
        self._timeout = timeout
        self._retries = retries
        self._is_windows = platform.system().lower() == "windows"

    def is_available(self) -> bool:
        return True  # ping está disponível em todos os sistemas

    def execute(self, host: str, **kwargs) -> EngineResult:
        timeout = kwargs.get("timeout", self._timeout)
        retries = kwargs.get("retries", self._retries)

        for attempt in range(retries + 1):
            ok, latency_ms, loss_pct = self._ping(host, timeout)
            if ok:
                return EngineResult(
                    status="ok",
                    value=round(latency_ms, 2),
                    unit="ms",
                    metadata={
                        "latency_ms": round(latency_ms, 2),
                        "packet_loss_percent": loss_pct,
                        "attempts": attempt + 1,
                    },
                )
            if attempt < retries:
                time.sleep(0.5)

        return EngineResult(
            status="critical",
            value=0.0,
            unit="ms",
            error="host_unreachable",
            metadata={"packet_loss_percent": 100.0, "attempts": retries + 1},
        )

    def _ping(self, host: str, timeout: int) -> Tuple[bool, float, float]:
        """Executa ping e retorna (sucesso, latencia_ms, packet_loss_pct)"""
        if self._is_windows:
            cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
        else:
            cmd = ["ping", "-c", "1", "-W", str(timeout), host]

        start = time.monotonic()
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout + 2
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            output = proc.stdout + proc.stderr

            latency_ms = self._parse_latency(output, elapsed_ms)
            loss_pct = self._parse_loss(output)

            success = proc.returncode == 0 and loss_pct < 100.0
            return success, latency_ms, loss_pct
        except subprocess.TimeoutExpired:
            return False, 0.0, 100.0
        except Exception as e:
            logger.debug(f"ICMPEngine ping error for {host}: {e}")
            return False, 0.0, 100.0

    def _parse_latency(self, output: str, fallback_ms: float) -> float:
        if self._is_windows:
            m = re.search(r"Average\s*=\s*(\d+)ms", output, re.IGNORECASE)
            if m:
                return float(m.group(1))
            m = re.search(r"time[=<](\d+)ms", output, re.IGNORECASE)
            if m:
                return float(m.group(1))
        else:
            m = re.search(r"rtt\s+min/avg/max/mdev\s*=\s*[\d.]+/([\d.]+)/", output)
            if m:
                return float(m.group(1))
            m = re.search(r"time=([\d.]+)\s*ms", output)
            if m:
                return float(m.group(1))
        return fallback_ms

    def _parse_loss(self, output: str) -> float:
        if self._is_windows:
            m = re.search(r"\((\d+)%\s*loss\)", output, re.IGNORECASE)
        else:
            m = re.search(r"(\d+)%\s*packet\s*loss", output)
        return float(m.group(1)) if m else 100.0
