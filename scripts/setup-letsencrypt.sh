#!/bin/bash
# =============================================================================
# Let's Encrypt - Certbot via webroot para coruja.techbiz.com.br
# Pré-requisito: porta 80 acessível externamente (http://coruja.techbiz.com.br)
# Uso: bash scripts/setup-letsencrypt.sh
# =============================================================================
set -e

DOMAIN="${CORUJA_DOMAIN:-coruja.techbiz.com.br}"
EMAIL="${CERTBOT_EMAIL:-admin@techbiz.com.br}"
WEBROOT="/var/www/certbot"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
NGINX_SSL_DIR="./nginx/ssl"

echo "=== Let's Encrypt Setup para $DOMAIN ==="
echo ""

# --- 1. Verificar se porta 80 está acessível externamente ---
echo "[1/6] Verificando acesso externo na porta 80..."
EXTERNAL_IP=$(curl -s --max-time 10 https://api.ipify.org 2>/dev/null || echo "desconhecido")
echo "      IP externo do servidor: $EXTERNAL_IP"

HTTP_CHECK=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "http://$DOMAIN/.well-known/acme-challenge/test" 2>/dev/null || echo "000")

if [ "$HTTP_CHECK" = "404" ] || [ "$HTTP_CHECK" = "200" ]; then
    echo "      ✅ Porta 80 acessível (HTTP $HTTP_CHECK)"
else
    echo "      ⚠️  Porta 80 retornou HTTP $HTTP_CHECK"
    echo "      Verifique se o port-forward 80→192.168.31.161:80 está ativo"
    echo "      e se o DNS $DOMAIN aponta para $EXTERNAL_IP"
    echo ""
    read -p "Continuar mesmo assim? (s/N): " CONFIRM
    [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ] && exit 1
fi

# --- 2. Instalar Certbot ---
echo "[2/6] Instalando Certbot..."
if command -v certbot &>/dev/null; then
    echo "      ✅ Certbot já instalado: $(certbot --version 2>&1)"
else
    apt-get update -qq
    apt-get install -y certbot
    echo "      ✅ Certbot instalado"
fi

# --- 3. Preparar diretório webroot e nginx ---
echo "[3/6] Preparando webroot para challenge..."
mkdir -p "$WEBROOT/.well-known/acme-challenge"

# Atualizar nginx para servir o webroot (temporariamente sem redirect na porta 80)
docker exec coruja-nginx sh -c "
    mkdir -p /var/www/certbot/.well-known/acme-challenge
    echo 'ok' > /var/www/certbot/.well-known/acme-challenge/test
"

# Recarregar nginx com config que serve o webroot
docker exec coruja-nginx nginx -s reload 2>/dev/null || true
echo "      ✅ Webroot configurado"

# --- 4. Gerar certificado ---
echo "[4/6] Gerando certificado Let's Encrypt..."
certbot certonly \
    --webroot \
    --webroot-path "$WEBROOT" \
    --domain "$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --non-interactive \
    --expand

echo "      ✅ Certificado gerado em $CERT_DIR"

# --- 5. Copiar certificados para o nginx ---
echo "[5/6] Copiando certificados para nginx..."
mkdir -p "$NGINX_SSL_DIR"
cp "$CERT_DIR/fullchain.pem" "$NGINX_SSL_DIR/coruja.crt"
cp "$CERT_DIR/privkey.pem"   "$NGINX_SSL_DIR/coruja.key"
chmod 644 "$NGINX_SSL_DIR/coruja.crt"
chmod 600 "$NGINX_SSL_DIR/coruja.key"

# Recarregar nginx com novo certificado
docker exec coruja-nginx nginx -s reload
echo "      ✅ Nginx recarregado com certificado Let's Encrypt"

# --- 6. Configurar renovação automática ---
echo "[6/6] Configurando renovação automática..."
RENEW_SCRIPT="/home/administrador/CorujaMonitor/scripts/renew-letsencrypt.sh"

cat > "$RENEW_SCRIPT" <<'RENEW_EOF'
#!/bin/bash
# Renovação automática Let's Encrypt
DOMAIN="${CORUJA_DOMAIN:-coruja.techbiz.com.br}"
NGINX_SSL_DIR="/home/administrador/CorujaMonitor/nginx/ssl"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
LOG="/var/log/letsencrypt-renew.log"

echo "[$(date)] Iniciando renovação..." >> "$LOG"

certbot renew --quiet --webroot \
    --webroot-path /var/www/certbot 2>> "$LOG"

# Copiar se renovado
if [ "$CERT_DIR/fullchain.pem" -nt "$NGINX_SSL_DIR/coruja.crt" ]; then
    cp "$CERT_DIR/fullchain.pem" "$NGINX_SSL_DIR/coruja.crt"
    cp "$CERT_DIR/privkey.pem"   "$NGINX_SSL_DIR/coruja.key"
    chmod 644 "$NGINX_SSL_DIR/coruja.crt"
    chmod 600 "$NGINX_SSL_DIR/coruja.key"
    docker exec coruja-nginx nginx -s reload
    echo "[$(date)] ✅ Certificado renovado e nginx recarregado" >> "$LOG"
else
    echo "[$(date)] Certificado ainda válido, sem renovação necessária" >> "$LOG"
fi
RENEW_EOF

chmod +x "$RENEW_SCRIPT"

# Adicionar cron: renovar às 3h todo dia
CRON_LINE="0 3 * * * $RENEW_SCRIPT"
(crontab -l 2>/dev/null | grep -v "renew-letsencrypt"; echo "$CRON_LINE") | crontab -
echo "      ✅ Cron configurado: renovação diária às 3h"

# --- Resultado ---
echo ""
echo "=============================================="
echo "✅ Let's Encrypt configurado com sucesso!"
echo "=============================================="
echo ""
echo "Domínio:     $DOMAIN"
echo "Certificado: $NGINX_SSL_DIR/coruja.crt"
echo "Expira em:   $(openssl x509 -in "$NGINX_SSL_DIR/coruja.crt" -noout -enddate 2>/dev/null | cut -d= -f2)"
echo "Renovação:   automática diária às 3h"
echo ""
echo "Acesse: https://$DOMAIN"
echo "Resultado esperado: 🔒 cadeado verde, sem aviso de segurança"
