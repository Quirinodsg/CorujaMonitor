#!/bin/bash

echo "========================================="
echo "  SETUP GIT - CORUJA MONITOR"
echo "  Repositório Público - Sem Senha"
echo "========================================="
echo ""

cd /home/administrador/CorujaMonitor

echo "[1/6] Inicializando Git..."
git init

echo ""
echo "[2/6] Adicionando remote..."
git remote add origin https://github.com/Quirinodsg/CorujaMonitor.git

echo ""
echo "[3/6] Configurando usuário..."
git config user.name "Quirinodsg"
git config user.email "quirinodsg@github.com"

echo ""
echo "[4/6] Baixando dados do repositório..."
git fetch origin

echo ""
echo "[5/6] Fazendo checkout da branch main..."
git checkout -b main origin/main

echo ""
echo "[6/6] Verificando status..."
git status

echo ""
echo "========================================="
echo "  ✓ GIT CONFIGURADO COM SUCESSO!"
echo "========================================="
echo ""
echo "Comandos úteis:"
echo "  git pull origin main    # Baixar atualizações"
echo "  git status              # Ver status"
echo "  git log --oneline -5    # Ver últimos commits"
echo ""
echo "Próximos passos:"
echo "  1. python api/reset_sistema.py"
echo "  2. docker-compose restart"
echo ""
