"""
Testes de validação do fix HTTPS para o Coruja Monitor.

Metodologia:
- Bug Condition tests: DEVEM FALHAR no código não corrigido (confirmam que o bug existe)
- Preservation tests: DEVEM PASSAR no código não corrigido (confirmam baseline a preservar)
"""

import os
import re
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

# ─── Caminhos dos arquivos ────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATE_SSL_SCRIPT = os.path.join(ROOT, "scripts", "generate-ssl-cert.sh")
DASHBOARD_JS        = os.path.join(ROOT, "frontend", "src", "components", "Dashboard.js")
ENTRYPOINT_SSL      = os.path.join(ROOT, "nginx", "docker-entrypoint-ssl.sh")
NGINX_CONF          = os.path.join(ROOT, "nginx", "nginx.conf")
CONFIG_JS           = os.path.join(ROOT, "frontend", "src", "config.js")
CERT_FILE           = os.path.join(ROOT, "nginx", "ssl", "coruja.crt")


# ═══════════════════════════════════════════════════════════════════════════════
# BUG CONDITION TESTS — devem FALHAR no código não corrigido
# ═══════════════════════════════════════════════════════════════════════════════

def test_cert_has_san_ip():
    """
    Bug Condition: O script generate-ssl-cert.sh NÃO inclui IP:192.168.31.161 no SAN.
    Browsers modernos (Chrome 58+) exigem SAN com IP para aceitar o certificado.
    FALHA no código atual: SAN atual é DNS:coruja.techbiz.com.br,DNS:localhost,IP:127.0.0.1
    """
    with open(GENERATE_SSL_SCRIPT) as f:
        content = f.read()

    # O script deve conter IP:192.168.31.161 ou IP:$SERVER_IP no SAN
    has_server_ip_var = "SERVER_IP" in content and "IP:$SERVER_IP" in content
    has_literal_ip    = "IP:192.168.31.161" in content

    assert has_server_ip_var or has_literal_ip, (
        "BUG CONFIRMADO: scripts/generate-ssl-cert.sh não inclui IP do servidor no SAN. "
        "Browsers modernos rejeitam certificados sem SAN para o IP de acesso. "
        f"SAN atual no script: {re.findall(r'subjectAltName=[^\"]+', content)}"
    )


def test_cert_has_san_domain():
    """
    Bug Condition: O certificado deve incluir DNS:coruja.techbiz.com.br no SAN.
    """
    with open(GENERATE_SSL_SCRIPT) as f:
        content = f.read()

    has_domain_var  = "DOMAIN" in content and "DNS:$DOMAIN" in content
    has_literal_dom = "DNS:coruja.techbiz.com.br" in content

    assert has_domain_var or has_literal_dom, (
        "BUG CONFIRMADO: scripts/generate-ssl-cert.sh não inclui DNS do domínio no SAN."
    )


def test_dashboard_ws_url_no_hardcoded_port():
    """
    Bug Condition: Dashboard.js usa :8000 hardcoded na WS_URL.
    Em HTTPS, o WebSocket deve passar pelo nginx (porta 443), não direto na 8000.
    FALHA no código atual: `${proto}//${window.location.hostname}:8000/api/v1/ws/dashboard`
    """
    with open(DASHBOARD_JS) as f:
        content = f.read()

    # Extrair o bloco WS_URL
    ws_block_match = re.search(r'const WS_URL\s*=\s*\(\(\)\s*=>\s*\{(.+?)\}\)\(\)', content, re.DOTALL)
    assert ws_block_match, "Constante WS_URL não encontrada em Dashboard.js"

    ws_block = ws_block_match.group(1)

    # O bloco NÃO deve conter :8000 como valor incondicional (fora de ternário/else)
    # Padrão problemático: return `${proto}//${window.location.hostname}:8000/...`
    # Padrão correto: `:8000` só aparece no branch do ternário (após `?` ou `:`)
    # Verificar se :8000 aparece diretamente no return (sem condicional)
    has_unconditional_8000 = bool(re.search(r'return\s+`\$\{proto\}//\$\{window\.location\.hostname\}:8000', ws_block))

    assert not has_unconditional_8000, (
        "BUG CONFIRMADO: Dashboard.js usa :8000 hardcoded na WS_URL sem condicional. "
        "Em HTTPS, o WebSocket deve usar window.location.host (sem porta hardcoded) "
        "para passar pelo nginx na porta 443. "
        f"Bloco WS_URL atual: {ws_block.strip()}"
    )


def test_entrypoint_configures_cron():
    """
    Bug Condition: nginx/docker-entrypoint-ssl.sh não existe.
    Sem entrypoint customizado, o cron de renovação do certificado nunca é configurado.
    FALHA no código atual: arquivo não existe.
    """
    assert os.path.exists(ENTRYPOINT_SSL), (
        "BUG CONFIRMADO: nginx/docker-entrypoint-ssl.sh não existe. "
        "Sem este arquivo, o container nginx não configura o cron de renovação SSL."
    )

    with open(ENTRYPOINT_SSL) as f:
        content = f.read()

    assert "crond" in content, (
        "BUG CONFIRMADO: nginx/docker-entrypoint-ssl.sh existe mas não configura crond. "
        "O cron de renovação SSL não será executado automaticamente."
    )

    assert "renew-ssl-cert.sh" in content, (
        "BUG CONFIRMADO: entrypoint não referencia renew-ssl-cert.sh no cron job."
    )


