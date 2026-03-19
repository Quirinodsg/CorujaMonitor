"""
FASE 2 — Testes do HTTP Sensor
Valida: HTTP 200, timeout, DNS failure, SSL error, latência, conteúdo.
"""
import pytest
import time
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../probe'))

from collectors.http_sensor import HTTPSensor


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_mock_response(status_code=200, text="OK", elapsed_ms=50):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    return resp


def patch_requests_get(response=None, side_effect=None):
    """Context manager para mockar requests.get."""
    import requests as req_lib
    if side_effect:
        return patch("requests.get", side_effect=side_effect)
    return patch("requests.get", return_value=response)


# ─── Testes básicos ──────────────────────────────────────────────────────────

class TestHTTPSensorBasic:

    def test_http_200_ok(self):
        """HTTP 200 dentro do threshold → status ok."""
        sensor = HTTPSensor("http://example.com", timeout=5.0)
        mock_resp = make_mock_response(200)

        with patch("requests.get", return_value=mock_resp) as mock_get:
            # Simular latência baixa via time.monotonic
            with patch("time.monotonic", side_effect=[0.0, 0.05]):  # 50ms
                result = sensor._do_request()

        assert result["status"] == "ok"
        assert result["status_code"] == 200
        assert result["type"] == "http"
        assert "latency_ms" in result

    def test_http_500_critical(self):
        """HTTP 500 → status critical."""
        sensor = HTTPSensor("http://example.com")
        mock_resp = make_mock_response(500)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        assert result["status"] == "critical"
        assert result["status_code"] == 500

    def test_http_404_warning(self):
        """HTTP 404 (esperado 200) → warning."""
        sensor = HTTPSensor("http://example.com", expected_status=200)
        mock_resp = make_mock_response(404)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        assert result["status"] == "warning"

    def test_http_expected_status_match(self):
        """Se expected_status=301 e recebe 301 → ok."""
        sensor = HTTPSensor("http://example.com", expected_status=301)
        mock_resp = make_mock_response(301)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        assert result["status"] == "ok"


# ─── Testes de timeout ───────────────────────────────────────────────────────

class TestHTTPSensorTimeout:

    def test_timeout_returns_critical(self):
        """Timeout → status critical, error_type timeout."""
        import requests as req_lib
        sensor = HTTPSensor("http://example.com", timeout=1.0)

        with patch("requests.get", side_effect=req_lib.exceptions.Timeout("timed out")):
            with patch("time.monotonic", side_effect=[0.0, 1.001]):
                result = sensor._do_request()

        assert result["status"] == "critical"
        assert result["error_type"] == "timeout"
        assert result["status_code"] is None

    def test_slow_response_warning(self):
        """Latência > warning_latency_ms → warning."""
        sensor = HTTPSensor("http://example.com", warning_latency_ms=500, critical_latency_ms=2000)
        mock_resp = make_mock_response(200)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.8]):  # 800ms
                result = sensor._do_request()

        assert result["status"] == "warning"
        assert result["latency_ms"] == pytest.approx(800.0, abs=1)

    def test_very_slow_response_critical(self):
        """Latência > critical_latency_ms → critical."""
        sensor = HTTPSensor("http://example.com", warning_latency_ms=500, critical_latency_ms=2000)
        mock_resp = make_mock_response(200)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 2.5]):  # 2500ms
                result = sensor._do_request()

        assert result["status"] == "critical"


# ─── Testes de DNS failure ───────────────────────────────────────────────────

class TestHTTPSensorDNS:

    def test_dns_failure(self):
        """DNS failure → critical, error_type dns_failure."""
        import requests as req_lib
        sensor = HTTPSensor("http://host-que-nao-existe.invalid")

        dns_error = req_lib.exceptions.ConnectionError(
            "HTTPConnectionPool: Max retries exceeded: getaddrinfo failed"
        )
        with patch("requests.get", side_effect=dns_error):
            with patch("time.monotonic", side_effect=[0.0, 0.1]):
                result = sensor._do_request()

        assert result["status"] == "critical"
        assert result["error_type"] == "dns_failure"

    def test_connection_refused(self):
        """Connection refused → critical, error_type connection_refused."""
        import requests as req_lib
        sensor = HTTPSensor("http://localhost:19999")

        conn_error = req_lib.exceptions.ConnectionError("Connection refused")
        with patch("requests.get", side_effect=conn_error):
            with patch("time.monotonic", side_effect=[0.0, 0.01]):
                result = sensor._do_request()

        assert result["status"] == "critical"
        assert result["error_type"] == "connection_refused"


# ─── Testes SSL ──────────────────────────────────────────────────────────────

