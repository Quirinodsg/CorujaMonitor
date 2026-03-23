#!/bin/bash
# =============================================================================
# Deploy do certificado A2Hosting (*.techbiz.com.br) no servidor Linux
# Executa na sua máquina local: bash _deploy_cert_linux.sh
# Requer: acesso SSH ao servidor 192.168.31.161
# =============================================================================

SERVER="192.168.31.161"
SERVER_USER="administrador"
REMOTE_DIR="/home/administrador/CorujaMonitor"

echo "=== Deploy Certificado Let's Encrypt (A2Hosting) ==="
echo "Servidor: $SERVER"
echo ""

# Copiar certificado (CRT com chain) e chave para o servidor
echo "[1/3] Copiando certificados para o servidor..."
scp nginx/ssl/coruja.crt ${SERVER_USER}@${SERVER}:${REMOTE_DIR}/nginx/ssl/coruja.crt
scp nginx/ssl/coruja.key ${SERVER_USER}@${SERVER}:${REMOTE_DIR}/nginx/ssl/coruja.key

echo "[2/3] Ajustando permissões e recarregando nginx..."
ssh ${SERVER_USER}@${SERVER} "
    chmod 644 ${REMOTE_DIR}/nginx/ssl/coruja.crt
    chmod 600 ${REMOTE_DIR}/nginx/ssl/coruja.key
    docker exec coruja-nginx nginx -t && docker exec coruja-nginx nginx -s reload
"

echo "[3/3] Verificando certificado ativo..."
ssh ${SERVER_USER}@${SERVER} "
    echo | openssl s_client -connect localhost:443 -servername coruja.techbiz.com.br 2>/dev/null \
        | openssl x509 -noout -subject -dates -issuer 2>/dev/null \
        && echo '✅ Certificado válido ativo no nginx'
"

echo ""
echo "=== Concluído ==="
echo "Acesse: https://coruja.techbiz.com.br"
echo "Resultado esperado: 🔒 cadeado verde, sem aviso"
