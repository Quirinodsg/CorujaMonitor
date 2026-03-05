# Instalação Coruja Probe com Usuário do Active Directory
# Execute como Administrador

param(
    [string]$Dominio = "SEU_DOMINIO",
    [string]$Usuario = "coruja.monitor",
    [string]$ApiUrl = "http://192.168.31.161:8000",
    [string]$ProbeToken = ""
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACAO CORUJA PROBE - USUARIO AD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está rodando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERRO: Execute este script como Administrador!" -ForegroundColor Red
    Write-Host "Clique direito no arquivo e selecione 'Executar como administrador'" -ForegroundColor Yellow
    pause
    exit 1
}

# Solicitar informações se não foram fornecidas
if ($Dominio -eq "SEU_DOMINIO") {
    $Dominio = Read-Host "Digite o nome do dominio (ex: EMPRESA ou empresa.local)"
}

if ($ProbeToken -eq "") {
    Write-Host ""
    Write-Host "Para obter o token da probe:" -ForegroundColor Yellow
    Write-Host "1. Acesse: http://192.168.31.161:3000" -ForegroundColor White
    Write-Host "2. Va em: Gerenciamento -> Empresas" -ForegroundColor White
    Write-Host "3. Expanda a empresa e clique em '+ Nova Probe'" -ForegroundColor White
    Write-Host "4. Copie o token gerado" -ForegroundColor White
    Write-Host ""
    $ProbeToken = Read-Host "Digite o token da probe"
}

Write-Host ""
$Senha = Read-Host "Digite a senha do usuario $Dominio\$Usuario" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Senha)
$SenhaTexto = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host ""
Write-Host "Configuracao:" -ForegroundColor Cyan
Write-Host "  Dominio: $Dominio" -ForegroundColor White
Write-Host "  Usuario: $Usuario" -ForegroundColor White
Write-Host "  API URL: $ApiUrl" -ForegroundColor White
Write-Host "  Token: $($ProbeToken.Substring(0, 10))..." -ForegroundColor White
Write-Host ""
$confirm = Read-Host "Confirma a instalacao? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Instalacao cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# 1. Criar diretórios
Write-Host "[1/7] Criando diretorios..." -ForegroundColor Yellow
$probeDir = "C:\Program Files\CorujaMonitor\Probe"
$collectorsDir = "$probeDir\collectors"
$logsDir = "$probeDir\logs"

New-Item -ItemType Directory -Path $probeDir -Force | Out-Null
New-Item -ItemType Directory -Path $collectorsDir -Force | Out-Null
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
Write-Host "   OK - Diretorios criados" -ForegroundColor Green

# 2. Verificar Python
Write-Host "[2/7] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   OK - $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERRO - Python nao encontrado!" -ForegroundColor Red
    Write-Host "   Instale Python 3.8+ de: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

# 3. Copiar arquivos (se existirem no diretório atual)
Write-Host "[3/7] Copiando arquivos da probe..." -ForegroundColor Yellow
if (Test-Path ".\probe\probe_core.py") {
    Copy-Item ".\probe\*.py" -Destination $probeDir -Force
    Copy-Item ".\probe\requirements.txt" -Destination $probeDir -Force
    Copy-Item ".\probe\collectors\*.py" -Destination $collectorsDir -Force
    Write-Host "   OK - Arquivos copiados" -ForegroundColor Green
} else {
    Write-Host "   AVISO - Arquivos da probe nao encontrados no diretorio atual" -ForegroundColor Yellow
    Write-Host "   Certifique-se de copiar manualmente:" -ForegroundColor Yellow
    Write-Host "   - probe_core.py" -ForegroundColor White
    Write-Host "   - config.py" -ForegroundColor White
    Write-Host "   - requirements.txt" -ForegroundColor White
    Write-Host "   - collectors/*.py" -ForegroundColor White
}

# 4. Criar config.py
Write-Host "[4/7] Configurando credenciais AD..." -ForegroundColor Yellow
$configContent = @"
# Configuracao Coruja Monitor Probe
# Gerado automaticamente em $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")

