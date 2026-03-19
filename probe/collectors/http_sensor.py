"""
HTTP Sensor — Coruja Monitor v3.0
Verifica disponibilidade HTTP/HTTPS com latência, status code, SSL e conteúdo.
Equivalente ao sensor HTTP do PRTG/Zabbix.
"""
import time
import logging
import socket
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

try:
    import requests
    from requests.exceptions import (
        ConnectionError, Timeout, SSLError, TooManyRedirects
    )
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class HTTPSensor:
    """
    Sensor HTTP completo:
    - Status code validation
    - Latência (ms)
    - SSL certificate check
    - Content match (opcional)
    - Timeout configurável
    - Redirect follow (configurável)
    - Status: ok / warning / critical
    """

    def __init__(
        self,
        url: str,
        timeout: float = 10.0,
        expected_status: int = 200,
        content_match: Optional[str] = None,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        warning_latency_ms: float = 1000.0,
        critical_latency_ms: float = 5000.0,
        retries: int = 1,
    ):
        self.url = url
        self.timeout = timeout
        self.expected_status = expected_status
        self.content_match = content_match
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.warning_latency_ms = warning_latency_ms
        self.critical_latency_ms = critical_latency_ms
        self.retries = retries

        parsed = urlparse(url)
        self.host = parsed.hostname or url
        self.scheme = parsed.scheme or "http"

    def collect(self) -> Dict[str, Any]:
        """Executa verificação HTTP com retry e retorna resultado estruturado."""
        if not REQUESTS_AVAILABLE:
            return self._error_result("requests library not available")

        last_result = None
        for attempt in range(self.retries + 1):
            last_result = self._do_request()
            if last_result["status"] != "critical":
                return last_result

        return last_result

    def _do_request(self) -> Dict[str, Any]:
        start = time.monotonic()
        error_type = None
        status_code = None
        content_matched = None

        try:
            resp = requests.get(
                self.url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=self.follow_redirects,
                headers={"User-Agent": "CorujaMonitor/3.0"},
            )
            latency_ms = (time.monotonic() - start) * 1000
            status_code = resp.status_code

            # Content match
            if self.content_match:
                content_matched = self.content_match in resp.text

            # Determinar status
            status = self._determine_status(status_code, latency_ms, content_matched)

            return {
                "type": "http",
                "name": f"HTTP {self.url}",
                "host": self.host,
                "url": self.url,
                "status": status,
                "value": latency_ms,
                "unit": "ms",
                "status_code": status_code,
                "latency_ms": round(latency_ms, 2),
                "content_matched": content_matched,
                "ssl": self.scheme == "https",
                "metadata": {
                    "expected_status": self.expected_status,
                    "actual_status": status_code,
                    "content_match": self.content_match,
                    "verify_ssl": self.verify_ssl,
                },
            }

        except requests.exceptions.SSLError as e:
            latency_ms = (time.monotonic() - start) * 1000
            error_type = "ssl_error"
            return self._error_result(f"SSL error: {e}", error_type, latency_ms)

        except requests.exceptions.ConnectionError as e:
            latency_ms = (time.monotonic() - start) * 1000
            # Distinguish DNS failure
            err_str = str(e).lower()
            if "name or service not known" in err_str or "nodename nor servname" in err_str or "getaddrinfo" in err_str:
                error_type = "dns_failure"
            else:
                error_type = "connection_refused"
            return self._error_result(str(e), error_type, latency_ms)

        except requests.exceptions.Timeout as e:
            latency_ms = (time.monotonic() - start) * 1000
            return self._error_result(f"Timeout after {self.timeout}s", "timeout", latency_ms)

        except requests.exceptions.TooManyRedirects as e:
            latency_ms = (time.monotonic() - start) * 1000
            return self._error_result("Too many redirects", "redirect_loop", latency_ms)

        except Exception as e:
            latency_ms = (time.monotonic() - start) * 1000
            return self._error_result(str(e), "unknown", latency_ms)

    def _determine_status(self, status_code: int, latency_ms: float, content_matched: Optional[bool]) -> str:
        # Wrong status code → critical
        if status_code != self.expected_status:
            if status_code >= 500:
                return "critical"
            if status_code >= 400:
                return "warning"
            return "warning"

        # Content mismatch → warning
        if content_matched is False:
            return "warning"

        # Latency thresholds
        if latency_ms >= self.critical_latency_ms:
            return "critical"
        if latency_ms >= self.warning_latency_ms:
            return "warning"

        return "ok"

    def _error_result(self, error: str, error_type: str = "error", latency_ms: float = 0.0) -> Dict[str, Any]:
        return {
            "type": "http",
            "name": f"HTTP {self.url}",
            "host": self.host,
            "url": self.url,
            "status": "critical",
            "value": latency_ms,
            "unit": "ms",
            "status_code": None,
            "latency_ms": round(latency_ms, 2),
            "content_matched": None,
            "ssl": self.scheme == "https",
            "error": error,
            "error_type": error_type,
            "metadata": {
                "expected_status": self.expected_status,
                "verify_ssl": self.verify_ssl,
            },
        }
