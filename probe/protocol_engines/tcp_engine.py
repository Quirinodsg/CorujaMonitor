"""
TCP Engine - Verificação de porta TCP com medição de latência
"""
import socket
import time
import logging

from .base_engine import BaseProtocolEngine, EngineResult

logger = logging.getLogger(__name__)


class TCPEngine(BaseProtocolEngine):
    """Engine TCP usando socket. Retorna latência em ms."""

    def __init__(self, timeout: float = 3.0, retries: int = 2):
        self._timeout = timeout
        self._retries = retries

    def is_available(self) -> bool:
        return True  # socket está sempre disponível

    def execute(self, host: str, **kwargs) -> EngineResult:
        port = kwargs.get("port")
        if port is None:
            return EngineResult(
                status="unknown",
                error="port_required",
                metadata={"host": host},
            )

        timeout = kwargs.get("timeout", self._timeout)
        retries = kwargs.get("retries", self._retries)

        last_error = None
        for attempt in range(retries + 1):
            ok, latency_ms, err = self._tcp_connect(host, int(port), float(timeout))
            if ok:
                return EngineResult(
                    status="ok",
                    value=round(latency_ms, 2),
                    unit="ms",
                    metadata={
                        "host": host,
                        "port": port,
                        "latency_ms": round(latency_ms, 2),
                        "attempts": attempt + 1,
                    },
                )
            last_error = err
            if attempt < retries:
                time.sleep(0.5)

        return EngineResult(
            status="critical",
            value=0.0,
            unit="ms",
            error="port_unreachable",
            metadata={
                "host": host,
                "port": port,
                "attempts": retries + 1,
                "last_error": last_error,
            },
        )

    def _tcp_connect(self, host: str, port: int, timeout: float):
        """Tenta conexão TCP. Retorna (sucesso, latencia_ms, erro)"""
        start = time.monotonic()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            latency_ms = (time.monotonic() - start) * 1000
            if result == 0:
                return True, latency_ms, None
            return False, 0.0, f"connect_ex={result}"
        except socket.timeout:
            return False, 0.0, "timeout"
        except ConnectionRefusedError:
            return False, 0.0, "connection_refused"
        except OSError as e:
            return False, 0.0, str(e)