# Credenciais do Active Directory para monitoramento WMI
WMI_CONFIG = {
    'domain': '$Dominio',
    'username': '$Usuario',
    'password': '$SenhaTexto',
    'use_domain_user': True
}

# URL da API do Coruja Monitor
API_URL = '$ApiUrl'

# Token da probe (obtido no dashboard)
PROBE_TOKEN = '$ProbeToken'

# Intervalo de coleta em segundos
COLLECTION_INTERVAL = 60

# Nivel de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = 'INFO'

# Auto-start habilitado
AUTO_START = True
"@
$configContent | Out-File -FilePath "$probeDir\config.py" -Encoding UTF8
Write-Host "   OK - Configuracao criada" -ForegroundColor Green

# 5. Instalar dependências Python
Write-Host "[5/7] Instalando dependencias Python..." -ForegroundColor Yellow
if (Test-Path "$probeDir\requirements.txt") {
    Set-Location $probeDir
    pip install -r requirements.txt --quiet
    Write-Host "   OK - Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "   AVISO - requirements.txt nao encontrado" -ForegroundColor Yellow
}

# 6. Configurar Task Scheduler com usuário AD
Write-Host "[6/7] Configurando auto-start com usuario AD..." -ForegroundColor Yellow
$taskCommand = "cmd /c cd /d `"$probeDir`" && python probe_core.py"
$taskUser = "$Dominio\$Usuario"

# Remover task existente se houver
schtasks /delete /tn "CorujaMonitorProbe" /f 2>$null | Out-Null

# Criar nova task
$result = schtasks /create /tn "CorujaMonitorProbe" `
  /tr $taskCommand `
  /sc onstart `
  /delay 0000:30 `
  /rl highest `
  /ru $taskUser `
  /rp $SenhaTexto `
  /f 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK - Task Scheduler configurado" -ForegroundColor Green
} else {
    Write-Host "   ERRO - Falha ao configurar Task Scheduler" -ForegroundColor Red
    Write-Host "   $result" -ForegroundColor Yellow
}

# 7. Iniciar probe
Write-Host "[7/7] Iniciando probe..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
schtasks /run /tn "CorujaMonitorProbe" | Out-Null
Start-Sleep -Seconds 3

# Verificar se iniciou
$process = Get-Process python -ErrorAction SilentlyContinue
if ($process) {
    Write-Host "   OK - Probe iniciada (PID: $($process.Id))" -ForegroundColor Green
} else {
    Write-Host "   AVISO - Probe pode nao ter iniciado" -ForegroundColor Yellow
}

# Limpar senha da memória
$SenhaTexto = $null
[System.GC]::Collect()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Probe configurada com usuario: $taskUser" -ForegroundColor Cyan
Write-Host ""
Write-Host "VERIFICAR STATUS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Task Scheduler:" -ForegroundColor White
Write-Host "   schtasks /query /tn `"CorujaMonitorProbe`"" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Processo rodando:" -ForegroundColor White
Write-Host "   tasklist | findstr python" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Logs:" -ForegroundColor White
Write-Host "   type `"$logsDir\probe.log`"" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Dashboard:" -ForegroundColor White
Write-Host "   $ApiUrl" -ForegroundColor Gray
Write-Host "   Gerenciamento -> Probes" -ForegroundColor Gray
Write-Host ""
Write-Host "ARQUIVOS IMPORTANTES:" -ForegroundColor Yellow
Write-Host "  Config: $probeDir\config.py" -ForegroundColor White
Write-Host "  Logs: $logsDir\probe.log" -ForegroundColor White
Write-Host ""
Write-Host "TESTAR REBOOT:" -ForegroundColor Yellow
Write-Host "  shutdown /r /t 60" -ForegroundColor White
Write-Host "  (Aguardar 1-2 minutos apos reboot e verificar se probe voltou)" -ForegroundColor Gray
Write-Host ""

pause
