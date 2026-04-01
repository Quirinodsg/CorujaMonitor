#!/bin/bash
# Gera certificado SSL self-signed para o Coruja Monitor
# Uso: ./scripts/generate-ssl-cert.sh

SSL_DIR="/etc/nginx/ssl"
CERT="$SSL_DIR/coruja.crt"
KEY="$SSL_DIR/coruja.key"
DOMAIN="${CORUJA_DOMAIN:-coruja.empresaxpto.com.br}"
SERVER_IP="${CORUJA_SERVER_IP:-192.168.1.100}"

mkdir -p "$SSL_DIR"

openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout "$KEY" \
    -out "$CERT" \
    -subj "/C=BR/ST=SP/L=SaoPaulo/O=EmpresaXPTO/OU=IT/CN=$DOMAIN" \
    -addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:$SERVER_IP,IP:127.0.0.1"

chmod 600 "$KEY"
chmod 644 "$CERT"

echo "✅ Certificado gerado em $CERT (válido por 365 dias)"
echo "   CN=$DOMAIN | SAN: DNS:$DOMAIN, DNS:localhost, IP:$SERVER_IP, IP:127.0.0.1"
