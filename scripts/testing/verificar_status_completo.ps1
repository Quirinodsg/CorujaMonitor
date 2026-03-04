Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACAO DE STATUS COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar probe rodando
Write-Host "[1] Status da Probe:" -ForegroundColor Yellow
$probe = Get-Process python -ErrorAction SilentlyContinue
if ($probe) {
    $runtime = (Get-Date) - $probe.StartTime
    Write-Host "  ✅ Probe rodando (PID: $($probe.Id))" -ForegroundColor Green
    Write-Host "  ⏱️  Tempo: $($runtime.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
} else {
    Write-Host "  ❌ Probe NÃO está rodando!" -ForegroundColor Red
}

# 2. Verificar última métrica no banco
Write-Host ""
Write-Host "[2] Última Métrica (PING):" -ForegroundColor Yellow
$result = docker-compose exec -T api python -c "from database import SessionLocal; from models import Metric, Sensor; db = SessionLocal(); s = db.query(Sensor).filter(Sensor.sensor_type=='ping').first(); m = db.query(Metric).filter(Metric.sensor_id==s.id).order_by(Metric.timestamp.desc()).first(); print(f'{m.value}|{m.status}|{m.timestamp}')" 2>$null
if ($result) {
    $parts = $result.Split('|')
    Write-Host "  Valor: $($parts[0]) ms" -ForegroundColor White
    Write-Host "  Status: $($parts[1])" -ForegroundColor White
    Write-Host "  Timestamp: $($parts[2])" -ForegroundColor White
    
    # Verificar se é recente (últimos 5 minutos)
    try {
        $timestamp = [DateTime]::Parse($parts[2])
        $diff = (Get-Date) - $timestamp
        if ($diff.TotalMinutes -lt 5) {
            Write-Host "  ✅ Métrica RECENTE (há $([int]$diff.TotalMinutes) minutos)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Métrica ANTIGA (há $([int]$diff.TotalMinutes) minutos)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ⚠️  Não foi possível verificar idade da métrica" -ForegroundColor Yellow
    }
}

# 3. Verificar incidentes ativos
Write-Host ""
Write-Host "[3] Incidentes Ativos:" -ForegroundColor Yellow
$incidents = docker-compose exec -T api python -c "from database import SessionLocal; from models import Incident; db = SessionLocal(); incidents = db.query(Incident).filter(Incident.status.in_(['open','acknowledged'])).all(); print(len(incidents)); [print(f'{i.id}|{i.title}|{i.status}|{i.severity}') for i in incidents]" 2>$null
$lines = $incidents -split "`n" | Where-Object { $_ -match '\S' }
$count = $lines[0]
Write-Host "  Total: $count incidentes" -ForegroundColor White
if ([int]$count -gt 0) {
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $parts = $lines[$i].Split('|')
        if ($parts.Count -ge 4) {
            Write-Host "  - ID $($parts[0]): $($parts[1])" -ForegroundColor Yellow
            Write-Host "    Status: $($parts[2]) | Severidade: $($parts[3])" -ForegroundColor Gray
        }
    }
}

# 4. Verificar containers Docker
Write-Host ""
Write-Host "[4] Containers Docker:" -ForegroundColor Yellow
$containers = docker-compose ps --format "{{.Name}}|{{.Status}}" 2>$null
foreach ($line in $containers) {
    $parts = $line.Split('|')
    if ($parts[1] -match "Up") {
        Write-Host "  ✅ $($parts[0]): $($parts[1])" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($parts[0]): $($parts[1])" -ForegroundColor Red
    }
}

# 5. Verificar logs recentes da API
Write-Host ""
Write-Host "[5] Logs Recentes da API (últimas 5 linhas):" -ForegroundColor Yellow
$apiLogs = docker-compose logs --tail=5 api 2>$null | Select-Object -Last 5
foreach ($log in $apiLogs) {
    if ($log -match "POST /api/v1/metrics") {
        Write-Host "  ✅ $log" -ForegroundColor Green
    } elseif ($log -match "ERROR") {
        Write-Host "  ❌ $log" -ForegroundColor Red
    } else {
        Write-Host "  $log" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DIAGNOSTICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Diagnóstico
if (-not $probe) {
    Write-Host "❌ PROBLEMA: Probe não está rodando!" -ForegroundColor Red
    Write-Host "   Solução: Execute 'python probe\probe_core.py'" -ForegroundColor Yellow
} elseif ($result -and $parts[2] -match "2026-02-25") {
    Write-Host "⚠️  PROBLEMA: Métricas não estão sendo enviadas!" -ForegroundColor Yellow
    Write-Host "   A probe está rodando mas não está enviando dados" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Possíveis causas:" -ForegroundColor Cyan
    Write-Host "   1. Probe conectando no IP errado" -ForegroundColor White
    Write-Host "   2. API não está recebendo as métricas" -ForegroundColor White
    Write-Host "   3. Erro na probe (verifique o terminal)" -ForegroundColor White
    Write-Host ""
    Write-Host "   Solução:" -ForegroundColor Cyan
    Write-Host "   1. Verifique o terminal da probe" -ForegroundColor White
    Write-Host "   2. Procure por erros ou 'Connection timeout'" -ForegroundColor White
    Write-Host "   3. Confirme que está conectando em 192.168.0.41:8000" -ForegroundColor White
} elseif ([int]$count -gt 0) {
    Write-Host "⚠️  ATENÇÃO: Há incidentes ativos" -ForegroundColor Yellow
    Write-Host "   Aguarde até 60 segundos para auto-resolução" -ForegroundColor Yellow
} else {
    Write-Host "✅ TUDO OK: Sistema funcionando normalmente!" -ForegroundColor Green
}

Write-Host ""
