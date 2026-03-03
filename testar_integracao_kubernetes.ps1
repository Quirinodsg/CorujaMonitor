# Script para Testar Integração Kubernetes com Probe
# Data: 27 FEV 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DE INTEGRAÇÃO KUBERNETES + PROBE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000"
$FRONTEND_URL = "http://localhost:3000"

# Função para fazer requisições
function Invoke-ApiRequest {
    param(
        [string]$Method,
        [string]$Endpoint,
        [hashtable]$Body = $null,
        [string]$Token = $null
    )
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    if ($Token) {
        $headers["Authorization"] = "Bearer $Token"
    }
    
    try {
        $params = @{
            Method = $Method
            Uri = "$API_URL$Endpoint"
            Headers = $headers
        }
        
        if ($Body) {
            $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Host "Erro: $_" -ForegroundColor Red
        return $null
    }
}

# 1. Verificar se API está rodando
Write-Host "1. Verificando API..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$API_URL/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "   ✓ API está rodando" -ForegroundColor Green
}
catch {
    Write-Host "   ✗ API não está acessível em $API_URL" -ForegroundColor Red
    Write-Host "   Execute: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# 2. Fazer login
Write-Host ""
Write-Host "2. Fazendo login..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin@coruja.com"
    password = "admin123"
}

$loginResponse = Invoke-ApiRequest -Method "POST" -Endpoint "/api/v1/auth/login" -Body $loginBody

if ($loginResponse -and $loginResponse.access_token) {
    $token = $loginResponse.access_token
    Write-Host "   ✓ Login realizado com sucesso" -ForegroundColor Green
}
else {
    Write-Host "   ✗ Falha no login" -ForegroundColor Red
    exit 1
}

# 3. Verificar endpoint de clusters
Write-Host ""
Write-Host "3. Verificando endpoint de clusters..." -ForegroundColor Yellow
$clusters = Invoke-ApiRequest -Method "GET" -Endpoint "/api/v1/kubernetes/clusters" -Token $token

if ($clusters -ne $null) {
    Write-Host "   ✓ Endpoint funcionando" -ForegroundColor Green
    Write-Host "   Clusters configurados: $($clusters.Count)" -ForegroundColor Cyan
    
    if ($clusters.Count -gt 0) {
        foreach ($cluster in $clusters) {
            Write-Host ""
            Write-Host "   Cluster: $($cluster.cluster_name)" -ForegroundColor White
            Write-Host "   - Tipo: $($cluster.cluster_type)" -ForegroundColor Gray
            Write-Host "   - Status: $($cluster.connection_status)" -ForegroundColor Gray
            Write-Host "   - Nodes: $($cluster.total_nodes)" -ForegroundColor Gray
            Write-Host "   - Pods: $($cluster.total_pods)" -ForegroundColor Gray
            Write-Host "   - Última coleta: $($cluster.last_collected_at)" -ForegroundColor Gray
        }
    }
}
else {
    Write-Host "   ✗ Erro ao acessar endpoint" -ForegroundColor Red
}

# 4. Verificar se probe está rodando
Write-Host ""
Write-Host "4. Verificando probe..." -ForegroundColor Yellow
$probeProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*probe_core.py*" -or $_.CommandLine -like "*probe_service.py*"
}

if ($probeProcess) {
    Write-Host "   ✓ Probe está rodando (PID: $($probeProcess.Id))" -ForegroundColor Green
}
else {
    Write-Host "   ⚠ Probe não está rodando" -ForegroundColor Yellow
    Write-Host "   Para iniciar: cd probe && .\iniciar_probe_limpo.bat" -ForegroundColor Cyan
}

# 5. Verificar logs do probe
Write-Host ""
Write-Host "5. Verificando logs do probe..." -ForegroundColor Yellow
$logFile = "probe\probe.log"

