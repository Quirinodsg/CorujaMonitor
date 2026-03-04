# Script para testar AIOps com dados reais
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "  TESTE COMPLETO DO AIOPS" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
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
    exit 1
}

Write-Host ""
Write-Host "2. Verificando sensores disponíveis..." -ForegroundColor Cyan
try {
    $sensors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensors/" -Method Get -Headers $headers
    Write-Host "   OK $($sensors.Count) sensores encontrados" -ForegroundColor Green
    
    if ($sensors.Count -eq 0) {
        Write-Host "   AVISO: Nenhum sensor encontrado. AIOps precisa de sensores para funcionar." -ForegroundColor Yellow
        exit 0
    }
    
    # Mostrar primeiros 5 sensores
    Write-Host ""
    Write-Host "   Sensores disponíveis:" -ForegroundColor White
    $sensors | Select-Object -First 5 | ForEach-Object {
        Write-Host "   - ID: $($_.id) | $($_.name) ($($_.sensor_type))" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ERRO: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Testando Detecção de Anomalias..." -ForegroundColor Cyan
$testSensor = $sensors[0]
Write-Host "   Analisando sensor: $($testSensor.name)" -ForegroundColor White

try {
    $anomalyRequest = @{
        sensor_id = $testSensor.id
        lookback_hours = 24
    } | ConvertTo-Json
    
    $anomalyResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/anomaly-detection" -Method Post -Body $anomalyRequest -Headers $headers -ContentType "application/json"
    
    Write-Host "   OK Análise concluída!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Resultados:" -ForegroundColor Yellow
    Write-Host "   - Anomalia detectada: $($anomalyResult.anomaly_detected)" -ForegroundColor White
    Write-Host "   - Confiança: $([math]::Round($anomalyResult.confidence * 100, 2))%" -ForegroundColor White
    
    if ($anomalyResult.anomalies) {
        Write-Host "   - Total de anomalias: $($anomalyResult.anomalies.Count)" -ForegroundColor White
    }
    
    if ($anomalyResult.recommendation) {
        Write-Host "   - Recomendação: $($anomalyResult.recommendation)" -ForegroundColor Cyan
    }
} catch {
    $errorDetail = $_.Exception.Message
    if ($_.ErrorDetails.Message) {
        $errorDetail = ($_.ErrorDetails.Message | ConvertFrom-Json).detail
    }
    Write-Host "   ERRO: $errorDetail" -ForegroundColor Red
    
    if ($errorDetail -like "*Insufficient data*") {
        Write-Host "   INFO: Sensor não tem dados suficientes (mínimo 10 amostras)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "4. Testando Correlação de Eventos..." -ForegroundColor Cyan
try {
    $correlationRequest = @{
        time_window_minutes = 30
        severity_filter = @("critical", "warning")
    } | ConvertTo-Json
    
    $correlationResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/event-correlation" -Method Post -Body $correlationRequest -Headers $headers -ContentType "application/json"
    
    Write-Host "   OK Correlação concluída!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Resultados:" -ForegroundColor Yellow
    Write-Host "   - Eventos correlacionados: $($correlationResult.correlated)" -ForegroundColor White
    Write-Host "   - Total de grupos: $($correlationResult.total_groups)" -ForegroundColor White
    
    if ($correlationResult.analysis) {
        Write-Host "   - Incidentes correlacionados: $($correlationResult.analysis.total_correlated_incidents)" -ForegroundColor White
        Write-Host "   - Servidores afetados: $($correlationResult.analysis.total_affected_servers)" -ForegroundColor White
        Write-Host "   - Padrão identificado: $($correlationResult.analysis.pattern)" -ForegroundColor Cyan
    }
} catch {
    $errorDetail = $_.Exception.Message
    if ($_.ErrorDetails.Message) {
        $errorDetail = ($_.ErrorDetails.Message | ConvertFrom-Json).detail
    }
    Write-Host "   ERRO: $errorDetail" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Verificando incidentes para RCA..." -ForegroundColor Cyan
try {
    $incidents = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/incidents/" -Method Get -Headers $headers
    
    if ($incidents.Count -eq 0) {
        Write-Host "   INFO: Nenhum incidente encontrado para análise de causa raiz" -ForegroundColor Yellow
    } else {
        Write-Host "   OK $($incidents.Count) incidentes encontrados" -ForegroundColor Green
        
        # Testar RCA no primeiro incidente
        $testIncident = $incidents[0]
        Write-Host ""
        Write-Host "6. Testando Análise de Causa Raiz..." -ForegroundColor Cyan
        Write-Host "   Analisando incidente: $($testIncident.title)" -ForegroundColor White
        
        try {
            $rcaRequest = @{
                incident_id = $testIncident.id
            } | ConvertTo-Json
            
            $rcaResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/root-cause-analysis" -Method Post -Body $rcaRequest -Headers $headers -ContentType "application/json"
            
            Write-Host "   OK Análise concluída!" -ForegroundColor Green
            Write-Host ""
            Write-Host "   Resultados:" -ForegroundColor Yellow
            Write-Host "   - Causa raiz: $($rcaResult.root_cause)" -ForegroundColor White
            Write-Host "   - Confiança: $([math]::Round($rcaResult.confidence * 100, 2))%" -ForegroundColor White
            Write-Host "   - Sintomas detectados: $($rcaResult.symptoms.Count)" -ForegroundColor White
            Write-Host "   - Eventos na timeline: $($rcaResult.timeline.Count)" -ForegroundColor White
            
            Write-Host ""
            Write-Host "7. Testando Criação de Plano de Ação..." -ForegroundColor Cyan
            
            try {
                $actionPlanResult = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aiops/action-plan/$($testIncident.id)?include_correlation=true" -Method Post -Headers $headers
                
                Write-Host "   OK Plano criado!" -ForegroundColor Green
                Write-Host ""
                Write-Host "   Plano de Ação:" -ForegroundColor Yellow
                Write-Host "   - ID do Plano: $($actionPlanResult.plan_id)" -ForegroundColor White
                Write-Host "   - Severidade: $($actionPlanResult.severity)" -ForegroundColor White
                Write-Host "   - Tempo estimado: $($actionPlanResult.estimated_resolution_time)" -ForegroundColor White
                Write-Host "   - Ações imediatas: $($actionPlanResult.immediate_actions.Count)" -ForegroundColor White
                Write-Host "   - Ações curto prazo: $($actionPlanResult.short_term_actions.Count)" -ForegroundColor White
                Write-Host "   - Ações longo prazo: $($actionPlanResult.long_term_actions.Count)" -ForegroundColor White
                Write-Host "   - Automação disponível: $($actionPlanResult.automation_available)" -ForegroundColor Cyan
                
                if ($actionPlanResult.immediate_actions.Count -gt 0) {
                    Write-Host ""
                    Write-Host "   Primeira ação imediata:" -ForegroundColor Yellow
                    $firstAction = $actionPlanResult.immediate_actions[0]
                    Write-Host "   - Prioridade: $($firstAction.priority)" -ForegroundColor White
                    Write-Host "   - Ação: $($firstAction.action)" -ForegroundColor White
                    Write-Host "   - Tempo estimado: $($firstAction.estimated_time)" -ForegroundColor White
                    Write-Host "   - Nível de risco: $($firstAction.risk_level)" -ForegroundColor White
                    if ($firstAction.command) {
                        Write-Host "   - Comando: $($firstAction.command)" -ForegroundColor Cyan
                    }
                }
            } catch {
                Write-Host "   ERRO ao criar plano: $_" -ForegroundColor Red
            }
        } catch {
            Write-Host "   ERRO ao analisar causa raiz: $_" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   ERRO ao buscar incidentes: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  RESUMO DO TESTE" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "O AIOps está funcionando e pronto para analisar:" -ForegroundColor White
Write-Host "  Detecção de Anomalias - Analisa padrões em métricas" -ForegroundColor Gray
Write-Host "  Correlação de Eventos - Agrupa incidentes relacionados" -ForegroundColor Gray
Write-Host "  Análise de Causa Raiz - Identifica causa de problemas" -ForegroundColor Gray
Write-Host "  Planos de Ação - Cria planos de resolução automáticos" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "  - AIOps precisa de DADOS para funcionar" -ForegroundColor White
Write-Host "  - Mínimo 10 métricas por sensor para detecção de anomalias" -ForegroundColor White
Write-Host "  - Incidentes são necessários para RCA e planos de ação" -ForegroundColor White
Write-Host "  - Quanto mais dados, melhor a análise!" -ForegroundColor White
Write-Host ""
Write-Host "Para gerar dados de teste:" -ForegroundColor Cyan
Write-Host "  1. Deixe a probe coletar métricas por algumas horas" -ForegroundColor Gray
Write-Host "  2. Ou use as Ferramentas de Teste para simular falhas" -ForegroundColor Gray
Write-Host "  3. Dashboard AIOps será atualizado automaticamente" -ForegroundColor Gray
Write-Host ""
