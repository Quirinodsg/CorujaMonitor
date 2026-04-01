#!/bin/bash
# =============================================================================
# Deploy Let's Encrypt no servidor Linux
# Executa no servidor: bash _setup_letsencrypt_linux.sh
# Pré-requisito: porta 80 liberada externamente para coruja.empresaxpto.com.br
# =============================================================================
set -e

cd /home/administrador/CorujaMonitor

echo "=== Deploy Let's Encrypt - Coruja Monitor ==="
echo ""

# 1. Atualizar código
echo "[1/4] Atualizando código..."
git pull

# 2. Criar diretório webroot no host
echo "[2/4] Criando diretório webroot..."
mkdir -p /var/www/certbot/.well-known/acme-challenge

# 3. Recriar nginx com novo volume do webroot
echo "[3/4] Recriando nginx com suporte a webroot..."
docker rm -f coruja-nginx 2>/dev/null || true
docker-compose up -d nginx
sleep 5

docker ps | grep coruja-nginx && echo "✅ nginx rodando" || { echo "❌ nginx falhou"; exit 1; }

# 4. Rodar setup do Let's Encrypt
echo "[4/4] Executando setup Let's Encrypt..."
echo ""
bash scripts/setup-letsencrypt.sh
