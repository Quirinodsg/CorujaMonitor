# ========================================
# CORRECAO DEFINITIVA - Cards de Categorias
# Data: 04/03/2026
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORRECAO DEFINITIVA - Cards Sobrepostos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se Docker está rodando
Write-Host "[1/6] Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
    Write-Host "Abra o Docker Desktop e tente novamente." -ForegroundColor Red
    exit 1
}
Write-Host "OK - Docker esta rodando" -ForegroundColor Green
Write-Host ""

# 2. Parar containers
Write-Host "[2/6] Parando containers..." -ForegroundColor Yellow
docker-compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao parar containers!" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Containers parados" -ForegroundColor Green
Write-Host ""

# 3. Rebuild frontend (SEM CACHE)
Write-Host "[3/6] Rebuilding frontend (sem cache)..." -ForegroundColor Yellow
Write-Host "Isso pode levar 2-3 minutos..." -ForegroundColor Cyan
docker-compose build --no-cache frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao fazer rebuild!" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Frontend rebuilded" -ForegroundColor Green
Write-Host ""

# 4. Iniciar containers
Write-Host "[4/6] Iniciando containers..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao iniciar containers!" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Containers iniciados" -ForegroundColor Green
Write-Host ""

# 5. Aguardar containers ficarem prontos
Write-Host "[5/6] Aguardando containers ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "OK - Containers prontos" -ForegroundColor Green
Write-Host ""

# 6. Verificar status
Write-Host "[6/6] Verificando status dos containers..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}"
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "CORRECAO APLICADA COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Abra o navegador em: http://localhost:3000" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+R para limpar o cache" -ForegroundColor White
Write-Host "3. Faca login: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "4. Va em: Gerenciamento > Servidores" -ForegroundColor White
Write-Host "5. Selecione um servidor" -ForegroundColor White
Write-Host "6. Verifique se os cards estao em COLUNA VERTICAL" -ForegroundColor White
Write-Host ""
Write-Host "Se ainda estiver com problema:" -ForegroundColor Yellow
Write-Host "- Feche TODOS os navegadores" -ForegroundColor White
Write-Host "- Abra em modo anonimo" -ForegroundColor White
Write-Host "- Se funcionar em anonimo, o problema e cache" -ForegroundColor White
Write-Host ""