class TestHTTPSensorSSL:

    def test_ssl_error_critical(self):
        """SSL error → critical, error_type ssl_error."""
        import requests as req_lib
        sensor = HTTPSensor("https://expired.badssl.com", verify_ssl=True)

        ssl_error = req_lib.exceptions.SSLError("SSL: CERTIFICATE_VERIFY_FAILED")
        with patch("requests.get", side_effect=ssl_error):
            with patch("time.monotonic", side_effect=[0.0, 0.1]):
                result = sensor._do_request()

        assert result["status"] == "critical"
        assert result["error_type"] == "ssl_error"
        assert result["ssl"] is True

    def test_ssl_disabled_ok(self):
        """verify_ssl=False ignora erros de certificado."""
        sensor = HTTPSensor("https://example.com", verify_ssl=False)
        mock_resp = make_mock_response(200)

        with patch("requests.get", return_value=mock_resp) as mock_get:
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        # Verifica que verify=False foi passado
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs.get("verify") is False
        assert result["status"] == "ok"


# ─── Testes de content match ─────────────────────────────────────────────────

class TestHTTPSensorContent:

    def test_content_match_found(self):
        """Content match encontrado → ok."""
        sensor = HTTPSensor("http://example.com", content_match="Welcome")
        mock_resp = make_mock_response(200, text="Welcome to our site!")

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        assert result["status"] == "ok"
        assert result["content_matched"] is True

    def test_content_match_not_found(self):
        """Content match não encontrado → warning."""
        sensor = HTTPSensor("http://example.com", content_match="Expected Text")
        mock_resp = make_mock_response(200, text="Something else entirely")

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        assert result["status"] == "warning"
        assert result["content_matched"] is False


# ─── Testes de retry ─────────────────────────────────────────────────────────

class TestHTTPSensorRetry:

    def test_retry_on_failure(self):
        """Com retries=1, tenta 2x antes de retornar critical."""
        import requests as req_lib
        sensor = HTTPSensor("http://example.com", retries=1)
        call_count = {"n": 0}

        def flaky_get(*args, **kwargs):
            call_count["n"] += 1
            raise req_lib.exceptions.ConnectionError("Connection refused")

        # Patch no namespace do módulo (importado via sys.path como collectors.http_sensor)
        with patch("collectors.http_sensor.requests.get", side_effect=flaky_get):
            with patch("time.monotonic", return_value=0.0):
                result = sensor.collect()

        assert result["status"] == "critical"
        # retries=1 → 2 chamadas ao requests.get
        assert call_count["n"] == 2

    def test_retry_succeeds_on_second_attempt(self):
        """Falha na 1ª tentativa, sucesso na 2ª."""
        import requests as req_lib
        sensor = HTTPSensor("http://example.com", retries=1)
        call_count = {"n": 0}
        mock_resp = make_mock_response(200)

        def flaky_get(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise req_lib.exceptions.ConnectionError("Connection refused")
            return mock_resp

        # Patch no namespace do módulo (importado via sys.path como collectors.http_sensor)
        with patch("collectors.http_sensor.requests.get", side_effect=flaky_get):
            with patch("time.monotonic", return_value=0.0):
                result = sensor.collect()

        assert result["status"] == "ok"
        assert call_count["n"] == 2


# ─── Testes de estrutura do resultado ────────────────────────────────────────

class TestHTTPSensorResultStructure:

    def test_result_has_required_fields(self):
        """Resultado sempre tem campos obrigatórios."""
        sensor = HTTPSensor("http://example.com")
        mock_resp = make_mock_response(200)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.05]):
                result = sensor._do_request()

        required = ["type", "name", "host", "url", "status", "value", "unit",
                    "status_code", "latency_ms", "ssl", "metadata"]
        for field in required:
            assert field in result, f"Campo '{field}' ausente no resultado"

    def test_error_result_has_required_fields(self):
        """Resultado de erro sempre tem campos obrigatórios."""
        sensor = HTTPSensor("http://example.com")
        result = sensor._error_result("test error", "test_type", 100.0)

        assert result["status"] == "critical"
        assert result["error"] == "test error"
        assert result["error_type"] == "test_type"
        assert result["latency_ms"] == 100.0
        assert result["status_code"] is None

    def test_latency_in_result(self):
        """Latência deve estar em ms e ser positiva."""
        sensor = HTTPSensor("http://example.com")
        mock_resp = make_mock_response(200)

        with patch("requests.get", return_value=mock_resp):
            with patch("time.monotonic", side_effect=[0.0, 0.123]):
                result = sensor._do_request()

        assert result["latency_ms"] == pytest.approx(123.0, abs=1)
        assert result["value"] == result["latency_ms"]
        assert result["unit"] == "ms"
