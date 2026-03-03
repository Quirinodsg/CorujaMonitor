# Script para rebuild completo do frontend sem cache
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "REBUILD COMPLETO DO FRONTEND" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Parando containers..." -ForegroundColor Yellow
docker-compose stop frontend 2>&1 | Out-Null

Write-Host "[2/5] Removendo container antigo..." -ForegroundColor Yellow
docker-compose rm -f frontend 2>&1 | Out-Null

Write-Host "[3/5] Fazendo rebuild SEM CACHE (pode demorar 2-3 minutos)..." -ForegroundColor Yellow
docker-compose build --no-cache frontend 2>&1 | Out-Null

Write-Host "[4/5] Iniciando frontend..." -ForegroundColor Yellow
docker-compose up -d frontend 2>&1 | Out-Null

Write-Host "[5/5] Aguardando 20 segundos para o frontend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "REBUILD COMPLETO FINALIZADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "AGORA FAÇA:" -ForegroundColor Cyan
Write-Host "1. Abra o navegador em: http://localhost:3000" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+R para limpar cache" -ForegroundColor White
Write-Host "3. Vá para Servidores e verifique os cards de categorias" -ForegroundColor White
Write-Host ""
Write-Host "Os cards devem estar assim:" -ForegroundColor Yellow
Write-Host "  Linha 1: [Sistema] [Docker] [Serviços]" -ForegroundColor White
Write-Host "  Linha 2: [Aplicações] [Rede]" -ForegroundColor White
Write-Host ""
