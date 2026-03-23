"""
tests/v35/test_https_redirect.py
Testes para Requirement 4: Redirect HTTP → HTTPS via Nginx
Verifica conteúdo dos arquivos de configuração.
"""
import os
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NGINX_CONF = os.path.join(BASE_DIR, "nginx", "nginx.conf")
DOCKER_COMPOSE = os.path.join(BASE_DIR, "docker-compose.yml")
GENERATE_CERT = os.path.join(BASE_DIR, "scripts", "generate-ssl-cert.sh")
RENEW_CERT = os.path.join(BASE_DIR, "scripts", "renew-ssl-cert.sh")


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestNginxConf:
    """Requirement 4.1, 4.2, 4.6"""

    def test_nginx_conf_exists(self):
        assert os.path.exists(NGINX_CONF), f"nginx/nginx.conf não encontrado em {NGINX_CONF}"

    def test_http_redirect_301(self):
        content = read_file(NGINX_CONF)
        assert "return 301 https://" in content, \
            "nginx.conf deve conter redirect 301 para HTTPS"

    def test_listen_80(self):
        content = read_file(NGINX_CONF)
        assert "listen 80" in content, "nginx.conf deve ter listen 80"

    def test_listen_443_ssl(self):
        content = read_file(NGINX_CONF)
        assert "listen 443 ssl" in content, "nginx.conf deve ter listen 443 ssl"

    def test_ssl_certificate_present(self):
        content = read_file(NGINX_CONF)
        assert "ssl_certificate" in content, "nginx.conf deve ter bloco ssl_certificate"

    def test_ssl_certificate_key_present(self):
        content = read_file(NGINX_CONF)
        assert "ssl_certificate_key" in content

    def test_api_proxy_pass(self):
        content = read_file(NGINX_CONF)
        assert "proxy_pass" in content and "/api/" in content, \
            "nginx.conf deve ter proxy_pass para /api/"

    def test_frontend_proxy_pass(self):
        content = read_file(NGINX_CONF)
        assert "frontend:3000" in content, \
            "nginx.conf deve ter proxy_pass para frontend:3000"

    def test_tls_protocols(self):
        content = read_file(NGINX_CONF)
        assert "TLSv1.2" in content or "TLSv1.3" in content, \
            "nginx.conf deve especificar protocolos TLS"

    def test_websocket_upgrade(self):
        content = read_file(NGINX_CONF)
        assert "Upgrade" in content, "nginx.conf deve suportar WebSocket (Upgrade header)"


class TestDockerCompose:
    """Requirement 4.5"""

    def test_docker_compose_exists(self):
        assert os.path.exists(DOCKER_COMPOSE)

    def test_nginx_service_present(self):
        content = read_file(DOCKER_COMPOSE)
        assert "nginx:" in content, "docker-compose.yml deve ter serviço nginx"

    def test_nginx_port_80(self):
        content = read_file(DOCKER_COMPOSE)
        assert '"80:80"' in content or "'80:80'" in content or "- 80:80" in content, \
            "docker-compose.yml deve expor porta 80"

    def test_nginx_port_443(self):
        content = read_file(DOCKER_COMPOSE)
        assert '"443:443"' in content or "'443:443'" in content or "- 443:443" in content, \
            "docker-compose.yml deve expor porta 443"

    def test_nginx_depends_on_api(self):
        content = read_file(DOCKER_COMPOSE)
        # Verifica que nginx está após api na seção depends_on
        nginx_idx = content.find("nginx:")
        api_idx = content.find("coruja-api")
        assert nginx_idx > 0, "Serviço nginx deve existir"


class TestSSLScripts:
    """Requirements 4.3, 4.4"""

    def test_generate_cert_script_exists(self):
        assert os.path.exists(GENERATE_CERT), \
            f"scripts/generate-ssl-cert.sh não encontrado"

    def test_generate_cert_uses_openssl(self):
        content = read_file(GENERATE_CERT)
        assert "openssl req" in content, \
            "generate-ssl-cert.sh deve usar openssl req"

    def test_generate_cert_creates_key_and_cert(self):
        content = read_file(GENERATE_CERT)
        assert ".key" in content and ".crt" in content, \
            "generate-ssl-cert.sh deve criar .key e .crt"

    def test_renew_cert_script_exists(self):
        assert os.path.exists(RENEW_CERT), \
            f"scripts/renew-ssl-cert.sh não encontrado"

    def test_renew_cert_checks_expiry(self):
        content = read_file(RENEW_CERT)
        assert "openssl x509" in content, \
            "renew-ssl-cert.sh deve verificar expiração com openssl x509"

    def test_renew_cert_30_days_threshold(self):
        content = read_file(RENEW_CERT)
        assert "30" in content, \
            "renew-ssl-cert.sh deve verificar antecedência de 30 dias"
