# Script de teste completo do botão Monitorar Serviços
Write-Host "=== TESTE COMPLETO: MONITORAR SERVIÇOS ===" -ForegroundColor Cyan

# 1. Verificar se frontend está rodando
Write-Host "`n1. Verificando Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Frontend rodando (Status $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend não está respondendo" -ForegroundColor Red
    exit 1
}

# 2. Verificar se API está rodando
Write-Host "`n2. Verificando API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ API rodando" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API não está respondendo" -ForegroundColor Red
    exit 1
}

# 3. Testar login
Write-Host "`n3. Testando Login..." -ForegroundColor Yellow
try {
    $body = @{email='admin@coruja.com';password='admin123'} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' -Method Post -Body $body -ContentType 'application/json'
    $token = $response.access_token
    Write-Host "   ✅ Login bem-sucedido" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erro no login" -ForegroundColor Red
    exit 1
}

# 4. Listar sensores standalone
Write-Host "`n4. Verificando Sensores Independentes..." -ForegroundColor Yellow
try {
    $headers = @{Authorization = "Bearer $token"}
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/sensors/standalone' -Method Get -Headers $headers
    Write-Host "   ✅ Endpoint de sensores independentes funcionando" -ForegroundColor Green
    Write-Host "   📊 Total de sensores: $($response.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Erro ao listar sensores" -ForegroundColor Red
}

# 5. Verificar compilação do frontend
Write-Host "`n5. Verificando Compilação do Frontend..." -ForegroundColor Yellow
$logs = docker logs coruja-frontend --tail 50 2>&1 | Out-String
if ($logs -match "webpack compiled") {
    Write-Host "   ✅ Frontend compilado com sucesso" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Verificar logs do frontend" -ForegroundColor Yellow
}

Write-Host "`n=== INSTRUÇÕES DE TESTE MANUAL ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "2. Faça login: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "3. Vá em: Servidores Monitorados" -ForegroundColor White
Write-Host "4. Clique no botão: ☁️ Monitorar Serviços" -ForegroundColor White
Write-Host ""
Write-Host "DEVE APARECER:" -ForegroundColor Yellow
Write-Host "  ✅ Modal com 9 tipos de sensores:" -ForegroundColor Green
Write-Host "     📡 SNMP Genérico" -ForegroundColor White
Write-Host "     📶 Access Point WiFi" -ForegroundColor White
Write-Host "     ☁️ Microsoft Azure" -ForegroundColor White
Write-Host "     🌡️ Temperatura" -ForegroundColor White
Write-Host "     🌐 HTTP/HTTPS" -ForegroundColor White
Write-Host "     💾 Storage/NAS" -ForegroundColor White
Write-Host "     🗄️ Banco de Dados" -ForegroundColor White
Write-Host "     🖨️ Impressora" -ForegroundColor White
Write-Host "     🔋 UPS/Nobreak" -ForegroundColor White
Write-Host ""
Write-Host "5. Clique em qualquer tipo (ex: Access Point WiFi)" -ForegroundColor White
Write-Host ""
Write-Host "DEVE ACONTECER:" -ForegroundColor Yellow
Write-Host "  ✅ Redirecionar para Biblioteca de Sensores" -ForegroundColor Green
Write-Host "  ✅ Categoria pré-selecionada (ex: access_point)" -ForegroundColor Green
Write-Host "  ✅ Modal de adicionar sensor abre automaticamente" -ForegroundColor Green
Write-Host ""
Write-Host "=== TESTE COMPLETO ===" -ForegroundColor Green
