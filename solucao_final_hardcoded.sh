#!/bin/bash

echo "=========================================="
echo "SOLUÇÃO FINAL - IP HARDCODED"
echo "=========================================="

echo "Parando frontend..."
docker compose stop frontend

echo "Removendo container e imagem..."
docker compose rm -f frontend
docker rmi corujamonitor-frontend:latest 2>/dev/null || true

echo "Limpando cache..."
docker builder prune -f

echo "Reconstruindo frontend (2 minutos)..."
docker compose build --no-cache frontend

echo "Iniciando frontend..."
docker compose up -d frontend

echo ""
echo "Aguardando 20 segundos..."
sleep 20

echo ""
echo "=========================================="
echo "PRONTO!"
echo "=========================================="
echo ""
echo "Acesse: http://192.168.31.161:3000"
echo "Email: admin@coruja.com"
echo "Senha: admin123"
echo ""
