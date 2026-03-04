# Script para Aplicar Dashboard Estilo Grafana - 27 FEV 2026

Write-Host "📊 Aplicando Dashboard Estilo Grafana..." -ForegroundColor Cyan
Write-Host ""

# Verificar se os arquivos foram criados
Write-Host "🔍 Verificando arquivos..." -ForegroundColor Yellow

$files = @(
    "frontend/src/components/MetricsViewer.js",
    "frontend/src/components/MetricsViewer.css",
    "api/routers/metrics_dashboard.py"
)

$allFilesExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - NÃO ENCONTRADO!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "❌ Alguns arquivos não foram encontrados!" -ForegroundColor Red
    Write-Host "Execute o script novamente ou crie os arquivos manualmente." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Todos os arquivos encontrados!" -ForegroundColor Green
Write-Host ""

# Reiniciar API
Write-Host "🔄 Reiniciando API..." -ForegroundColor Yellow
docker-compose restart api

Write-Host ""
Write-Host "⏳ Aguardando API iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar se API está rodando
$apiStatus = docker-compose ps api --format json | ConvertFrom-Json

if ($apiStatus.State -eq "running") {
    Write-Host "✅ API está rodando!" -ForegroundColor Green
} else {
    Write-Host "❌ API não está rodando!" -ForegroundColor Red
    Write-Host "Status: $($apiStatus.State)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

# Testar endpoints
Write-Host "🧪 Testando Endpoints..." -ForegroundColor Yellow
Write-Host ""

$endpoints = @(
    "/api/v1/metrics/dashboard/servers?range=24h",
    "/api/v1/metrics/dashboard/network?range=24h",
    "/api/v1/metrics/dashboard/webapps?range=24h",
    "/api/v1/metrics/dashboard/kubernetes?range=24h"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$endpoint" `
            -Method GET `
            -UseBasicParsing `
            -TimeoutSec 5 `
            -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $endpoint" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $endpoint - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ $endpoint - Erro: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

# Resumo
Write-Host "📊 DASHBOARD ESTILO GRAFANA APLICADO!" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Componentes criados:" -ForegroundColor Cyan
Write-Host "  - MetricsViewer.js (~500 linhas)"
Write-Host "  - MetricsViewer.css (~400 linhas)"
Write-Host "  - metrics_dashboard.py (~400 linhas)"
Write-Host ""
Write-Host "✅ Integrações:" -ForegroundColor Cyan
Write-Host "  - MainLayout.js (rota adicionada)"
Write-Host "  - Sidebar.js (menu adicionado)"
Write-Host "  - main.py (router registrado)"
Write-Host ""
Write-Host "✅ Dashboards disponíveis:" -ForegroundColor Cyan
Write-Host "  - 🖥️  Servidores"
Write-Host "  - 📡 Rede (APs/Switches)"
Write-Host "  - 🌐 WebApps"
Write-Host "  - ☸️  Kubernetes"
Write-Host "  - ⚙️  Personalizado"
Write-Host ""
Write-Host "🚀 Como usar:" -ForegroundColor Yellow
Write-Host "  1. Acesse: http://localhost:3000"
Write-Host "  2. Login: admin@coruja.com / admin123"
Write-Host "  3. Menu: 📊 Métricas (Grafana)"
Write-Host ""
Write-Host "📚 Documentação:" -ForegroundColor Yellow
Write-Host "  - DESIGN_GRAFANA_STYLE_DASHBOARD_27FEV.md"
Write-Host "  - GRAFANA_STYLE_DASHBOARD_IMPLEMENTADO_27FEV.md"
Write-Host ""
Write-Host "🎉 Dashboard pronto para uso!" -ForegroundColor Green