@given(
    server_ip=st.from_regex(
        r'(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}',
        fullmatch=True
    )
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
def test_generate_ssl_script_has_server_ip(server_ip):
    """
    Property-Based: Para qualquer IP de servidor privado, o script deve suportar
    configuração via variável de ambiente CORUJA_SERVER_IP.
    """
    with open(GENERATE_SSL_SCRIPT) as f:
        content = f.read()

    # O script deve usar uma variável para o IP (não hardcoded)
    assert "SERVER_IP" in content, (
        f"BUG CONFIRMADO: scripts/generate-ssl-cert.sh não usa variável SERVER_IP. "
        f"Para o IP {server_ip}, o certificado não seria gerado com o SAN correto."
    )
    assert "CORUJA_SERVER_IP" in content or "${CORUJA_SERVER_IP:-" in content, (
        f"BUG CONFIRMADO: SERVER_IP não é configurável via env CORUJA_SERVER_IP. "
        f"Para o IP {server_ip}, seria necessário editar o script manualmente."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PRESERVATION TESTS — devem PASSAR no código não corrigido (e após o fix)
# ═══════════════════════════════════════════════════════════════════════════════

def test_http_redirects_to_https():
    """
    Preservation: nginx.conf deve redirecionar HTTP→HTTPS (return 301).
    Este comportamento deve ser preservado após o fix.
    """
    with open(NGINX_CONF) as f:
        content = f.read()

    assert "return 301 https://" in content, (
        "REGRESSÃO: nginx.conf perdeu o redirect HTTP→HTTPS (return 301 https://)"
    )

    # Verificar que está no bloco listen 80
    listen80_block = re.search(r'listen 80;.*?return 301', content, re.DOTALL)
    assert listen80_block, (
        "REGRESSÃO: redirect 301 não está no bloco listen 80 do nginx.conf"
    )


def test_config_js_uses_relative_url():
    """
    Preservation: config.js deve usar URL relativa /api/v1 quando não na porta 3000.
    Este comportamento foi corrigido anteriormente e deve ser preservado.
    """
    with open(CONFIG_JS) as f:
        content = f.read()

    assert "/api/v1" in content, (
        "REGRESSÃO: config.js não contém /api/v1"
    )

    # Verificar que usa URL relativa no bloco else (não porta 3000)
    assert "API_URL = `/api/v1`" in content or "API_URL = '/api/v1'" in content, (
        "REGRESSÃO: config.js não usa URL relativa /api/v1 para acesso via nginx"
    )


def test_config_js_port_3000_uses_absolute_url():
    """
    Preservation: config.js deve usar URL absoluta http://hostname:8000/api/v1
    quando acessado na porta 3000 (modo dev direto sem nginx).
    """
    with open(CONFIG_JS) as f:
        content = f.read()

    assert "port === '3000'" in content or 'port === "3000"' in content, (
        "REGRESSÃO: config.js perdeu a lógica de detecção de porta 3000"
    )

    assert ":8000/api/v1" in content, (
        "REGRESSÃO: config.js perdeu a URL absoluta para modo dev (porta 3000)"
    )


def test_nginx_conf_has_ssl():
    """
    Preservation: nginx.conf deve ter ssl_certificate e ssl_certificate_key configurados.
    """
    with open(NGINX_CONF) as f:
        content = f.read()

    assert "ssl_certificate " in content, (
        "REGRESSÃO: nginx.conf perdeu ssl_certificate"
    )
    assert "ssl_certificate_key " in content, (
        "REGRESSÃO: nginx.conf perdeu ssl_certificate_key"
    )
    assert "listen 443 ssl" in content, (
        "REGRESSÃO: nginx.conf perdeu listen 443 ssl"
    )


def test_nginx_conf_websocket_upgrade():
    """
    Preservation: nginx.conf deve ter headers Upgrade e Connection no bloco WebSocket.
    """
    with open(NGINX_CONF) as f:
        content = f.read()

    # Verificar bloco WebSocket
    ws_block = re.search(r'location /api/v1/ws/\s*\{(.+?)\}', content, re.DOTALL)
    assert ws_block, "REGRESSÃO: nginx.conf perdeu o bloco location /api/v1/ws/"

    ws_content = ws_block.group(1)
    assert "Upgrade" in ws_content, (
        "REGRESSÃO: nginx.conf perdeu header Upgrade no bloco WebSocket"
    )
    assert 'Connection "upgrade"' in ws_content or "Connection 'upgrade'" in ws_content, (
        "REGRESSÃO: nginx.conf perdeu header Connection upgrade no bloco WebSocket"
    )


def test_nginx_conf_proxy_headers():
    """
    Preservation: nginx.conf deve ter headers de proxy no bloco /api/.
    """
    with open(NGINX_CONF) as f:
        content = f.read()

    api_block = re.search(r'location /api/\s*\{(.+?)\}', content, re.DOTALL)
    assert api_block, "REGRESSÃO: nginx.conf perdeu o bloco location /api/"

    api_content = api_block.group(1)
    assert "X-Forwarded-Proto" in api_content, (
        "REGRESSÃO: nginx.conf perdeu header X-Forwarded-Proto no bloco /api/"
    )
    assert "X-Real-IP" in api_content, (
        "REGRESSÃO: nginx.conf perdeu header X-Real-IP no bloco /api/"
    )
    assert "X-Forwarded-For" in api_content, (
        "REGRESSÃO: nginx.conf perdeu header X-Forwarded-For no bloco /api/"
    )
