# ═══════════════════════════════════════════════════════════════
# 🔧 SCRIPT DE TESTE WMI - 192.168.31.110
# ═══════════════════════════════════════════════════════════════
# 
# OBJETIVO: Testar conectividade WMI com servidor remoto
# EXECUTAR: Na SRVSONDA001 como Administrador
# 
# ═══════════════════════════════════════════════════════════════

$hostname = "192.168.31.110"

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔧 TESTE WMI - $hostname" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Solicitar credenciais
Write-Host "Digite as credenciais do servidor $hostname" -ForegroundColor Yellow
Write-Host "Usuário: Administrator (ou $hostname\Administrator)" -ForegroundColor Gray
$cred = Get-Credential -Message "Credenciais do $hostname"

if (-not $cred) {
    Write-Host "❌ Credenciais não fornecidas. Abortando." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 INICIANDO TESTES..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════
# TESTE 1: Sistema Operacional
# ═══════════════════════════════════════════════════════════════
Write-Host "📊 [1/4] Testando Sistema Operacional..." -ForegroundColor Yellow

try {
    $os = Get-WmiObject -Class Win32_OperatingSystem `
      -ComputerName $hostname `
      -Credential $cred `
      -ErrorAction Stop
    
    Write-Host "✅ SUCESSO!" -ForegroundColor Green
    Write-Host "   Sistema: $($os.Caption)" -ForegroundColor Gray
    Write-Host "   Versão: $($os.Version)" -ForegroundColor Gray
    Write-Host "   Arquitetura: $($os.OSArchitecture)" -ForegroundColor Gray
    Write-Host "   Hostname: $($os.CSName)" -ForegroundColor Gray
    
    # Calcular uptime
    $bootTime = $os.ConvertToDateTime($os.LastBootUpTime)
    $uptime = (Get-Date) - $bootTime
    Write-Host "   Uptime: $($uptime.Days) dias, $($uptime.Hours) horas" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "POSSÍVEIS CAUSAS:" -ForegroundColor Yellow
    Write-Host "1. TrustedHosts não configurado na SRVSONDA001" -ForegroundColor Gray
    Write-Host "2. PSRemoting não habilitado no $hostname" -ForegroundColor Gray
    Write-Host "3. Firewall WMI bloqueado no $hostname" -ForegroundColor Gray
    Write-Host "4. Credenciais incorretas" -ForegroundColor Gray
    Write-Host ""
    Write-Host "SOLUÇÃO:" -ForegroundColor Yellow
    Write-Host "Execute: Set-Item WSMan:\localhost\Client\TrustedHosts -Value '192.168.31.*' -Force" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# TESTE 2: CPU
# ═══════════════════════════════════════════════════════════════
Write-Host "📊 [2/4] Testando CPU..." -ForegroundColor Yellow

try {
    $cpu = Get-WmiObject -Class Win32_Processor `
      -ComputerName $hostname `
      -Credential $cred `
      -ErrorAction Stop
    
    Write-Host "✅ SUCESSO!" -ForegroundColor Green
    Write-Host "   CPU: $($cpu.Name)" -ForegroundColor Gray
    Write-Host "   Cores Lógicos: $($cpu.NumberOfLogicalProcessors)" -ForegroundColor Gray
    Write-Host "   Cores Físicos: $($cpu.NumberOfCores)" -ForegroundColor Gray
    Write-Host "   Uso Atual: $($cpu.LoadPercentage)%" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════
# TESTE 3: Memória
# ═══════════════════════════════════════════════════════════════
Write-Host "📊 [3/4] Testando Memória..." -ForegroundColor Yellow

try {
    $mem = Get-WmiObject -Class Win32_OperatingSystem `
      -ComputerName $hostname `
      -Credential $cred `
      -ErrorAction Stop
    
    $totalGB = [math]::Round($mem.TotalVisibleMemorySize/1MB, 2)
    $freeGB = [math]::Round($mem.FreePhysicalMemory/1MB, 2)
    $usedGB = $totalGB - $freeGB
    $usedPercent = [math]::Round(($usedGB / $totalGB) * 100, 1)
    
    Write-Host "✅ SUCESSO!" -ForegroundColor Green
    Write-Host "   Memória Total: $totalGB GB" -ForegroundColor Gray
    Write-Host "   Memória Usada: $usedGB GB ($usedPercent%)" -ForegroundColor Gray
    Write-Host "   Memória Livre: $freeGB GB" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════
# TESTE 4: Discos
# ═══════════════════════════════════════════════════════════════
Write-Host "📊 [4/4] Testando Discos..." -ForegroundColor Yellow

try {
    $disks = Get-WmiObject -Class Win32_LogicalDisk `
      -ComputerName $hostname `
      -Credential $cred `
      -Filter "DriveType=3" `
      -ErrorAction Stop
    
    Write-Host "✅ SUCESSO!" -ForegroundColor Green
    
    foreach ($disk in $disks) {
        $sizeGB = [math]::Round($disk.Size/1GB, 2)
        $freeGB = [math]::Round($disk.FreeSpace/1GB, 2)
        $usedGB = $sizeGB - $freeGB
        $usedPercent = [math]::Round(($usedGB / $sizeGB) * 100, 1)
        
        $volumeName = if ($disk.VolumeName) { $disk.VolumeName } else { "Sem Nome" }
        
        Write-Host ""
        Write-Host "   Disco: $($disk.DeviceID)" -ForegroundColor Cyan
        Write-Host "   Nome: $volumeName" -ForegroundColor Gray
        Write-Host "   Total: $sizeGB GB" -ForegroundColor Gray
        Write-Host "   Usado: $usedGB GB ($usedPercent%)" -ForegroundColor Gray
        Write-Host "   Livre: $freeGB GB" -ForegroundColor Gray
    }
    Write-Host ""
    
} catch {
    Write-Host "❌ FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════
# TESTE 5: Serviços (Opcional)
# ═══════════════════════════════════════════════════════════════
Write-Host "📊 [EXTRA] Testando Serviços..." -ForegroundColor Yellow

try {
    # Testar alguns serviços importantes
    $services = @("WinRM", "W32Time", "Spooler", "MSSQLSERVER")
    
    foreach ($serviceName in $services) {
        try {
            $service = Get-WmiObject -Class Win32_Service `
              -ComputerName $hostname `
              -Credential $cred `
              -Filter "Name='$serviceName'" `
              -ErrorAction SilentlyContinue
            
            if ($service) {
                $status = if ($service.State -eq "Running") { "✅" } else { "⚠️" }
                Write-Host "   $status $($service.DisplayName): $($service.State)" -ForegroundColor Gray
            }
        } catch {
            # Ignorar erros de serviços não encontrados
        }
    }
    Write-Host ""
    
} catch {
    Write-Host "⚠️ Não foi possível listar serviços" -ForegroundColor Yellow
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ═══════════════════════════════════════════════════════════════
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ TESTE CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Configurar credenciais no frontend (futuro)" -ForegroundColor Gray
Write-Host "2. Probe Python vai usar as mesmas credenciais" -ForegroundColor Gray
Write-Host "3. Métricas serão coletadas automaticamente" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "- Guarde as credenciais usadas neste teste" -ForegroundColor Gray
Write-Host "- Elas serão necessárias para configurar no sistema" -ForegroundColor Gray
Write-Host ""
