# Script para aplicar override CSS
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APLICANDO OVERRIDE CSS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Reiniciando frontend..." -ForegroundColor Yellow
docker-compose restart frontend 2>&1 | Out-Null

Write-Host "[2/2] Aguardando 15 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "OVERRIDE APLICADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "AGORA:" -ForegroundColor Cyan
Write-Host "1. Pressione Ctrl+Shift+R no navegador" -ForegroundColor White
Write-Host "2. Vá para Servidores" -ForegroundColor White
Write-Host "3. Os cards devem estar alinhados" -ForegroundColor White
Write-Host ""
Write-Host "Se ainda não funcionar, abra aba anônima (Ctrl+Shift+N)" -ForegroundColor Yellow
Write-Host ""
