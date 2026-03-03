# Script para testar notificações automáticas
Write-Host "=== TESTE DE NOTIFICAÇÕES AUTOMÁTICAS ===" -ForegroundColor Cyan
Write-Host ""

$apiKey = "ijsnz-cluur-lsr7i-lka62-3lwwp"
$baseUrl = "http://localhost:8000/api/v1"

# Headers com API Key
$headers = @{
    'X-API-Key' = $apiKey
    'Content-Type' = 'application/json'
}

Write-Host "1. Buscando sensores disponíveis..." -ForegroundColor Yellow
try {
    $sensors = Invoke-RestMethod -Uri "$baseUrl/sensors" -Method GET -Headers $headers
    Write-Host "   ✓ Encontrados $($sensors.Count) sensores" -ForegroundColor Green
    
    # Pegar o primeiro sensor ativo
    $sensor = $sensors | Where-Object { $_.is_active -eq $true } | Select-Object -First 1
    
    if ($sensor) {
        Write-Host "   ✓ Sensor selecionado: $($sensor.name) (ID: $($sensor.id))" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "2. Simulando falha no sensor..." -ForegroundColor Yellow
        $failureBody = @{
            sensor_id = $sensor.id
            duration_minutes = 5
        } | ConvertTo-Json
        
        $result = Invoke-RestMethod -Uri "$baseUrl/test-tools/simulate-failure" -Method POST -Headers $headers -Body $failureBody
        Write-Host "   ✓ Falha simulada com sucesso!" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "3. Aguardando worker processar (60 segundos)..." -ForegroundColor Yellow
        Write-Host "   O worker roda a cada 60 segundos para verificar sensores" -ForegroundColor Gray
        
        for ($i = 60; $i -gt 0; $i--) {
            Write-Host "`r   Aguardando: $i segundos restantes..." -NoNewline -ForegroundColor Cyan
            Start-Sleep -Seconds 1
        }
        Write-Host ""
        Write-Host ""
        
        Write-Host "4. Verificando logs do worker..." -ForegroundColor Yellow
        Write-Host "   Procurando por notificações enviadas..." -ForegroundColor Gray
        Write-Host ""
        
        $logs = docker logs coruja-worker --tail 200 2>&1 | Select-String -Pattern "Incidente criado|Enviando notificações|TOPdesk|Teams|Email|Resumo"
        
        if ($logs) {
            Write-Host "   LOGS ENCONTRADOS:" -ForegroundColor Green
            $logs | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
        } else {
            Write-Host "   ⚠ Nenhum log de notificação encontrado ainda" -ForegroundColor Yellow
            Write-Host "   Isso pode significar que:" -ForegroundColor Gray
            Write-Host "   - O worker ainda não processou (aguarde mais 60 segundos)" -ForegroundColor Gray
            Write-Host "   - Não há configuração de notificações ativa" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "5. Verificando incidentes criados..." -ForegroundColor Yellow
        $incidents = Invoke-RestMethod -Uri "$baseUrl/incidents?status=open" -Method GET -Headers $headers
        
        if ($incidents -and $incidents.Count -gt 0) {
            Write-Host "   ✓ Encontrados $($incidents.Count) incidente(s) aberto(s)" -ForegroundColor Green
            $incidents | ForEach-Object {
                Write-Host "   - ID: $($_.id) | $($_.title) | Severidade: $($_.severity)" -ForegroundColor White
            }
        } else {
            Write-Host "   ⚠ Nenhum incidente aberto encontrado" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "   ✗ Nenhum sensor ativo encontrado" -ForegroundColor Red
    }
    
} catch {
    Write-Host "   ✗ Erro: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== PRÓXIMOS PASSOS ===" -ForegroundColor Cyan
Write-Host "1. Verifique o TOPdesk para ver se o chamado foi criado" -ForegroundColor White
Write-Host "2. Verifique o Teams para ver se a mensagem foi enviada" -ForegroundColor White
Write-Host "3. Verifique o email se configurado" -ForegroundColor White
Write-Host "4. Execute novamente: docker logs coruja-worker --tail 100" -ForegroundColor White
Write-Host ""
