# Script para configurar a probe BH para coletar dados do sensor de ping
Write-Host "🔧 Configurando Probe BH para Sensor de Ping..." -ForegroundColor Cyan
Write-Host ""

# 1. Parar a probe atual
Write-Host "1️⃣ Parando probe atual..." -ForegroundColor Yellow
$pythonProcess = Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.Id -eq 21116}
if ($pythonProcess) {
    Stop-Process -Id 21116 -Force
    Write-Host "   ✅ Probe parada (PID: 21116)" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "   ⚠️ Probe não está rodando" -ForegroundColor Yellow
}
Write-Host ""

# 2. Backup da configuração atual
Write-Host "2️⃣ Fazendo backup da configuração..." -ForegroundColor Yellow
if (Test-Path "probe/probe_config.json") {
    Copy-Item "probe/probe_config.json" "probe/probe_config.json.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "   ✅ Backup criado" -ForegroundColor Green
}
Write-Host ""

# 3. Criar nova configuração
Write-Host "3️⃣ Criando nova configuração..." -ForegroundColor Yellow
$config = @{
    api_url = "http://192.168.30.189:8000"
    probe_token = "TvQ8v6wdYAIhbtSdciuwbb8CP74LilEOMFSYL-4qWXk"
    collection_interval = 60
    monitored_services = @()
    udm_targets = @(
        @{
            hostname = "DESKTOP-P9VGN04"
            ip_address = "192.168.30.189"
            sensors = @("ping", "cpu", "memory", "disk")
        }
    )
}

$configJson = $config | ConvertTo-Json -Depth 10
Set-Content -Path "probe/probe_config.json" -Value $configJson -Encoding UTF8
Write-Host "   ✅ Configuração atualizada" -ForegroundColor Green
Write-Host ""

# 4. Mostrar nova configuração
Write-Host "4️⃣ Nova configuração:" -ForegroundColor Yellow
Write-Host $configJson -ForegroundColor Gray
Write-Host ""

# 5. Reiniciar probe
Write-Host "5️⃣ Reiniciando probe..." -ForegroundColor Yellow
Write-Host "   Execute manualmente:" -ForegroundColor Gray
Write-Host "   cd probe" -ForegroundColor White
Write-Host "   python probe_core.py" -ForegroundColor White
Write-Host ""

Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Abra um novo terminal" -ForegroundColor White
Write-Host "   2. cd probe" -ForegroundColor White
Write-Host "   3. python probe_core.py" -ForegroundColor White
Write-Host "   4. Aguarde 60 segundos (collection_interval)" -ForegroundColor White
Write-Host "   5. Verifique se o sensor de ping está recebendo dados" -ForegroundColor White
