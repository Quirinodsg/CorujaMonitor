#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           REBUILD DEFINITIVO - LIMPAR TUDO                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "1. Parando TODOS os containers..."
docker compose down

echo ""
echo "2. Removendo TODAS as imagens do Coruja..."
docker rmi corujamonitor-frontend:latest 2>/dev/null || true
docker rmi coruja-frontend:latest 2>/dev/null || true
docker rmi $(docker images | grep coruja | awk '{print $3}') 2>/dev/null || true

echo ""
echo "3. Limpando TODO o cache do Docker..."
docker builder prune -af
docker system prune -af

echo ""
echo "4. Verificando código do config.js..."
echo "   Última versão do CACHE_VERSION:"
grep "CACHE_VERSION" frontend/src/config.js

echo ""
echo "5. Reconstruindo TUDO do zero (vai demorar 3-5 minutos)..."
docker compose build --no-cache

echo ""
echo "6. Iniciando containers..."
docker compose up -d

echo ""
echo "7. Aguardando containers iniciarem (30 segundos)..."
sleep 30

echo ""
echo "8. Verificando status..."
docker compose ps

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    REBUILD CONCLUÍDO!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "IMPORTANTE:"
echo "  1. Feche TODAS as abas do navegador"
echo "  2. Limpe o cache do navegador (Ctrl+Shift+Del)"
echo "  3. Abra aba ANÔNIMA (Ctrl+Shift+N)"
echo "  4. Acesse: http://192.168.31.161:3000"
echo ""
echo "Credenciais:"
echo "  Email: admin@coruja.com"
echo "  Senha: admin123"
echo ""
echo "No Console do Navegador (F12) deve aparecer:"
echo "  ✓ CORRETO: http://192.168.31.161:8000/api/v1/auth/login"
echo "  ✗ ERRADO:  http://localhost:8000/api/v1/auth/login"
echo ""
