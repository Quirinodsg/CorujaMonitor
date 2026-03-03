Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIAR PROBE COM DEBUG" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar diretório atual
Write-Host "[1] Diretório Atual:" -ForegroundColor Yellow
Write-Host "  $PWD" -ForegroundColor White

# Verificar arquivo de configuração
Write-Host ""
Write-Host "[2] Arquivo de Configuração:" -ForegroundColor Yellow
if (Test-Path "probe\probe_config.json") {
    Write-Host "  ✅ probe\probe_config.json encontrado" -ForegroundColor Green
    $config = Get-Content "probe\probe_config.json" | ConvertFrom-Json
    Write-Host "  API URL: $($config.api_url)" -ForegroundColor Cyan
    Write-Host "  Token: $($config.probe_token.Substring(0,10))..." -ForegroundColor Cyan
    Write-Host "  Intervalo: $($config.collection_interval)s" -ForegroundColor Cyan
} else {
    Write-Host "  ❌ probe\probe_config.json NÃO encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar probe_core.py
Write-Host ""
Write-Host "[3] Arquivo da Probe:" -ForegroundColor Yellow
if (Test-Path "probe\probe_core.py") {
    Write-Host "  ✅ probe\probe_core.py encontrado" -ForegroundColor Green
} else {
    Write-Host "  ❌ probe\probe_core.py NÃO encontrado!" -ForegroundColor Red
    exit 1
}

# Parar probe antiga se existir
Write-Host ""
Write-Host "[4] Verificando Processos:" -ForegroundColor Yellow
$probe = Get-Process python -ErrorAction SilentlyContinue
if ($probe) {
    Write-Host "  ⚠️  Probe já está rodando (PID: $($probe.Id))" -ForegroundColor Yellow
    Write-Host "  Parando..." -ForegroundColor Yellow
    $probe | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "  ✅ Probe parada" -ForegroundColor Green
} else {
    Write-Host "  ✅ Nenhuma probe rodando" -ForegroundColor Green
}

# Iniciar probe
Write-Host ""
Write-Host "[5] Iniciando Probe:" -ForegroundColor Yellow
Write-Host "  Comando: python probe\probe_core.py" -ForegroundColor Cyan
Write-Host "  Diretório: $PWD" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LOGS DA PROBE (Ctrl+C para parar)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Definir variável de ambiente para forçar caminho do config
$env:PROBE_CONFIG_PATH = "probe\probe_config.json"

# Iniciar probe
python probe\probe_core.py
