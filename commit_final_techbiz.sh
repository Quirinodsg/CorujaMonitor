#!/bin/bash

echo "=========================================="
echo "COMMIT FINAL: Correção Techbiz + Scripts"
echo "=========================================="
echo ""

# Adicionar TODOS os arquivos novos
echo "Adicionando arquivos..."
git add frontend/src/config.js
git add rebuild_frontend_linux.sh
git add rebuild_frontend_completo_linux.sh
git add verificar_empresas_banco.sh
git add verificar_techbiz_linux.sh
git add excluir_techbiz_direto.sh
git add commit_techbiz.sh
git add commit_final_techbiz.sh
git add CORRIGIR_EMPRESA_TECHBIZ.md
git add COMANDOS_CORRIGIR_TECHBIZ.txt
git add COMANDOS_EXCLUIR_TECHBIZ_LINUX.txt
git add COMANDOS_FINAIS_TECHBIZ.txt
git add COMANDOS_GIT_BASH.txt
git add SOLUCAO_TECHBIZ_RESUMO.txt
git add SOLUCAO_FINAL_TECHBIZ.txt
git add SOLUCAO_IMEDIATA_TECHBIZ.txt
git add SOLUCAO_DEFINITIVA_CACHE.txt
git add SOLUCAO_FINAL_REBUILD.txt
git add LIMPAR_CACHE_AGRESSIVO.txt
git add RESUMO_FINAL_PROBLEMA_TECHBIZ.md
git add USAR_GITHUB_DESKTOP_TECHBIZ.txt

# Commit
echo ""
echo "Fazendo commit..."
git commit -m "fix: Correção completa do problema Techbiz + aumento CACHE_VERSION

- Aumentado CACHE_VERSION para v4.0-REBUILD para forçar atualização
- Scripts de rebuild do frontend (completo e rápido)
- Scripts de verificação e exclusão de empresas no banco
- Documentação completa do problema e soluções
- Problema: Imagem Docker do frontend com código antigo
- Solução: Rebuild completo + cache busting no config.js"

# Push
echo ""
echo "Enviando para GitHub..."
git push origin master

echo ""
echo "=========================================="
echo "COMMIT CONCLUÍDO!"
echo "=========================================="
echo ""
echo "NO SERVIDOR LINUX, execute:"
echo ""
echo "cd ~/CorujaMonitor"
echo "git pull origin master"
echo "chmod +x rebuild_frontend_completo_linux.sh"
echo "./rebuild_frontend_completo_linux.sh"
echo ""
