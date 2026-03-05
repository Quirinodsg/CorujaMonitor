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
git add COMANDOS_GIT_BASH.txt
git add verificar_techbiz_linux.sh
git add excluir_techbiz_direto.sh
git add COMANDOS_EXCLUIR_TECHBIZ_LINUX.txt

# Commit
echo ""
echo "Fazendo commit..."
git commit -m "fix: Adiciona scripts para excluir empresa Techbiz e rebuild do frontend

- Script verificar_techbiz_linux.sh para verificar se empresa existe no banco
- Script excluir_techbiz_direto.sh para excluir empresa diretamente do banco
- Script rebuild_frontend_linux.sh para reconstruir frontend sem cache
- Documentação completa do problema e solução
- Comandos prontos para execução no servidor Linux
- Problema: Empresa Techbiz existe no banco mas dá Network Error ao excluir
- Solução: Excluir diretamente do banco + rebuild do frontend"

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
echo "chmod +x verificar_techbiz_linux.sh"
echo "./verificar_techbiz_linux.sh"
echo "chmod +x excluir_techbiz_direto.sh"
echo "./excluir_techbiz_direto.sh"
echo "chmod +x rebuild_frontend_linux.sh"
echo "./rebuild_frontend_linux.sh"
echo ""
