#!/bin/bash

echo "========================================="
echo "  ATUALIZAR SERVIDOR LINUX SEM GIT"
echo "========================================="
echo ""

# Configurações
SERVIDOR="192.168.31.161"
USUARIO="root"
PASTA_DESTINO="/home/administrador/CorujaMonitor"

echo "Copiando arquivos para o servidor Linux..."
echo ""

# Copiar arquivos da API
scp api/reset_sistema.py ${USUARIO}@${SERVIDOR}:${PASTA_DESTINO}/api/
scp api/routers/system_reset.py ${USUARIO}@${SERVIDOR}:${PASTA_DESTINO}/api/routers/
scp api/main.py ${USUARIO}@${SERVIDOR}:${PASTA_DESTINO}/api/

# Copiar arquivos do frontend
scp frontend/src/components/SystemReset.js ${USUARIO}@${SERVIDOR}:${PASTA_DESTINO}/frontend/src/components/
scp frontend/src/components/SystemReset.css ${USUARIO}@${SERVIDOR}:${PASTA_DESTINO}/frontend/src/components/

echo ""
echo "========================================="
echo "  ✓ ARQUIVOS COPIADOS!"
echo "========================================="
echo ""
echo "Agora execute no servidor Linux:"
echo ""
echo "  cd ${PASTA_DESTINO}"
echo "  docker-compose restart"
echo ""
echo "Ou reinicie manualmente:"
echo "  cd ${PASTA_DESTINO}/api"
echo "  python reset_sistema.py"
echo ""
