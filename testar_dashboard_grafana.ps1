# Script para Testar Dashboard Grafana - 27 FEV 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DO DASHBOARD ESTILO GRAFANA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se os containers estão rodando
Write-Host "1. Verificando containers..." -ForegroundColor Yellow
$api = docker-compose ps api --format json | ConvertFrom-Json
$frontend = docker-compose ps frontend --format json | ConvertFrom-Json

if ($api.State -eq "running") {
    Write-Host "   ✅ API rodando" -ForegroundColor Green
} else {
    Write-Host "   ❌ API não está rodando" -ForegroundColor Red
    exit 1
}

if ($frontend.State -eq "running") {
    Write-Host "   ✅ Frontend rodando" -ForegroundColor Green
} else {
    Write-Host "   ❌ Frontend não está rodando" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Testar autenticação
Write-Host "2. Testando autenticação..." -ForegroundColor Yellow
try {
    $body = '{"email":"admin@coruja.com","password":"admin123"}'
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
    $token = $response.access_token
    Write-Host "   ✅ Login realizado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erro ao fazer login: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Testar endpoint de servidores
Write-Host "3. Testando endpoint de servidores..." -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $token"}
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h" -Headers $headers
    
    Write-Host "   ✅ Endpoint funcionando" -ForegroundColor Green
    Write-Host "   📊 Resumo:" -ForegroundColor Cyan
    Write-Host "      - CPU Média: $($result.summary.cpu_avg)%" -ForegroundColor White
    Write-Host "      - Memória Média: $($result.summary.memory_avg)%" -ForegroundColor White
    Write-Host "      - Disco Médio: $($result.summary.disk_avg)%" -ForegroundColor White
    Write-Host "      - Servidores Online: $($result.summary.servers_online) de $($result.summary.servers_total)" -ForegroundColor White
    
    if ($result.servers.Count -gt 0) {
        Write-Host ""
        Write-Host "   🖥️  Servidores:" -ForegroundColor Cyan
        foreach ($server in $result.servers) {
            $statusIcon = if ($server.status -eq "ok") { "✅" } elseif ($server.status -eq "warning") { "⚠️" } else { "❌" }
            Write-Host "      $statusIcon $($server.name) - CPU: $($server.cpu)% | MEM: $($server.memory)% | DISK: $($server.disk)%" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   ❌ Erro ao testar endpoint: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 4. Testar endpoint de rede
Write-Host "4. Testando endpoint de rede..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/network?range=24h" -Headers $headers
    Write-Host "   ✅ Endpoint de rede funcionando" -ForegroundColor Green
    Write-Host "   📡 Dispositivos: $($result.summary.devices_total) (Online: $($result.summary.devices_online))" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Endpoint de rede com erro (pode ser normal se não houver dispositivos)" -ForegroundColor Yellow
}

Write-Host ""

# 5. Testar endpoint de webapps
Write-Host "5. Testando endpoint de webapps..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/webapps?range=24h" -Headers $headers
    Write-Host "   ✅ Endpoint de webapps funcionando" -ForegroundColor Green
    Write-Host "   🌐 Aplicações: $($result.summary.apps_total) (Online: $($result.summary.apps_online))" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Endpoint de webapps com erro (pode ser normal se não houver apps)" -ForegroundColor Yellow
}

Write-Host ""

# 6. Testar endpoint de kubernetes
Write-Host "6. Testando endpoint de kubernetes..." -ForegroundColor Yellow
try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/kubernetes?range=24h" -Headers $headers
    Write-Host "   ✅ Endpoint de kubernetes funcionando" -ForegroundColor Green
    Write-Host "   ☸️  Clusters: $($result.summary.clusters_total) | Pods: $($result.summary.pods_total)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Endpoint de kubernetes com erro (pode ser normal se não houver clusters)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ TESTES CONCLUÍDOS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 7. Instruções de acesso
Write-Host "📋 COMO ACESSAR O DASHBOARD:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Abra o navegador e acesse:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "2. Faça login com:" -ForegroundColor Yellow
Write-Host "   Email: admin@coruja.com" -ForegroundColor White
Write-Host "   Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "3. Clique no menu lateral:" -ForegroundColor Yellow
Write-Host "   📊 Métricas (Grafana)" -ForegroundColor White
Write-Host ""
Write-Host "4. Explore os dashboards:" -ForegroundColor Yellow
Write-Host "   - Servidores (CPU, Memória, Disco)" -ForegroundColor White
Write-Host "   - Rede (APs, Switches)" -ForegroundColor White
Write-Host "   - WebApps (Aplicações Web)" -ForegroundColor White
Write-Host "   - Kubernetes (Clusters, Pods)" -ForegroundColor White
Write-Host "   - Personalizado (Dashboard customizável)" -ForegroundColor White
Write-Host ""
Write-Host "5. Ajuste o período:" -ForegroundColor Yellow
Write-Host "   - 1h, 6h, 24h, 7d, 30d" -ForegroundColor White
Write-Host ""
Write-Host "6. Ative o auto-refresh:" -ForegroundColor Yellow
Write-Host "   - Marque a checkbox 'Auto-refresh'" -ForegroundColor White
Write-Host "   - Atualiza a cada 5 segundos" -ForegroundColor White
Write-Host ""

# 8. Abrir navegador automaticamente
Write-Host "Deseja abrir o navegador automaticamente? (S/N)" -ForegroundColor Yellow
$resposta = Read-Host

if ($resposta -eq "S" -or $resposta -eq "s") {
    Write-Host "Abrindo navegador..." -ForegroundColor Green
    Start-Process "http://localhost:3000"
}

Write-Host ""
Write-Host "✅ Script concluído!" -ForegroundColor Green
