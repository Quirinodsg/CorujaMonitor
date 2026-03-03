# Script para testar detecção automática de IP
# 26 FEV 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DE DETECÇÃO AUTOMÁTICA DE IP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar IP da máquina
Write-Host "🔍 Detectando IP da máquina..." -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"} | Select-Object -First 1).IPAddress

if ($ip) {
    Write-Host "✅ IP detectado: $ip" -ForegroundColor Green
} else {
    Write-Host "❌ Não foi possível detectar o IP" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 URLs do Sistema:" -ForegroundColor Cyan
Write-Host "   Frontend: http://${ip}:3000" -ForegroundColor White
Write-Host "   API:      http://${ip}:8000" -ForegroundColor White
Write-Host "   Ollama:   http://${ip}:11434" -ForegroundColor White

Write-Host ""
Write-Host "🧪 Testando conectividade..." -ForegroundColor Yellow

# Testar API
Write-Host "   Testando API..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://${ip}:8000/docs" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅ OK" -ForegroundColor Green
    }
} catch {
    Write-Host " ❌ FALHOU" -ForegroundColor Red
}

# Testar Frontend
Write-Host "   Testando Frontend..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://${ip}:3000" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅ OK" -ForegroundColor Green
    }
} catch {
    Write-Host " ❌ FALHOU" -ForegroundColor Red
}

Write-Host ""
Write-Host "📝 Instruções:" -ForegroundColor Cyan
Write-Host "   1. Abra o navegador" -ForegroundColor White
Write-Host "   2. Acesse: http://${ip}:3000" -ForegroundColor White
Write-Host "   3. Abra o Console (F12)" -ForegroundColor White
Write-Host "   4. Verifique a mensagem:" -ForegroundColor White
Write-Host "      🔧 API URL configurada: http://${ip}:8000" -ForegroundColor Gray
Write-Host "      🌐 Hostname detectado: ${ip}" -ForegroundColor Gray

Write-Host ""
Write-Host "✅ Sistema configurado para detecção automática!" -ForegroundColor Green
Write-Host "   Quando o IP mudar, apenas acesse o novo IP no navegador." -ForegroundColor White
Write-Host "   Não precisa editar código ou reiniciar containers!" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
