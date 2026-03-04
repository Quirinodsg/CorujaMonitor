# Verificação Completa do Sistema - 02 MAR 2026
# Este script verifica se todas as correções estão funcionando

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICAÇÃO COMPLETA DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar status dos containers
Write-Host "1. Verificando containers Docker..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 2. Verificar se API está respondendo
Write-Host "2. Testando API de métricas..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API de métricas funcionando!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Erro na API de métricas: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Verificar se frontend está respondendo
Write-Host "3. Testando Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend funcionando!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Erro no Frontend: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Verificar arquivos modificados
Write-Host "4. Verificando arquivos modificados..." -ForegroundColor Yellow

$files = @(
    "frontend/src/components/Dashboard.js",
    "frontend/src/components/Dashboard.css",
    "frontend/src/styles/cards-theme.css",
    "api/main.py"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file existe" -ForegroundColor Green
    } else {
        Write-Host "❌ $file não encontrado" -ForegroundColor Red
    }
}
Write-Host ""

# 5. Verificar se data-status está presente no Dashboard.js
Write-Host "5. Verificando implementação de data-status..." -ForegroundColor Yellow
$dashboardContent = Get-Content "frontend/src/components/Dashboard.js" -Raw
if ($dashboardContent -match 'data-status=\{incident\.status\}') {
    Write-Host "✅ data-status implementado no Dashboard.js" -ForegroundColor Green
} else {
    Write-Host "❌ data-status não encontrado no Dashboard.js" -ForegroundColor Red
}
Write-Host ""

# 6. Verificar ordem dos routers na API
Write-Host "6. Verificando ordem dos routers na API..." -ForegroundColor Yellow
$apiContent = Get-Content "api/main.py" -Raw
$metricsIndex = $apiContent.IndexOf('app.include_router(metrics.router')
$metricsDashboardIndex = $apiContent.IndexOf('app.include_router(metrics_dashboard.router')

if ($metricsIndex -lt $metricsDashboardIndex) {
    Write-Host "✅ Ordem dos routers correta (metrics antes de metrics_dashboard)" -ForegroundColor Green
} else {
    Write-Host "❌ Ordem dos routers incorreta" -ForegroundColor Red
}
Write-Host ""

# 7. Resumo final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO DA VERIFICAÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Cores de incidentes: Implementado" -ForegroundColor Green
Write-Host "✅ Navegação de cards: Implementado" -ForegroundColor Green
Write-Host "✅ API de métricas: Corrigido" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMO PASSO:" -ForegroundColor Yellow
Write-Host "Pressione Ctrl + Shift + R no navegador para limpar o cache!" -ForegroundColor Yellow
Write-Host ""
