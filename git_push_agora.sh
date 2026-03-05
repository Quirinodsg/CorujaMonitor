#!/bin/bash

echo "=========================================="
echo "ENVIANDO ARQUIVOS PARA O GIT"
echo "=========================================="

echo ""
echo "Adicionando arquivos..."
git add corrigir_tabelas_banco.sh
git add EXECUTAR_AGORA_CORRIGIR_ERROS.txt
git add diagnostico_login_completo.sh
git add corrigir_login_definitivo.sh
git add commit_correcao_erros_paginas.sh
git add COMANDOS_GIT_CORRECAO_ERROS.txt
git add enviar_correcao_erros.ps1
git add ENVIAR_ARQUIVOS_GIT_AGORA.txt
git add COPIAR_E_COLAR_NO_LINUX.txt
git add GIT_COMANDOS_AGORA.txt
git add git_push_agora.sh

echo ""
echo "Fazendo commit..."
git commit -m "fix: Corrigir erros nas páginas (Empresas, Incidentes, Relatórios, KB, IA)

- Script para criar todas as tabelas necessárias no banco
- Popular Knowledge Base com dados iniciais
- Diagnóstico completo de login
- Correção definitiva de login com senha correta
- Scripts para Git Bash e GitHub Desktop"

echo ""
echo "Enviando para o GitHub..."
git push origin master

echo ""
echo "=========================================="
echo "✓ CONCLUÍDO!"
echo "=========================================="
echo ""
echo "Agora execute no servidor Linux:"
echo ""
echo "  cd ~/CorujaMonitor"
echo "  git pull origin master"
echo "  chmod +x corrigir_tabelas_banco.sh"
echo "  ./corrigir_tabelas_banco.sh"
echo ""
echo "Ou use o método rápido:"
echo "  Copie o conteúdo de COPIAR_E_COLAR_NO_LINUX.txt"
echo "  Cole no terminal Linux"
echo ""
