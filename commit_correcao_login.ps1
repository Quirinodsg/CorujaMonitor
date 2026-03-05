# Script para fazer commit da correção do Login

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMMIT - Correção Login Servidor Linux" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Erro: Execute este script no diretório do projeto" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Diretório correto" -ForegroundColor Green
Write-Host ""

# Verificar status
Write-Host "📋 Status do Git:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Adicionar arquivos
Write-Host "➕ Adicionando arquivos..." -ForegroundColor Yellow
git add frontend/src/components/Login.js
git add PASSO_A_PASSO_LOGIN_LINUX.md
git add CORRIGIR_AGORA.txt
git add corrigir_login_manual.sh
git add corrigir_login_linux.sh
git add ATUALIZAR_SERVIDOR_LINUX_GIT.md
git add commit_correcao_login.ps1

Write-Host "✅ Arquivos adicionados" -ForegroundColor Green
Write-Host ""

# Fazer commit
Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow
git commit -m "fix: Corrigir URL da API no Login.js para funcionar em rede

- Substituir localhost:8000 por detecção dinâmica do IP
- Usar window.location.origin para pegar IP atual
- Adicionar scripts de correção para servidor Linux
- Documentação completa do processo

Problema: Frontend usava URL hardcoded http://localhost:8000
Solução: Detectar dinamicamente o IP usando window.location.origin

Arquivos modificados:
- frontend/src/components/Login.js (linha 74-75)
- Scripts de correção para Linux
- Documentação completa"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit realizado com sucesso" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao fazer commit" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Fazer push
Write-Host "🚀 Fazendo push para o repositório..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Fazendo push para 'master'..." -ForegroundColor Cyan
git push origin master

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tente manualmente:" -ForegroundColor Yellow
    Write-Host "  git push origin master" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ COMMIT E PUSH CONCLUÍDOS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "NO SERVIDOR LINUX (192.168.31.161):" -ForegroundColor Yellow
Write-Host "  cd ~/CorujaMonitor" -ForegroundColor White
Write-Host "  docker compose down" -ForegroundColor White
Write-Host "  git pull origin master" -ForegroundColor White
Write-Host "  docker compose build --no-cache" -ForegroundColor White
Write-Host "  docker compose up -d" -ForegroundColor White
Write-Host "  sleep 30" -ForegroundColor White
Write-Host ""
Write-Host "Depois teste no navegador:" -ForegroundColor Yellow
Write-Host "  http://192.168.31.161:3000" -ForegroundColor White
Write-Host ""
