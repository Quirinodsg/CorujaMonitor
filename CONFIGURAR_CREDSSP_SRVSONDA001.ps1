# ========================================
# CONFIGURAR CREDSSP NA SRVSONDA001
# ========================================
# Executar como Administrador na máquina 192.168.31.162

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURANDO CREDSSP PARA WMI REMOTO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar chaves de registro para CredSSP
Write-Host "[1/5] Criando chaves de registro..." -ForegroundColor Yellow

$regPath1 = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CredentialsDelegation"
$regPath2 = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CredentialsDelegation\AllowFreshCredentials"
$regPath3 = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\CredentialsDelegation\AllowFreshCredentialsWhenNTLMOnly"

# Criar paths se não existirem
New-Item -Path $regPath1 -Force | Out-Null
New-Item -Path $regPath2 -Force | Out-Null
New-Item -Path $regPath3 -Force | Out-Null

Write-Host "✅ Chaves criadas" -ForegroundColor Green

# Habilitar delegação
Write-Host "[2/5] Habilitando delegação de credenciais..." -ForegroundColor Yellow

Set-ItemProperty -Path $regPath1 -Name "AllowFreshCredentials" -Value 1 -Type DWord
Set-ItemProperty -Path $regPath1 -Name "AllowFreshCredentialsWhenNTLMOnly" -Value 1 -Type DWord
Set-ItemProperty -Path $regPath1 -Name "ConcatenateDefaults_AllowFresh" -Value 1 -Type DWord
Set-ItemProperty -Path $regPath1 -Name "ConcatenateDefaults_AllowFreshNTLMOnly" -Value 1 -Type DWord

Write-Host "✅ Delegação habilitada" -ForegroundColor Green

# Adicionar servidor específico
Write-Host "[3/5] Adicionando servidor 192.168.31.110..." -ForegroundColor Yellow

Set-ItemProperty -Path $regPath2 -Name "1" -Value "WSMAN/192.168.31.110" -Type String
Set-ItemProperty -Path $regPath3 -Name "1" -Value "WSMAN/192.168.31.110" -Type String

# Adicionar wildcard para flexibilidade
Set-ItemProperty -Path $regPath2 -Name "2" -Value "WSMAN/*" -Type String
Set-ItemProperty -Path $regPath3 -Name "2" -Value "WSMAN/*" -Type String

Write-Host "✅ Servidor adicionado" -ForegroundColor Green

# Aplicar políticas
Write-Host "[4/5] Aplicando políticas..." -ForegroundColor Yellow

gpupdate /force | Out-Null

Write-Host "✅ Políticas aplicadas" -ForegroundColor Green

# Testar conexão
Write-Host "[5/5] Testando conexão CredSSP..." -ForegroundColor Yellow
Write-Host ""

try {
    $password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential('Techbiz\coruja.monitor', $password)
    
    $result = Invoke-Command -ComputerName 192.168.31.110 -Credential $credential -Authentication CredSSP -ScriptBlock { 
        Get-WmiObject Win32_OperatingSystem | Select-Object Caption, Version
    } -ErrorAction Stop
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ SUCESSO! CONEXÃO CREDSSP FUNCIONANDO" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Sistema Operacional: $($result.Caption)" -ForegroundColor Cyan
    Write-Host "Versão: $($result.Version)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Próximo passo: Copiar wmi_remote_collector.py atualizado" -ForegroundColor Yellow
    
} catch {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ ERRO AO TESTAR CONEXÃO" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis soluções:" -ForegroundColor Yellow
    Write-Host "1. Reiniciar a máquina SRVSONDA001" -ForegroundColor White
    Write-Host "2. Verificar se CredSSP está habilitado no servidor .110" -ForegroundColor White
    Write-Host "3. Verificar firewall" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURAÇÃO CONCLUÍDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
