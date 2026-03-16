# ========================================
# CONFIGURAR WINRM NO SERVIDOR .110
# ========================================
# Executar como Administrador no servidor 192.168.31.110 (SRVHVSPRD010)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURANDO WINRM PARA MONITORAMENTO" -ForegroundColor Cyan
Write-Host "Servidor: 192.168.31.110 (SRVHVSPRD010)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Habilitar PSRemoting
Write-Host "[1/8] Habilitando PSRemoting..." -ForegroundColor Yellow
try {
    Enable-PSRemoting -Force -SkipNetworkProfileCheck
    Write-Host "✅ PSRemoting habilitado" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao habilitar PSRemoting: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Adicionar usuário ao grupo Remote Management Users
Write-Host "[2/8] Adicionando usuário ao grupo Remote Management Users..." -ForegroundColor Yellow
try {
    net localgroup "Remote Management Users" "Techbiz\coruja.monitor" /add 2>$null
    Write-Host "✅ Usuário adicionado ao grupo" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Usuário já está no grupo ou erro: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3. Configurar autenticação WinRM
Write-Host "[3/8] Configurando autenticação WinRM..." -ForegroundColor Yellow
try {
    winrm set winrm/config/service/auth '@{Basic="true";Kerberos="true";Negotiate="true";CredSSP="true"}'
    Write-Host "✅ Autenticação configurada" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao configurar autenticação: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Configurar serviço WinRM
Write-Host "[4/8] Configurando serviço WinRM..." -ForegroundColor Yellow
try {
    winrm set winrm/config/service '@{AllowUnencrypted="true"}'
    winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="1024"}'
    Write-Host "✅ Serviço configurado" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao configurar serviço: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Configurar listener HTTP
Write-Host "[5/8] Configurando listener HTTP..." -ForegroundColor Yellow
try {
    # Remover listener existente se houver
    winrm delete winrm/config/listener?Address=*+Transport=HTTP 2>$null
    # Criar novo listener
    winrm create winrm/config/listener?Address=*+Transport=HTTP
    Write-Host "✅ Listener HTTP configurado" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Listener já existe ou erro: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 6. Configurar TrustedHosts
Write-Host "[6/8] Configurando TrustedHosts..." -ForegroundColor Yellow
try {
    Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
    Write-Host "✅ TrustedHosts configurado" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao configurar TrustedHosts: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Configurar Firewall
Write-Host "[7/8] Configurando Firewall..." -ForegroundColor Yellow
try {
    # Remover regra antiga se existir
    Remove-NetFirewallRule -Name "WinRM-HTTP-In-Coruja" -ErrorAction SilentlyContinue
    
    # Criar nova regra
    New-NetFirewallRule -Name "WinRM-HTTP-In-Coruja" `
        -DisplayName "Windows Remote Management (HTTP-In) - Coruja" `
        -Enabled True `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 5985 `
        -Action Allow `
        -Profile Any
    
    Write-Host "✅ Firewall configurado" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao configurar firewall: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Reiniciar serviço WinRM
Write-Host "[8/8] Reiniciando serviço WinRM..." -ForegroundColor Yellow
try {
    Restart-Service WinRM -Force
    Start-Sleep -Seconds 3
    Write-Host "✅ Serviço WinRM reiniciado" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao reiniciar WinRM: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO CONFIGURAÇÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar configuração
Write-Host "Configuração WinRM:" -ForegroundColor Yellow
winrm get winrm/config

Write-Host ""
Write-Host "Listeners ativos:" -ForegroundColor Yellow
winrm enumerate winrm/config/listener

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ CONFIGURAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximo passo:" -ForegroundColor Yellow
Write-Host "1. Testar conexão da SRVSONDA001 (.162)" -ForegroundColor White
Write-Host "2. Reiniciar a probe" -ForegroundColor White
Write-Host ""
