#!/usr/bin/env pwsh
# Script para testar a correção das métricas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DA CORREÇÃO DAS MÉTRICAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se API está rodando
Write-Host "1. Verificando se API está rodando..." -ForegroundColor Yellow
$apiStatus = docker-compose ps api 2>&1 | Select-String "Up"
if ($apiStatus) {
    Write-Host "   ✅ API está rodando" -ForegroundColor Green
} else {
    Write-Host "   ❌ API não está rodando" -ForegroundColor Red
    Write-Host "   Execute: docker-compose restart api" -ForegroundColor Yellow
    exit 1
}

# 2. Testar endpoint de métricas
Write-Host ""
Write-Host "2. Testando endpoint de métricas..." -ForegroundColor Yellow
$response = curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h 2>&1
Write-Host "   Status HTTP: $response" -ForegroundColor Cyan

if ($response -eq "401") {
    Write-Host "   ✅ Endpoint encontrado (401 = precisa autenticação)" -ForegroundColor Green
} elseif ($response -eq "200") {
    Write-Host "   ✅ Endpoint funcionando perfeitamente!" -ForegroundColor Green
} elseif ($response -eq "404") {
    Write-Host "   ❌ Endpoint não encontrado (404)" -ForegroundColor Red
    Write-Host "   A API precisa ser reiniciada!" -ForegroundColor Yellow
} else {
    Write-Host "   ⚠️  Status inesperado: $response" -ForegroundColor Yellow
}

# 3. Verificar ordem dos routers no código
Write-Host ""
Write-Host "3. Verificando ordem dos routers..." -ForegroundColor Yellow
$mainPy = Get-Content api/main.py | Select-String "metrics"
$metricsLine = ($mainPy | Select-String "metrics\.router" | Select-Object -First 1).LineNumber
$dashboardLine = ($mainPy | Select-String "metrics_dashboard\.router" | Select-Object -First 1).LineNumber

if ($dashboardLine -lt $metricsLine) {
    Write-Host "   ✅ Ordem correta: metrics_dashboard ANTES de metrics" -ForegroundColor Green
} else {
    Write-Host "   ❌ Ordem incorreta: metrics ANTES de metrics_dashboard" -ForegroundColor Red
}

# 4. Instruções finais
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Abra o navegador" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+R para limpar o cache" -ForegroundColor Yellow
Write-Host "3. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "4. Clique no botão 'Métricas (Grafana)'" -ForegroundColor White
Write-Host "5. Verifique se os dados carregam corretamente" -ForegroundColor White
Write-Host ""
Write-Host "Se ainda aparecer erro 404:" -ForegroundColor Yellow
Write-Host "  - Reconstrua o frontend: docker-compose build --no-cache frontend" -ForegroundColor Cyan
Write-Host "  - Reinicie tudo: docker-compose restart" -ForegroundColor Cyan
Write-Host ""
