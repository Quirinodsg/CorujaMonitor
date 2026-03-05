#!/bin/bash

echo "=========================================="
echo "ADICIONANDO ARQUIVOS NOVOS AO GIT"
echo "=========================================="

echo ""
echo "Adicionando arquivos de diagnóstico..."
git add DIAGNOSTICAR_ERROS_AGORA.txt
git add EXECUTAR_NO_LINUX_AGORA.txt
git add diagnostico_erros_paginas.sh
git add testar_endpoints_autenticado.sh
git add git_add_novos_arquivos.sh

echo ""
echo "Fazendo commit..."
git commit -m "feat: Scripts de diagnóstico de erros nas páginas

- Script para diagnosticar erros em endpoints
- Script para testar endpoints com autenticação
- Guias de execução no Linux"

echo ""
echo "Enviando para o GitHub..."
git push origin master

echo ""
echo "=========================================="
echo "✓ ARQUIVOS ENVIADOS!"
echo "=========================================="
echo ""
