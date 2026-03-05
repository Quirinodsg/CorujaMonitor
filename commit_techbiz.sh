#!/bin/bash

# Script para commit da correção da empresa Techbiz

echo "=========================================="
echo "COMMIT: Correção Empresa Techbiz"
echo "=========================================="
echo ""

# Adicionar arquivos
echo "Adicionando arquivos..."
git add rebuild_frontend_linux.sh
git add rebuild_frontend_completo_linux.sh
git add verificar_empresas_banco.sh
git add CORRIGIR_EMPRESA_TECHBIZ.md
git add COMANDOS_CORRIGIR_TECHBIZ.txt
git add commit_correcao_techbiz.ps1
git add USAR_GITHUB_DESKTOP_TECHBIZ.txt
git add SOLUCAO_TECHBIZ_RESUMO.txt
git add SOLUCAO_FINAL_TECHBIZ.txt
git add SOLUCAO_IMEDIATA_TECHBIZ.txt
git add SOLUCAO_DEFINITIVA_CACHE.txt
git add SOLUCAO_FINAL_REBUILD.txt
git add LIMPAR_CACHE_AGRESSIVO.txt
git add RESUMO_FINAL_PROBLEMA_TECHBIZ.md
git add COMANDOS_FINAIS_TECHBIZ.txt
git add commit_techbiz.sh
git add COMANDOS_GIT_BASH.txt
git add verificar_techbiz_linux.sh
git add excluir_techbiz_direto.sh
git add COMANDOS_EXCLUIR_TECHBIZ_LINUX.txt

# Commit
echo ""
echo "Fazendo commit..."
git commit -m "fix: Corrige problema de CORS com localhost hardcoded no frontend

- Problema: Frontend usando localhost ao invés do IP do servidor
- Erro CORS ao tentar excluir empresa Techbiz
- Script rebuild_frontend_completo_linux.sh para limpeza total
- Script rebuild_frontend_linux.sh para rebuild rápido
- Script verificar_techbiz_linux.sh para verificar banco
- Script excluir_techbiz_direto.sh para excluir do banco
- Documentação completa da solução
- Causa: Cache do navegador + imagem Docker não reconstruída
- Solução: Rebuild completo + limpar cache do navegador"

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
echo "chmod +x rebuild_frontend_completo_linux.sh"
echo "./rebuild_frontend_completo_linux.sh"
echo ""
echo "DEPOIS NO NAVEGADOR:"
echo "1. Abra em ABA ANÔNIMA: Ctrl+Shift+N"
echo "2. Acesse: http://192.168.31.161:3000"
echo "3. Verifique no Console (F12) se mostra IP correto"
echo ""
