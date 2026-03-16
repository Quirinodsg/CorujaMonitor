"""
ICMP Sensor - Ping com latência, packet loss e retry
Equivalente ao sensor ICMP do PRTG
"""
import subprocess
import platform
import re
import socket
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ICMPSensor:
    """
    Sensor ICMP completo com:
    - Latência (ms)
    - Packet loss (%)
    - Timeout configurável
    - Retry automático
    - Status: ok / warning / critical
    """

    def __init__(
        self,
        host: str,
        count: int = 4,
        timeout: int = 3,
        retries: int = 2,
        warning_latency_ms: float = 100.0,
        critical_latency_ms: float = 500.0,
        warning_loss_pct: float = 10.0,
        critical_loss_pct: float = 50.0,
    ):
        self.host = host
        self.count = count
        self.timeout = timeout
        self.retries = retries
        self.warning_latency_ms = warning_latency_ms
        self.critical_latency_ms = critical_latency_ms
        self.warning_loss_pct = warning_loss_pct
        self.critical_loss_pct = critical_loss_pct
        self._is_windows = platform.system().lower() == "windows"

    def _build_command(self) -> list:
        if self._is_windows:
            return ["ping", "-n", str(self.count), "-w", str(self.timeout * 1000), self.host]
        else:
            return ["ping", "-c", str(self.count), "-W", str(self.timeout), self.host]

    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Extrai latência e packet loss do output do ping"""
        result = {"latency_ms": 0.0, "packet_loss_percent": 100.0, "min_ms": 0.0, "max_ms": 0.0, "avg_ms": 0.0}

        if self._is_windows:
            # Packet loss: "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)"
            loss_match = re.search(r"Lost\s*=\s*\d+\s*\((\d+)%\s*loss\)", output, re.IGNORECASE)
            if loss_match:
                result["packet_loss_percent"] = float(loss_match.group(1))

            # Latency: "Minimum = 1ms, Maximum = 3ms, Average = 2ms"
            rtt_match = re.search(r"Minimum\s*=\s*(\d+)ms.*Maximum\s*=\s*(\d+)ms.*Average\s*=\s*(\d+)ms", output, re.IGNORECASE)
            if rtt_match:
                result["min_ms"] = float(rtt_match.group(1))
                result["max_ms"] = float(rtt_match.group(2))
                result["avg_ms"] = float(rtt_match.group(3))
                result["latency_ms"] = result["avg_ms"]
        else:
            # Linux: "1 packets transmitted, 1 received, 0% packet loss"
            loss_match = re.search(r"(\d+)%\s*packet\s*loss", output)
            if loss_match:
                result["packet_loss_percent"] = float(loss_match.group(1))

            # Linux: "rtt min/avg/max/mdev = 0.123/0.456/0.789/0.100 ms"
            rtt_match = re.search(r"rtt\s+min/avg/max/mdev\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)", output)
            if rtt_match:
                result["min_ms"] = float(rtt_match.group(1))
                result["avg_ms"] = float(rtt_match.group(2))
                result["max_ms"] = float(rtt_match.group(3))
                result["latency_ms"] = result["avg_ms"]

        return result

    def _determine_status(self, latency_ms: float, packet_loss_pct: float) -> str:
        if packet_loss_pct >= self.critical_loss_pct or latency_ms >= self.critical_latency_ms:
            return "critical"
        if packet_loss_pct >= self.warning_loss_pct or latency_ms >= self.warning_latency_ms:
            return "warning"
        return "ok"

    def collect(self) -> Dict[str, Any]:
        """Executa ping com retry e retorna métricas"""
        cmd = self._build_command()
        last_error = None

        for attempt in range(self.retries + 1):
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout * self.count + 2,
                )
                output = proc.stdout + proc.stderr
                parsed = self._parse_output(output)

                # Se returncode != 0 mas conseguiu parsear, usa os dados
                if proc.returncode != 0 and parsed["packet_loss_percent"] == 100.0:
                    if attempt < self.retries:
                        logger.debug(f"ICMP attempt {attempt+1} failed for {self.host}, retrying...")
                        time.sleep(1)
                        continue

                status = self._determine_status(parsed["latency_ms"], parsed["packet_loss_percent"])
                is_online = parsed["packet_loss_percent"] < 100.0

                return {
                    "type": "icmp_ping",
                    "name": "ICMP Ping",
                    "host": self.host,
                    "status": status,
                    "latency_ms": parsed["latency_ms"],
                    "packet_loss_percent": parsed["packet_loss_percent"],
                    "min_ms": parsed["min_ms"],
                    "max_ms": parsed["max_ms"],
                    "avg_ms": parsed["avg_ms"],
                    "is_online": is_online,
                    "value": parsed["latency_ms"],
                    "unit": "ms",
                    "metadata": {
                        "count": self.count,
                        "timeout": self.timeout,
                        "attempts": attempt + 1,
                        "collection_method": "icmp",
                    },
                }

            except subprocess.TimeoutExpired:
                last_error = "timeout"
                if attempt < self.retries:
                    time.sleep(1)
                    continue
            except Exception as e:
                last_error = str(e)
                logger.error(f"ICMP error for {self.host}: {e}")
                break

        # Falhou em todas as tentativas
        return {
            "type": "icmp_ping",
            "name": "ICMP Ping",
            "host": self.host,
            "status": "critical",
            "latency_ms": 0.0,
            "packet_loss_percent": 100.0,
            "min_ms": 0.0,
            "max_ms": 0.0,
            "avg_ms": 0.0,
            "is_online": False,
            "value": 0.0,
            "unit": "ms",
            "metadata": {
                "count": self.count,
                "timeout": self.timeout,
                "attempts": self.retries + 1,
                "error": last_error,
                "collection_method": "icmp",
            },
        }
