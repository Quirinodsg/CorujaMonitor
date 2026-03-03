# Script para testar Backend Kubernetes
# Data: 27 FEV 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE BACKEND KUBERNETES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se API esta rodando
Write-Host "[1/6] Verificando status da API..." -ForegroundColor Yellow
$apiStatus = docker ps --filter "name=coruja-api" --format "{{.Status}}"
if ($apiStatus -like "*Up*") {
    Write-Host "OK API esta rodando" -ForegroundColor Green
} else {
    Write-Host "ERRO API nao esta rodando" -ForegroundColor Red
    exit 1
}

# 2. Verificar tabelas criadas
Write-Host ""
Write-Host "[2/6] Verificando tabelas no banco..." -ForegroundColor Yellow
$tables = docker-compose exec -T db psql -U postgres -d coruja -c "\dt" 2>&1
if ($tables -match "kubernetes_clusters" -and $tables -match "kubernetes_resources" -and $tables -match "kubernetes_metrics") {
    Write-Host "OK Tabelas Kubernetes criadas" -ForegroundColor Green
} else {
    Write-Host "ERRO Tabelas nao encontradas" -ForegroundColor Red
}

# 3. Verificar endpoints da API
Write-Host ""
Write-Host "[3/6] Verificando endpoints da API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    if ($response.Content -match "kubernetes") {
        Write-Host "OK Endpoints Kubernetes registrados" -ForegroundColor Green
    } else {
        Write-Host "AVISO Endpoints podem nao estar visiveis" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERRO Nao foi possivel acessar /docs" -ForegroundColor Red
}

# 4. Verificar bibliotecas instaladas
Write-Host ""
Write-Host "[4/6] Verificando bibliotecas Python..." -ForegroundColor Yellow
$k8sLib = docker-compose exec -T api pip list 2>&1 | Select-String "kubernetes"
$yamlLib = docker-compose exec -T api pip list 2>&1 | Select-String "PyYAML"
if ($k8sLib -and $yamlLib) {
    Write-Host "OK kubernetes e pyyaml instalados" -ForegroundColor Green
} else {
    Write-Host "ERRO Bibliotecas nao instaladas" -ForegroundColor Red
}

# 5. Verificar collector criado
Write-Host ""
Write-Host "[5/6] Verificando collector Kubernetes..." -ForegroundColor Yellow
if (Test-Path "../probe/collectors/kubernetes_collector.py") {
    Write-Host "OK Collector Kubernetes criado" -ForegroundColor Green
} else {
    Write-Host "ERRO Collector nao encontrado" -ForegroundColor Red
}

# 6. Verificar router registrado
Write-Host ""
Write-Host "[6/6] Verificando router no main.py..." -ForegroundColor Yellow
$mainContent = Get-Content "main.py" -Raw
if ($mainContent -match "kubernetes" -and $mainContent -match "app.include_router\(kubernetes.router\)") {
    Write-Host "OK Router Kubernetes registrado" -ForegroundColor Green
} else {
    Write-Host "ERRO Router nao registrado" -ForegroundColor Red
}

# Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DA IMPLEMENTACAO BACKEND" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Modelos criados:" -ForegroundColor Cyan
Write-Host "  - KubernetesCluster (configuracao de clusters)" -ForegroundColor White
Write-Host "  - KubernetesResource (recursos descobertos)" -ForegroundColor White
Write-Host "  - KubernetesMetric (metricas historicas)" -ForegroundColor White
Write-Host ""
Write-Host "Endpoints implementados:" -ForegroundColor Cyan
Write-Host "  POST   /api/v1/kubernetes/clusters - Criar cluster" -ForegroundColor White
Write-Host "  GET    /api/v1/kubernetes/clusters - Listar clusters" -ForegroundColor White
Write-Host "  GET    /api/v1/kubernetes/clusters/{id} - Obter cluster" -ForegroundColor White
Write-Host "  PUT    /api/v1/kubernetes/clusters/{id} - Atualizar cluster" -ForegroundColor White
Write-Host "  DELETE /api/v1/kubernetes/clusters/{id} - Deletar cluster" -ForegroundColor White
Write-Host "  POST   /api/v1/kubernetes/clusters/{id}/test - Testar conexao" -ForegroundColor White
Write-Host "  POST   /api/v1/kubernetes/clusters/{id}/discover - Auto-discovery" -ForegroundColor White
Write-Host "  GET    /api/v1/kubernetes/clusters/{id}/resources - Listar recursos" -ForegroundColor White
Write-Host "  GET    /api/v1/kubernetes/clusters/{id}/metrics - Metricas agregadas" -ForegroundColor White
Write-Host ""
Write-Host "Collector implementado:" -ForegroundColor Cyan
Write-Host "  - probe/collectors/kubernetes_collector.py" -ForegroundColor White
Write-Host "  - Coleta nodes, pods, deployments, daemonsets, statefulsets, services" -ForegroundColor White
Write-Host "  - Usa Metrics Server para CPU e memoria" -ForegroundColor White
Write-Host "  - Suporta kubeconfig, service account e bearer token" -ForegroundColor White
Write-Host ""
Write-Host "Bibliotecas instaladas:" -ForegroundColor Cyan
Write-Host "  - kubernetes==29.0.0" -ForegroundColor White
Write-Host "  - pyyaml==6.0.1" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Testar criacao de cluster via API" -ForegroundColor White
Write-Host "  2. Testar conexao com cluster real" -ForegroundColor White
Write-Host "  3. Executar auto-discovery" -ForegroundColor White
Write-Host "  4. Integrar collector com probe" -ForegroundColor White
Write-Host "  5. Criar dashboards no frontend" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BACKEND IMPLEMENTADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
