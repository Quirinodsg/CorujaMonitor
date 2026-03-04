# Script para testar relatórios
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DE RELATÓRIOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000/api/v1"

# Login
Write-Host "1. Fazendo login..." -ForegroundColor Yellow
$login = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method Post -Body '{"email":"admin@coruja.com","password":"admin123"}' -ContentType "application/json"
$headers = @{"Authorization" = "Bearer $($login.access_token)"}
Write-Host "   ✅ Login realizado" -ForegroundColor Green
Write-Host ""

# Testar templates
Write-Host "2. Listando templates de relatórios..." -ForegroundColor Yellow
try {
    $templates = Invoke-RestMethod -Uri "$API_URL/reports/templates" -Method Get -Headers $headers
    Write-Host "   ✅ Total de templates: $($templates.Count)" -ForegroundColor Green
    $templates | ForEach-Object {
        Write-Host "      - $($_.name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Erro ao listar templates: $_" -ForegroundColor Red
}
Write-Host ""

# Testar relatório de disponibilidade
Write-Host "3. Testando relatório de disponibilidade mensal..." -ForegroundColor Yellow
try {
    $availability = Invoke-RestMethod -Uri "$API_URL/reports/generate/availability/monthly" -Method Get -Headers $headers
    Write-Host "   ✅ Relatório gerado com sucesso!" -ForegroundColor Green
    Write-Host "      Período: $($availability.period)" -ForegroundColor Cyan
    Write-Host "      Total de servidores: $($availability.total_servers)" -ForegroundColor Cyan
    Write-Host "      Disponibilidade: $($availability.availability_percentage)%" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}
Write-Host ""

# Testar relatório de problemas
Write-Host "4. Testando relatório de problemas..." -ForegroundColor Yellow
try {
    $problems = Invoke-RestMethod -Uri "$API_URL/reports/generate/problems/monthly" -Method Get -Headers $headers
    Write-Host "   ✅ Relatório gerado com sucesso!" -ForegroundColor Green
    Write-Host "      Servidores com problemas: $($problems.servers_with_most_problems.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}
Write-Host ""

# Testar relatório de IA
Write-Host "5. Testando relatório de resoluções por IA..." -ForegroundColor Yellow
try {
    $ai = Invoke-RestMethod -Uri "$API_URL/reports/generate/ai-resolution/monthly" -Method Get -Headers $headers
    Write-Host "   ✅ Relatório gerado com sucesso!" -ForegroundColor Green
    Write-Host "      Total de incidentes: $($ai.total_incidents)" -ForegroundColor Cyan
    Write-Host "      Resolvidos pela IA: $($ai.ai_resolved)" -ForegroundColor Cyan
    Write-Host "      Taxa de resolução: $($ai.ai_resolution_rate)%" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}
Write-Host ""

# Testar relatório de CPU
Write-Host "6. Testando relatório de utilização de CPU..." -ForegroundColor Yellow
try {
    $cpu = Invoke-RestMethod -Uri "$API_URL/reports/generate/cpu-utilization/monthly" -Method Get -Headers $headers
    Write-Host "   ✅ Relatório gerado com sucesso!" -ForegroundColor Green
    Write-Host "      Utilização média: $($cpu.average_utilization)%" -ForegroundColor Cyan
    Write-Host "      Pico máximo: $($cpu.peak_utilization)%" -ForegroundColor Cyan
    Write-Host "      Total de servidores: $($cpu.total_servers)" -ForegroundColor Cyan
    
    if ($cpu.cloud_costs) {
        Write-Host "      ☁️ Custos de nuvem calculados!" -ForegroundColor Green
        Write-Host "         Provedor mais barato: $($cpu.cloud_costs.cheapest_provider)" -ForegroundColor Cyan
        Write-Host "         Custo mensal: R$ $($cpu.cloud_costs.cheapest_cost)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
    Write-Host "      Detalhes: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Testar relatório de Memória
Write-Host "7. Testando relatório de utilização de Memória..." -ForegroundColor Yellow
try {
    $memory = Invoke-RestMethod -Uri "$API_URL/reports/generate/memory-utilization/monthly" -Method Get -Headers $headers
    Write-Host "   ✅ Relatório gerado com sucesso!" -ForegroundColor Green
    Write-Host "      Utilização média: $($memory.average_utilization)%" -ForegroundColor Cyan
    Write-Host "      Pico máximo: $($memory.peak_utilization)%" -ForegroundColor Cyan
    Write-Host "      Total de servidores: $($memory.total_servers)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
    Write-Host "      Detalhes: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE CONCLUÍDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
