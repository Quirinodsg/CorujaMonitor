Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRECAO COMPLETA DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Parar TODAS as probes Python
Write-Host "[1/6] Parando todas as probes Python..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Stop-Process -Force
    Write-Host "  ✅ $($pythonProcesses.Count) processo(s) Python parado(s)" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "  ℹ️  Nenhum processo Python rodando" -ForegroundColor Gray
}

# Passo 2: Fechar incidentes resolvidos
Write-Host ""
Write-Host "[2/6] Fechando incidentes resolvidos..." -ForegroundColor Yellow
try {
    $result = docker-compose exec -T api python fechar_incidentes_resolvidos.py 2>&1
    $result | Where-Object { $_ -match "Encontrados|Fechando|Fechados|Ainda ativos|incidente" -and $_ -notmatch "DEBUG|httpx|httpcore|Traceback" } | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️  Erro ao fechar incidentes: $_" -ForegroundColor Yellow
}

# Passo 3: Reiniciar worker
Write-Host ""
Write-Host "[3/6] Reiniciando worker..." -ForegroundColor Yellow
docker-compose restart worker 2>&1 | Out-Null
Write-Host "  ✅ Worker reiniciado" -ForegroundColor Green

# Passo 4: Reiniciar API
Write-Host ""
Write-Host "[4/6] Reiniciando API..." -ForegroundColor Yellow
docker-compose restart api 2>&1 | Out-Null
Write-Host "  ✅ API reiniciada" -ForegroundColor Green

# Passo 5: Aguardar serviços
Write-Host ""
Write-Host "[5/6] Aguardando serviços iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "  ✅ Serviços prontos" -ForegroundColor Green

# Passo 6: Iniciar probe correta
Write-Host ""
Write-Host "[6/6] Iniciando probe correta..." -ForegroundColor Yellow
Write-Host "  📍 Diretório: $PWD" -ForegroundColor Cyan
Write-Host "  🔗 API URL: http://192.168.0.41:8000" -ForegroundColor Cyan
Write-Host ""

# Verificar se probe_config.json existe
if (Test-Path "probe\probe_config.json") {
    $config = Get-Content "probe\probe_config.json" | ConvertFrom-Json
    Write-Host "  ✅ Configuração encontrada:" -ForegroundColor Green
    Write-Host "     API URL: $($config.api_url)" -ForegroundColor White
    Write-Host "     Intervalo: $($config.collection_interval)s" -ForegroundColor White
} else {
    Write-Host "  ❌ probe_config.json não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SISTEMA CORRIGIDO!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando probe em 3 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Iniciar probe
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python probe\probe_core.py"

Write-Host ""
Write-Host "✅ Probe iniciada em nova janela!" -ForegroundColor Green
Write-Host ""
Write-Host "Validação:" -ForegroundColor Cyan
Write-Host "1. Verifique a janela da probe - deve conectar em 192.168.0.41:8000" -ForegroundColor White
Write-Host "2. Aguarde 60 segundos para primeira coleta" -ForegroundColor White
Write-Host "3. Acesse http://192.168.0.41:3000 e verifique:" -ForegroundColor White
Write-Host "   - Sensores atualizando (timestamp atual)" -ForegroundColor White
Write-Host "   - Incidentes fechados (0 abertos)" -ForegroundColor White
Write-Host "   - Servidor visível no NOC" -ForegroundColor White
Write-Host ""
