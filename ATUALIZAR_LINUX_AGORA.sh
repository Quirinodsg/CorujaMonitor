#!/bin/bash
# ========================================
# ATUALIZAR SERVIDOR LINUX
# ========================================

echo "=========================================="
echo "CONECTANDO NO SERVIDOR LINUX"
echo "=========================================="
echo ""
echo "IP: 192.168.31.161"
echo "Usuário: root ou administrador"
echo ""
echo "Após conectar, execute:"
echo ""
echo "cd /home/administrador/CorujaMonitor && \\"
echo "git fetch origin && \\"
echo "git checkout master && \\"
echo "git pull origin master && \\"
echo "docker-compose restart"
echo ""
echo "=========================================="
echo "CONECTANDO..."
echo "=========================================="
echo ""

# Conectar via SSH
ssh root@192.168.31.161
