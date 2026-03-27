#!/bin/bash
# Cria CA privada TechBiz e emite certificado para coruja.techbiz.com.br
# Uso: bash scripts/setup-internal-ca.sh
set -e

DOMAIN="${CORUJA_DOMAIN:-coruja.techbiz.com.br}"
SERVER_IP="${CORUJA_SERVER_IP:-192.168.31.161}"
SSL_DIR="/etc/nginx/ssl"
CA_DIR="$SSL_DIR/ca"
DAYS_CA=3650    # CA válida por 10 anos
DAYS_CERT=730   # Cert válido por 2 anos

mkdir -p "$CA_DIR"

echo "=== [1/4] Gerando CA privada TechBiz ==="
# Gerar chave da CA
openssl genrsa -out "$CA_DIR/ca.key" 4096

# Gerar certificado raiz da CA (self-signed)
openssl req -x509 -new -nodes \
    -key "$CA_DIR/ca.key" \
    -sha256 \
    -days $DAYS_CA \
    -out "$CA_DIR/ca.crt" \
    -subj "/C=BR/ST=SP/L=SaoPaulo/O=TechBiz/OU=IT/CN=TechBiz Internal CA"

echo "✅ CA gerada: $CA_DIR/ca.crt"

echo "=== [2/4] Gerando chave e CSR para $DOMAIN ==="
openssl genrsa -out "$SSL_DIR/coruja.key" 2048

# CSR com SAN via arquivo de configuração
cat > /tmp/coruja-csr.conf <<EOF
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
req_extensions     = req_ext

[dn]
C  = BR
ST = SP
L  = SaoPaulo
O  = TechBiz
OU = IT
CN = $DOMAIN

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
IP.1  = $SERVER_IP
IP.2  = 127.0.0.1
EOF

openssl req -new \
    -key "$SSL_DIR/coruja.key" \
    -out /tmp/coruja.csr \
    -config /tmp/coruja-csr.conf

echo "=== [3/4] Assinando certificado com a CA TechBiz ==="
cat > /tmp/coruja-ext.conf <<EOF
authorityKeyIdentifier = keyid,issuer
basicConstraints       = CA:FALSE
keyUsage               = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage       = serverAuth
subjectAltName         = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
IP.1  = $SERVER_IP
IP.2  = 127.0.0.1
EOF

openssl x509 -req \
    -in /tmp/coruja.csr \
    -CA "$CA_DIR/ca.crt" \
    -CAkey "$CA_DIR/ca.key" \
    -CAcreateserial \
    -out "$SSL_DIR/coruja.crt" \
    -days $DAYS_CERT \
    -sha256 \
    -extfile /tmp/coruja-ext.conf

chmod 600 "$SSL_DIR/coruja.key"
chmod 644 "$SSL_DIR/coruja.crt"
chmod 600 "$CA_DIR/ca.key"
chmod 644 "$CA_DIR/ca.crt"

# Limpar arquivos temporários
rm -f /tmp/coruja-csr.conf /tmp/coruja.csr /tmp/coruja-ext.conf

echo "=== [4/4] Verificando certificado ==="
openssl x509 -in "$SSL_DIR/coruja.crt" -text -noout | grep -A4 "Subject Alternative Name"
openssl verify -CAfile "$CA_DIR/ca.crt" "$SSL_DIR/coruja.crt" && echo "✅ Certificado válido pela CA TechBiz"

echo ""
echo "=== CONCLUÍDO ==="
echo "Certificado: $SSL_DIR/coruja.crt (válido $DAYS_CERT dias)"
echo "CA Root:     $CA_DIR/ca.crt"
echo ""
echo "PRÓXIMO PASSO — Distribuir a CA nos browsers:"
echo "  Copie o arquivo: $CA_DIR/ca.crt"
echo "  Windows: duplo-clique → Instalar → 'Autoridades de Certificação Raiz Confiáveis'"
echo "  Chrome/Edge: Configurações → Privacidade → Certificados → Autoridades → Importar"
echo "  Firefox: about:preferences#privacy → Ver Certificados → Autoridades → Importar"