if (Test-Path $logFile) {
    Write-Host "   ✓ Arquivo de log encontrado" -ForegroundColor Green
    
    # Últimas 20 linhas
    $lastLines = Get-Content $logFile -Tail 20
    
    # Procurar por mensagens Kubernetes
    $k8sLines = $lastLines | Where-Object { $_ -match "kubernetes|Kubernetes|K8s" }
    
    if ($k8sLines) {
        Write-Host ""
        Write-Host "   Últimas mensagens Kubernetes:" -ForegroundColor Cyan
        foreach ($line in $k8sLines) {
            if ($line -match "ERROR|Error|error") {
                Write-Host "   $line" -ForegroundColor Red
            }
            elseif ($line -match "WARNING|Warning|warning") {
                Write-Host "   $line" -ForegroundColor Yellow
            }
            else {
                Write-Host "   $line" -ForegroundColor Gray
            }
        }
    }
    else {
        Write-Host "   ⚠ Nenhuma mensagem Kubernetes encontrada nos logs recentes" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   ⚠ Arquivo de log não encontrado" -ForegroundColor Yellow
}

# 6. Verificar biblioteca kubernetes instalada
Write-Host ""
Write-Host "6. Verificando biblioteca kubernetes..." -ForegroundColor Yellow
try {
    $pythonCheck = python -c "import kubernetes; print('OK')" 2>&1
    if ($pythonCheck -match "OK") {
        Write-Host "   ✓ Biblioteca kubernetes instalada" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ Biblioteca kubernetes não instalada" -ForegroundColor Red
        Write-Host "   Execute: cd probe && pip install kubernetes pyyaml" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ⚠ Não foi possível verificar (Python não encontrado?)" -ForegroundColor Yellow
}

# 7. Verificar recursos coletados
Write-Host ""
Write-Host "7. Verificando recursos coletados..." -ForegroundColor Yellow

if ($clusters -and $clusters.Count -gt 0) {
    $clusterId = $clusters[0].id
    $resources = Invoke-ApiRequest -Method "GET" -Endpoint "/api/v1/kubernetes/clusters/$clusterId/resources" -Token $token
    
    if ($resources -ne $null) {
        Write-Host "   ✓ Endpoint de recursos funcionando" -ForegroundColor Green
        Write-Host "   Total de recursos: $($resources.Count)" -ForegroundColor Cyan
        
        if ($resources.Count -gt 0) {
            # Agrupar por tipo
            $byType = $resources | Group-Object -Property resource_type
            Write-Host ""
            Write-Host "   Recursos por tipo:" -ForegroundColor Cyan
            foreach ($group in $byType) {
                Write-Host "   - $($group.Name): $($group.Count)" -ForegroundColor Gray
            }
        }
        else {
            Write-Host "   ⚠ Nenhum recurso coletado ainda" -ForegroundColor Yellow
            Write-Host "   Aguarde a próxima coleta (60 segundos)" -ForegroundColor Cyan
        }
    }
}
else {
    Write-Host "   ⚠ Nenhum cluster configurado" -ForegroundColor Yellow
}

# 8. Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Status dos Componentes:" -ForegroundColor White
Write-Host "- API: " -NoNewline
if ($health) { Write-Host "✓ Rodando" -ForegroundColor Green } else { Write-Host "✗ Parada" -ForegroundColor Red }

Write-Host "- Probe: " -NoNewline
if ($probeProcess) { Write-Host "✓ Rodando" -ForegroundColor Green } else { Write-Host "✗ Parada" -ForegroundColor Red }

Write-Host "- Biblioteca Kubernetes: " -NoNewline
if ($pythonCheck -match "OK") { Write-Host "✓ Instalada" -ForegroundColor Green } else { Write-Host "✗ Não instalada" -ForegroundColor Red }

Write-Host ""
Write-Host "Clusters Configurados: $($clusters.Count)" -ForegroundColor White

if ($clusters -and $clusters.Count -gt 0 -and $resources) {
    Write-Host "Recursos Coletados: $($resources.Count)" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($clusters.Count -eq 0) {
    Write-Host "1. Configure um cluster Kubernetes:" -ForegroundColor Yellow
    Write-Host "   - Acesse: $FRONTEND_URL" -ForegroundColor Cyan
    Write-Host "   - Login: admin@coruja.com / admin123" -ForegroundColor Cyan
    Write-Host "   - Vá em 'Servidores' → 'Monitorar Serviços'" -ForegroundColor Cyan
    Write-Host "   - Clique em '☸️ Kubernetes'" -ForegroundColor Cyan
    Write-Host "   - Siga o wizard de configuração" -ForegroundColor Cyan
}
elseif (-not $probeProcess) {
    Write-Host "1. Inicie o probe:" -ForegroundColor Yellow
    Write-Host "   cd probe" -ForegroundColor Cyan
    Write-Host "   .\iniciar_probe_limpo.bat" -ForegroundColor Cyan
}
elseif ($pythonCheck -notmatch "OK") {
    Write-Host "1. Instale a biblioteca kubernetes:" -ForegroundColor Yellow
    Write-Host "   cd probe" -ForegroundColor Cyan
    Write-Host "   pip install kubernetes pyyaml" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Reinicie o probe:" -ForegroundColor Yellow
    Write-Host "   .\parar_todas_probes.bat" -ForegroundColor Cyan
    Write-Host "   .\iniciar_probe_limpo.bat" -ForegroundColor Cyan
}
elseif ($resources -and $resources.Count -eq 0) {
    Write-Host "1. Aguarde a próxima coleta (60 segundos)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Monitore os logs:" -ForegroundColor Yellow
    Write-Host "   Get-Content probe\probe.log -Tail 50 -Wait" -ForegroundColor Cyan
}
else {
    Write-Host "✓ Sistema funcionando corretamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Criar dashboards no frontend" -ForegroundColor Cyan
    Write-Host "2. Implementar alertas" -ForegroundColor Cyan
    Write-Host "3. Adicionar mais clusters" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Documentação:" -ForegroundColor White
Write-Host "- INTEGRACAO_KUBERNETES_PROBE_27FEV.md" -ForegroundColor Gray
Write-Host "- RESUMO_COMPLETO_KUBERNETES_27FEV.md" -ForegroundColor Gray
Write-Host "- GUIA_RAPIDO_KUBERNETES.md" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
