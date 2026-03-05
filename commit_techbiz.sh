#!/bin/bash

# Script para commit da correção da empresa Techbiz

echo "=========================================="
echo "COMMIT: Correção Empresa Techbiz"
echo "=========================================="
echo ""

# Adicionar arquivos
echo "Adicionando arquivos..."
git add rebuild_frontend_linux.sh
git add CORRIGIR_EMPRESA_TECHBIZ.md
git add COMANDOS_CORRIGIR_TECHBIZ.txt
git add commit_correcao_techbiz.ps1
git add USAR_GITHUB_DESKTOP_TECHBIZ.txt
git add SOLUCAO_TECHBIZ_RESUMO.txt
git add commit_techbiz.sh

# Commit
echo ""
echo "Fazendo commit..."
git commit -m "fix: Adiciona script para rebuild do frontend e corrigir empresa Techbiz fantasma

- Script rebuild_frontend_linux.sh para reconstruir frontend sem cache
- Documentação completa do problema e solução
- Comandos prontos para execução no servidor Linux
- Problema: Frontend em cache mostrando dados antigos
- Solução: Rebuild completo da imagem Docker do frontend"

# Push
echo ""
echo "Enviando para GitHub..."
git push origin master

echo ""
echo "=========================================="
echo "COMMIT CONCLUÍDO!"
echo "=========================================="
echo ""
echo "PRÓXIMOS PASSOS NO SERVIDOR LINUX:"
echo ""
echo "cd ~/CorujaMonitor"
echo "git pull origin master"
echo "chmod +x rebuild_frontend_linux.sh"
echo "./rebuild_frontend_linux.sh"
echo ""
