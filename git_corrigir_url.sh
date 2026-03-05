#!/bin/bash

echo "Enviando correção de URL duplicada para o Git..."

git add frontend/src/config.js
git add corrigir_url_duplicada.sh
git add git_corrigir_url.sh

git commit -m "fix: Corrigir URL duplicada (/api/v1/api/v1)

- Remover /api/v1 do config.js (componentes já adicionam)
- Atualizar CACHE_VERSION para v7.0
- Script para rebuild do frontend"

git push origin master

echo ""
echo "✓ Arquivos enviados!"
echo ""
echo "Agora execute no servidor Linux:"
echo "  cd ~/CorujaMonitor"
echo "  git pull origin master"
echo "  chmod +x corrigir_url_duplicada.sh"
echo "  ./corrigir_url_duplicada.sh"
echo ""
