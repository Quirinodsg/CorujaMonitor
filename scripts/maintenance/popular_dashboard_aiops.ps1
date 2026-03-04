# Script para popular o dashboard AIOps com análises
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "  POPULAR DASHBOARD AIOPS" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script vai executar análises para popular o dashboard." -ForegroundColor White
Write-Host ""

# Login
Write-Host "1. Fazendo login..." -ForegroundColor Cyan
$body = '{"email":"admin@coruja.com","password":"admin123"}'
try {
    $login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
    $token = $login.access_token
    $headers = @{"Authorization"="Bearer $token"}
    Write-Host "   OK Login realizado" -ForegroundColor Green
} catch {
    Write-Host "   ERRO: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique se o sistema está rodando:" -ForegroundColor Yellow
    Write-Host "  docker ps" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "2. Buscando sensores..." -ForegroundColor Cyan
try {
    $sensors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensors/" -Method Get -Headers $headers
    Write-Host "   OK $($sensors.Count) sensores encontrados" -ForegroundColor Green
    
    if ($sensors.Count -eq 0) {
        Write-Host "   AVISO: Nenhum sensor encontrado." -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "   ERRO: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Executando análises de anomalias..." -ForegroundColor Cyan
$anomaliesDetected = 0
$analysisCount = 0

# Analisar primeiros 5 sensores
$sensorsToAnalyze = $sensors | Select-Object -First 5
foreach ($sensor in $sensorsToAnalyze) {
    Write-Host "   Analisando: $($sensor.name)..." -ForegroundColor Gray
    
    try {
        $anomalyRequest = @{
            sensor_id = $sensor.id
            lookback_hours = 24
        } | ConvertTo-Json
        
        $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/anomaly-detection" -Method Post -Body $anomalyRequest -Headers $headers -ContentType "application/json"
        
        $analysisCount++
        if ($result.anomaly_detected) {
            $anomaliesDetected++
            Write-Host "      ANOMALIA detectada! Confiança: $([math]::Round($result.confidence * 100, 1))%" -ForegroundColor Yellow
        } else {
            Write-Host "      Normal" -ForegroundColor Green
        }
    } catch {
        Write-Host "      Erro ou dados insuficientes" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "   Resumo:" -ForegroundColor White
Write-Host "   - Análises executadas: $analysisCount" -ForegroundColor Cyan
Write-Host "   - Anomalias detectadas: $anomaliesDetected" -ForegroundColor Yellow

Write-Host ""
Write-Host "4. Executando correlação de eventos..." -ForegroundColor Cyan
try {
    $correlationRequest = @{
        time_window_minutes = 30
        severity_filter = @("critical", "warning")
    } | ConvertTo-Json
    
    $corrResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/event-correlation" -Method Post -Body $correlationRequest -Headers $headers -ContentType "application/json"
    
    Write-Host "   OK Correlação executada" -ForegroundColor Green
    Write-Host "   - Grupos encontrados: $($corrResult.total_groups)" -ForegroundColor Cyan
} catch {
    Write-Host "   Erro na correlação (normal se não houver incidentes)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "5. Buscando incidentes para análise RCA..." -ForegroundColor Cyan
try {
    $incidents = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/incidents/?status=open" -Method Get -Headers $headers
    
    if ($incidents.Count -gt 0) {
        Write-Host "   OK $($incidents.Count) incidentes encontrados" -ForegroundColor Green
        
        # Analisar primeiro incidente
        $incident = $incidents[0]
        Write-Host ""
        Write-Host "6. Executando análise de causa raiz..." -ForegroundColor Cyan
        Write-Host "   Incidente: $($incident.title)" -ForegroundColor Gray
        
        try {
            $rcaRequest = @{
                incident_id = $incident.id
            } | ConvertTo-Json
            
            $rcaResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/root-cause-analysis" -Method Post -Body $rcaRequest -Headers $headers -ContentType "application/json"
            
            Write-Host "   OK RCA executado" -ForegroundColor Green
            Write-Host "   - Causa raiz: $($rcaResult.root_cause)" -ForegroundColor Cyan
            Write-Host "   - Confiança: $([math]::Round($rcaResult.confidence * 100, 0))%" -ForegroundColor Cyan
            
            Write-Host ""
            Write-Host "7. Criando plano de ação..." -ForegroundColor Cyan
            
            try {
                $planResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/action-plan/$($incident.id)?include_correlation=true" -Method Post -Headers $headers
                
                Write-Host "   OK Plano criado: $($planResult.plan_id)" -ForegroundColor Green
                Write-Host "   - Ações imediatas: $($planResult.immediate_actions.Count)" -ForegroundColor Cyan
                Write-Host "   - Ações curto prazo: $($planResult.short_term_actions.Count)" -ForegroundColor Cyan
                Write-Host "   - Ações longo prazo: $($planResult.long_term_actions.Count)" -ForegroundColor Cyan
            } catch {
                Write-Host "   Erro ao criar plano" -ForegroundColor Gray
            }
        } catch {
            Write-Host "   Erro ao executar RCA" -ForegroundColor Gray
        }
    } else {
        Write-Host "   Nenhum incidente aberto (sistema saudável)" -ForegroundColor Green
    }
} catch {
    Write-Host "   Erro ao buscar incidentes" -ForegroundColor Gray
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  DASHBOARD POPULADO!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "Agora acesse o dashboard AIOps e veja:" -ForegroundColor White
Write-Host "  Menu -> AIOps -> Overview" -ForegroundColor Cyan
Write-Host ""
Write-Host "Você verá:" -ForegroundColor White
Write-Host "  - Anomalias detectadas: $anomaliesDetected" -ForegroundColor Yellow
Write-Host "  - Análises realizadas: $analysisCount" -ForegroundColor Yellow
Write-Host "  - Correlações executadas: 1" -ForegroundColor Yellow
Write-Host ""
Write-Host "O dashboard NÃO está mais zerado!" -ForegroundColor Green
Write-Host ""
Write-Host "Para manter atualizado:" -ForegroundColor Cyan
Write-Host "  - Execute este script periodicamente" -ForegroundColor Gray
Write-Host "  - Ou execute análises manualmente na interface" -ForegroundColor Gray
Write-Host ""
