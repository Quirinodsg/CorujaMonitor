#!/bin/bash

cd "/c/Users/andre.quirino/Coruja Monitor"

git add frontend/src/config.js
git add LIMPAR_CACHE_COMPLETO_AGORA.txt
git add TESTAR_SISTEMA_AGORA.txt
git add RESOLVER_GIT_CONFLICT_AGORA.txt

git commit -m "fix: Aumentar versão cache para v8.0 - forçar reload completo"

git push origin master

echo ""
echo "✓ Enviado para o Git!"
echo ""
echo "Execute no Linux:"
echo "cd /home/administrador/CorujaMonitor"
echo "git pull origin master"
echo "./rebuild_frontend_limpo.sh"
