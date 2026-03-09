#!/bin/bash

echo "========================================="
echo "  CONFIGURAR GIT NO SERVIDOR LINUX"
echo "========================================="
echo ""

cd /home/administrador/CorujaMonitor

# 1. Inicializar repositório Git
echo "[1/5] Inicializando repositório Git..."
git init

# 2. Adicionar remote (substitua pela URL do seu repositório)
echo "[2/5] Adicionando remote origin..."
echo ""
echo "Qual é a URL do seu repositório Git?"
echo "Exemplo: https://github.com/usuario/coruja-monitor.git"
echo "Ou: git@github.com:usuario/coruja-monitor.git"
echo ""
read -p "URL do repositório: " REPO_URL

git remote add origin "$REPO_URL"

# 3. Configurar usuário Git
echo ""
echo "[3/5] Configurando usuário Git..."
read -p "Seu nome: " GIT_NAME
read -p "Seu email: " GIT_EMAIL

git config user.name "$GIT_NAME"
git config user.email "$GIT_EMAIL"

# 4. Fazer fetch do repositório
echo ""
echo "[4/5] Baixando dados do repositório..."
git fetch origin

# 5. Fazer checkout da branch main
echo ""
echo "[5/5] Fazendo checkout da branch main..."
git checkout -b main origin/main

echo ""
echo "========================================="
echo "  ✓ GIT CONFIGURADO COM SUCESSO!"
echo "========================================="
echo ""
echo "Agora você pode usar:"
echo "  git pull origin main    # Baixar atualizações"
echo "  git status              # Ver status"
echo "  git log                 # Ver histórico"
echo ""
