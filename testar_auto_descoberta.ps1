# Script para testar auto-descoberta de IP
Write-Host "🔍 Testando Auto-Descoberta de IP do Servidor API" -ForegroundColor Cyan

# 1. Parar probe atual
Write-Host "`n1️⃣ Parando probe atual..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null
Start-Sleep -Seconds 2

# 2. Simular mudança de IP (colocar IP inválido)
Write-Host "2️⃣ Simulando mudança de IP (configurando IP inválido)..." -ForegroundColor Yellow
$configPath = "probe/probe_config.json"
$config = Get-Content $configPath | ConvertFrom-Json
$oldUrl = $config.api_url
$config.api_url = "http://192.168.999.999:8000"  # IP inválido
$config | ConvertTo-Json | Set-Content $configPath
Write-Host "   IP alterado de $oldUrl para $($config.api_url)" -ForegroundColor Gray

# 3. Iniciar probe (deve auto-descobrir o IP correto)
Write-Host "3️⃣ Iniciando probe com auto-descoberta..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd probe; python probe_core.py" -WindowStyle Normal

Write-Host "`n⏳ Aguardando 10 segundos para auto-descoberta..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 4. Verificar se o IP foi corrigido
Write-Host "4️⃣ Verificando configuração atualizada..." -ForegroundColor Yellow
$configUpdated = Get-Content $configPath | ConvertFrom-Json
Write-Host "   IP atual: $($configUpdated.api_url)" -ForegroundColor Cyan

if ($configUpdated.api_url -ne "http://192.168.999.999:8000") {
    Write-Host "`n✅ Auto-descoberta funcionou!" -ForegroundColor Green
    Write-Host "   IP foi automaticamente corrigido para: $($configUpdated.api_url)" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Auto-descoberta não atualizou o IP" -ForegroundColor Yellow
    Write-Host "   Verifique se o servidor API está rodando" -ForegroundColor Yellow
}

Write-Host "`n📊 Logs da probe:" -ForegroundColor Cyan
Write-Host "   Verifique a janela da probe para ver o processo de auto-descoberta" -ForegroundColor Gray
