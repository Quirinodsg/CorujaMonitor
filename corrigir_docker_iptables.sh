#!/bin/bash
# Script para corrigir iptables e reiniciar Docker
# Executa em background para não travar SSH

echo "Iniciando correcao do Docker e iptables..."

# Para o Docker
systemctl stop docker
echo "Docker parado"

# Limpa iptables
iptables -t nat -F 2>/dev/null
iptables -t mangle -F 2>/dev/null
iptables -F 2>/dev/null
iptables -X 2>/dev/null
echo "Iptables limpo"

# Reinicia Docker
systemctl start docker
echo "Docker iniciado"

# Aguarda Docker estabilizar
sleep 10

# Vai para diretorio do projeto
cd /home/administrador/CorujaMonitor

# Sobe containers
docker-compose up -d

echo "Containers iniciados!"
echo ""
echo "Verificando status..."
docker ps
echo ""
echo "Testando API..."
curl http://localhost:8000/health
echo ""
echo "Concluido!"
