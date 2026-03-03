# Script para aplicar ajuste automático de fonte nos sensores
# Data: 03/03/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AJUSTE AUTOMÁTICO DE FONTE - SENSORES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Reiniciando frontend..." -ForegroundColor Yellow
docker-compose restart frontend 2>&1 | Out-Null

Write-Host "[2/2] Aguardando 15 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "AJUSTE APLICADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "O QUE FOI FEITO:" -ForegroundColor Cyan
Write-Host "- Fonte ajusta automaticamente baseado no tamanho do nome" -ForegroundColor White
Write-Host "- Nomes curtos (<30 chars): 12px" -ForegroundColor White
Write-Host "- Nomes médios (30-50 chars): 11px" -ForegroundColor White
Write-Host "- Nomes longos (50-70 chars): 10px" -ForegroundColor White
Write-Host "- Nomes muito longos (>70 chars): 9px" -ForegroundColor White
Write-Host "- Sensores Docker: sempre 10px" -ForegroundColor White
Write-Host ""
Write-Host "AGORA:" -ForegroundColor Yellow
Write-Host "1. Pressione Ctrl+Shift+R no navegador" -ForegroundColor White
Write-Host "2. Vá para Servidores > Docker" -ForegroundColor White
Write-Host "3. Os nomes devem estar legíveis sem sobrepor" -ForegroundColor White
Write-Host ""
