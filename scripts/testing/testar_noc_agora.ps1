# Script para testar NOC com incidentes ativos
# Verifica se o NOC mostra corretamente servidores com incidentes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DO NOC COM INCIDENTES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuração
$API_URL = "http://localhost:8000/api/v1"
$EMAIL = "admin@coruja.com"
$PASSWORD = "admin123"

# 1. Login
Write-Host "1. Fazendo login..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method Post -Body (@{
    email = $EMAIL
    password = $PASSWORD
} | ConvertTo-Json) -ContentType "application/json"

$TOKEN = $loginResponse.access_token
$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

Write-Host "   ✅ Login realizado com sucesso" -ForegroundColor Green
Write-Host ""

# 2. Verificar incidentes ativos
Write-Host "2. Verificando incidentes ativos..." -ForegroundColor Yellow
$incidents = Invoke-RestMethod -Uri "$API_URL/incidents?status=open" -Method Get -Headers $headers

Write-Host "   📊 Total de incidentes OPEN: $($incidents.Count)" -ForegroundColor Cyan

$acknowledgedIncidents = Invoke-RestMethod -Uri "$API_URL/incidents?status=acknowledged" -Method Get -Headers $headers
Write-Host "   📊 Total de incidentes ACKNOWLEDGED: $($acknowledgedIncidents.Count)" -ForegroundColor Cyan

$totalActiveIncidents = $incidents.Count + $acknowledgedIncidents.Count
Write-Host "   📊 Total de incidentes ATIVOS: $totalActiveIncidents" -ForegroundColor Cyan
Write-Host ""

# 3. Testar endpoint NOC Global Status
Write-Host "3. Testando NOC - Global Status..." -ForegroundColor Yellow
try {
    $nocStatus = Invoke-RestMethod -Uri "$API_URL/noc/global-status" -Method Get -Headers $headers
    
    Write-Host "   ✅ NOC Global Status funcionando!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📊 RESULTADO:" -ForegroundColor Cyan
    Write-Host "      Servidores OK: $($nocStatus.servers_ok)" -ForegroundColor Green
    Write-Host "      Servidores AVISO: $($nocStatus.servers_warning)" -ForegroundColor Yellow
    Write-Host "      Servidores CRÍTICOS: $($nocStatus.servers_critical)" -ForegroundColor Red
    Write-Host "      Total de Servidores: $($nocStatus.total_servers)" -ForegroundColor Cyan
    Write-Host "      Disponibilidade: $($nocStatus.availability)%" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar se NOC zerou
    if ($nocStatus.total_servers -eq 0 -and $totalActiveIncidents -gt 0) {
        Write-Host "   ❌ PROBLEMA DETECTADO: NOC zerou mesmo com incidentes ativos!" -ForegroundColor Red
        Write-Host "      Incidentes ativos: $totalActiveIncidents" -ForegroundColor Red
        Write-Host "      Servidores no NOC: $($nocStatus.total_servers)" -ForegroundColor Red
    } elseif ($nocStatus.total_servers -gt 0) {
        Write-Host "   ✅ NOC está mostrando servidores corretamente!" -ForegroundColor Green
    }
    
} catch {
    Write-Host "   ❌ Erro ao buscar NOC Global Status: $_" -ForegroundColor Red
}
Write-Host ""

# 4. Testar endpoint NOC Heatmap
Write-Host "4. Testando NOC - Heatmap..." -ForegroundColor Yellow
try {
    $heatmap = Invoke-RestMethod -Uri "$API_URL/noc/heatmap" -Method Get -Headers $headers
    
    Write-Host "   ✅ NOC Heatmap funcionando!" -ForegroundColor Green
    Write-Host "   📊 Total de servidores no heatmap: $($heatmap.Count)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($heatmap.Count -gt 0) {
        Write-Host "   📋 Primeiros 5 servidores:" -ForegroundColor Cyan
        $heatmap | Select-Object -First 5 | ForEach-Object {
            $statusColor = switch ($_.status) {
                "ok" { "Green" }
                "warning" { "Yellow" }
                "critical" { "Red" }
                default { "White" }
            }
            Write-Host "      - $($_.hostname): $($_.status) ($($_.availability)%)" -ForegroundColor $statusColor
        }
    }
    
} catch {
    Write-Host "   ❌ Erro ao buscar NOC Heatmap: $_" -ForegroundColor Red
}
Write-Host ""

# 5. Testar endpoint NOC Active Incidents
Write-Host "5. Testando NOC - Active Incidents..." -ForegroundColor Yellow
try {
    $activeIncidents = Invoke-RestMethod -Uri "$API_URL/noc/active-incidents" -Method Get -Headers $headers
    
    Write-Host "   ✅ NOC Active Incidents funcionando!" -ForegroundColor Green
    Write-Host "   📊 Total de incidentes ativos: $($activeIncidents.Count)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($activeIncidents.Count -gt 0) {
        Write-Host "   📋 Primeiros 3 incidentes:" -ForegroundColor Cyan
        $activeIncidents | Select-Object -First 3 | ForEach-Object {
            $severityColor = if ($_.severity -eq "critical") { "Red" } else { "Yellow" }
            Write-Host "      - [$($_.severity)] $($_.server_name) - $($_.sensor_name)" -ForegroundColor $severityColor
            Write-Host "        Duração: $($_.duration)" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host "   ❌ Erro ao buscar NOC Active Incidents: $_" -ForegroundColor Red
}
Write-Host ""

# 6. Testar endpoint NOC KPIs
Write-Host "6. Testando NOC - KPIs..." -ForegroundColor Yellow
try {
    $kpis = Invoke-RestMethod -Uri "$API_URL/noc/kpis" -Method Get -Headers $headers
    
    Write-Host "   ✅ NOC KPIs funcionando!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   📊 KPIs:" -ForegroundColor Cyan
    Write-Host "      MTTR (Tempo Médio de Resolução): $($kpis.mttr) minutos" -ForegroundColor Cyan
    Write-Host "      MTBF (Tempo Médio Entre Falhas): $($kpis.mtbf) horas" -ForegroundColor Cyan
    Write-Host "      SLA (Acordo de Nível de Serviço): $($kpis.sla)%" -ForegroundColor Cyan
    Write-Host "      Incidentes 24h: $($kpis.incidents_24h)" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ❌ Erro ao buscar NOC KPIs: $_" -ForegroundColor Red
}
Write-Host ""

# 7. Resumo Final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO DO TESTE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($nocStatus.total_servers -gt 0) {
    Write-Host "✅ NOC está funcionando corretamente!" -ForegroundColor Green
    Write-Host "   - Mostrando $($nocStatus.total_servers) servidores" -ForegroundColor Green
    Write-Host "   - $totalActiveIncidents incidentes ativos detectados" -ForegroundColor Green
    Write-Host "   - Disponibilidade geral: $($nocStatus.availability)%" -ForegroundColor Green
} else {
    Write-Host "⚠️ NOC pode estar com problemas" -ForegroundColor Yellow
    Write-Host "   - Nenhum servidor sendo exibido" -ForegroundColor Yellow
    Write-Host "   - Verifique se há servidores cadastrados" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Teste concluído!" -ForegroundColor Cyan
