#!/bin/bash

echo "========================================"
echo "DIAGNÓSTICO COMPLETO - GIT"
echo "========================================"
echo ""

echo "1. PASTA ATUAL:"
pwd
echo ""

echo "2. STATUS DO GIT:"
git status
echo ""

echo "3. VERIFICAR SE HÁ MODIFICAÇÕES NOS ARQUIVOS PRINCIPAIS:"
echo ""
echo "--- api/routers/sensors.py ---"
git diff api/routers/sensors.py | head -20
echo ""
echo "--- frontend/src/components/Servers.js ---"
git diff frontend/src/components/Servers.js | head -20
echo ""
echo "--- probe/collectors/disk_collector.py ---"
git diff probe/collectors/disk_collector.py | head -20
echo ""

echo "4. VERIFICAR ÚLTIMOS COMMITS:"
git log --oneline -5
echo ""

echo "5. VERIFICAR SE EXISTEM OUTRAS PASTAS CORUJA:"
cd /c/Users/andre.quirino
echo "Pastas com 'Coruja' no nome:"
ls -la | grep -i coruja
echo ""

echo "========================================"
echo "ANÁLISE:"
echo "========================================"
echo ""
echo "Se 'git status' mostrar 'nothing to commit':"
echo "  → As correções JÁ FORAM enviadas para o Git"
echo "  → Vá para o servidor Linux e faça: git pull origin master"
echo ""
echo "Se 'git status' mostrar arquivos modificados:"
echo "  → Execute os comandos do arquivo GIT_COMANDOS_SEPARADOS.txt"
echo ""
echo "Se encontrar outra pasta 'Coruja' (sem Monitor):"
echo "  → As modificações podem estar lá"
echo "  → Entre nessa pasta e execute: git status"
echo ""
