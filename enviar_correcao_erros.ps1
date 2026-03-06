#!/usr/bin/env pwsh

Write-Host "=========================================="
Write-Host "ENVIANDO CORREÇÃO DE ERROS PARA O GIT"
Write-Host "=========================================="
Write-Host ""

# 1. Adicionar arquivos
Write-Host "1. Adicionando arquivos..."
git add corrigir_tabelas_banco.sh
git add diagnostico_erros_paginas.sh
git add rebuild_frontend_limpo.sh
git add EXECUTAR_NO_LINUX_AGORA.txt
git add RESOLVER_ERRO_DOCKER_BUILD.txt
git add frontend/src/config.js

# 2. Commit
Write-Host ""
Write-Host "2. Criando commit..."
git commit -m "fix: Corrigir erros nas páginas + resolver erro Docker build

- Corrigido API_URL duplicado em config.js (era /api/v1/api/v1)
- Adicionado script para criar tabelas faltantes no banco
- Adicionado script de rebuild com limpeza de cache Docker
- Adicionado script de diagnóstico de erros
- Instruções para resolver erro de build do Docker

Problema 1: Páginas davam erro 404 devido a URL duplicada
Solução 1: Remover /api/v1 duplicado do config.js

Problema 2: Docker build falha com 'parent snapshot does not exist'
Solução 2: Limpar cache do Docker BuildKit antes do rebuild
"

# 3. Push
Write-Host ""
Write-Host "3. Enviando para GitHub..."
git push origin master

Write-Host ""
Write-Host "=========================================="
Write-Host "✓ ARQUIVOS ENVIADOS COM SUCESSO!"
Write-Host "=========================================="
Write-Host ""
Write-Host "PRÓXIMO PASSO:"
Write-Host "→ Abra o arquivo: RESOLVER_ERRO_DOCKER_BUILD.txt"
Write-Host "→ Copie os comandos e cole no terminal Linux"
Write-Host "→ Isso vai limpar o cache do Docker e reconstruir"
Write-Host ""
