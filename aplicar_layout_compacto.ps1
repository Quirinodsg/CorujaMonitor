# ========================================
# LAYOUT COMPACTO - Cards de Categorias
# Data: 04/03/2026
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APLICANDO LAYOUT COMPACTO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Parar containers
Write-Host "[1/4] Parando containers..." -ForegroundColor Yellow
docker-compose down
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# 2. Rebuild frontend
Write-Host "[2/4] Rebuilding frontend..." -ForegroundColor Yellow
docker-compose build --no-cache frontend
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# 3. Iniciar containers
Write-Host "[3/4] Iniciando containers..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# 4. Aguardar
Write-Host "[4/4] Aguardando containers..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "LAYOUT COMPACTO APLICADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "AGORA:" -ForegroundColor Cyan
Write-Host "1. Limpe o cache: Ctrl+Shift+R" -ForegroundColor White
Write-Host "2. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "3. Clique no icone da categoria para expandir" -ForegroundColor White
Write-Host "4. Sensores aparecem DENTRO do card" -ForegroundColor White
Write-Host ""
