# Script para testar status do Ollama
Write-Host "🔍 Testando Status do Ollama..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar variável de ambiente nos containers
Write-Host "1️⃣ Verificando variável OLLAMA_BASE_URL nos containers:" -ForegroundColor Yellow
Write-Host "   API:" -ForegroundColor Gray
docker exec coruja-api sh -c "printenv | grep OLLAMA"
Write-Host "   AI-Agent:" -ForegroundColor Gray
docker exec coruja-ai-agent sh -c "printenv | grep OLLAMA"
Write-Host ""

# 2. Testar conexão direta com Ollama
Write-Host "2️⃣ Testando conexão direta com Ollama:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "   ✅ Ollama está ONLINE" -ForegroundColor Green
    Write-Host "   Modelos instalados:" -ForegroundColor Gray
    foreach ($model in $response.models) {
        Write-Host "      - $($model.name)" -ForegroundColor White
    }
} catch {
    Write-Host "   ❌ Ollama está OFFLINE: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Login na API
Write-Host "3️⃣ Fazendo login na API..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "   ✅ Login realizado com sucesso" -ForegroundColor Green
    Write-Host ""
    
    # 4. Testar endpoint de status do Ollama
    Write-Host "4️⃣ Testando endpoint /api/v1/ai/status:" -ForegroundColor Yellow
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/status" -Method Get -Headers $headers
    
    Write-Host "   Status do Ollama:" -ForegroundColor Gray
    Write-Host "      Online: $($statusResponse.online)" -ForegroundColor $(if ($statusResponse.online) { "Green" } else { "Red" })
    Write-Host "      URL: $($statusResponse.url)" -ForegroundColor White
    Write-Host "      Modelo: $($statusResponse.model)" -ForegroundColor White
    if ($statusResponse.version) {
        Write-Host "      Versão: $($statusResponse.version)" -ForegroundColor White
    }
    if ($statusResponse.error) {
        Write-Host "      Erro: $($statusResponse.error)" -ForegroundColor Red
    }
    
    Write-Host ""
    if ($statusResponse.online) {
        Write-Host "🎉 SUCESSO! Ollama está funcionando corretamente!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Ollama está configurado mas não está respondendo" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ❌ Erro ao testar: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Teste concluído!" -ForegroundColor Cyan
