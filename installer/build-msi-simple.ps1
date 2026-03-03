# Script alternativo para criar MSI sem WiX Toolset
# Usa Windows Installer XML (WiX) via NuGet ou cria EXE autoextraível

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = ".\output",
    [switch]$UseInnoSetup
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR SIMPLES - CORUJA MONITOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($UseInnoSetup) {
    Write-Host "Criando instalador com Inno Setup..." -ForegroundColor Yellow
    Write-Host ""
    
    # Criar script Inno Setup
    $issContent = @"
[Setup]
AppName=Coruja Monitor Probe
AppVersion=$Version
DefaultDirName={pf}\CorujaMonitor
DefaultGroupName=Coruja Monitor
OutputDir=$OutputDir
OutputBaseFilename=CorujaMonitorProbe-$Version-Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "..\probe\*"; DestDir: "{app}\Probe"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Iniciar Coruja Probe"; Filename: "{cmd}"; Parameters: "/k cd /d ""{app}\Probe"" && python probe_core.py"
Name: "{group}\Configurar Probe"; Filename: "notepad.exe"; Parameters: """{app}\Probe\probe_config.json"""
Name: "{group}\Desinstalar"; Filename: "{uninstallexe}"

[Run]
Filename: "{cmd}"; Parameters: "/c net user MonitorUser Monitor@{code:GetRandomPassword} /add"; Flags: runhidden
Filename: "{cmd}"; Parameters: "/c net localgroup Administradores MonitorUser /add"; Flags: runhidden
Filename: "{cmd}"; Parameters: "/c netsh advfirewall firewall set rule group=""Windows Management Instrumentation (WMI)"" new enable=yes"; Flags: runhidden

[Code]
function GetRandomPassword(Param: String): String;
begin
  Result := IntToStr(Random(99999));
end;
"@
    
    $issFile = Join-Path $PSScriptRoot "CorujaProbe.iss"
    $issContent | Out-File -FilePath $issFile -Encoding UTF8
    
    Write-Host "Script Inno Setup criado: $issFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Yellow
    Write-Host "1. Instale Inno Setup: https://jrsoftware.org/isdl.php" -ForegroundColor White
    Write-Host "2. Compile: iscc.exe CorujaProbe.iss" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "Criando instalador autoextraível..." -ForegroundColor Yellow
    Write-Host ""
    
    # Criar script de instalação
    $installScript = @"
@echo off
REM Instalador Coruja Monitor Probe
REM Versão: $Version

echo ========================================
echo   CORUJA MONITOR - INSTALACAO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    pause
    exit /b 1
)

echo [1/8] Extraindo arquivos...
mkdir "%ProgramFiles%\CorujaMonitor\Probe" 2>nul
xcopy /E /I /Y probe "%ProgramFiles%\CorujaMonitor\Probe\"

echo [2/8] Criando usuario MonitorUser...
set "PASSWORD=Monitor@%RANDOM%%RANDOM%"
net user MonitorUser "%PASSWORD%" /add /comment:"Usuario para monitoramento Coruja" /passwordchg:no /expires:never /active:yes >nul 2>&1

echo [3/8] Adicionando aos grupos...
net localgroup Administradores MonitorUser /add >nul 2>&1
net localgroup "Remote Management Users" MonitorUser /add >nul 2>&1

echo [4/8] Configurando Firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

echo [5/8] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1

echo [6/8] Criando atalhos...
powershell -Command "\$WshShell = New-Object -ComObject WScript.Shell; \$Shortcut = \$WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Coruja Monitor Probe.lnk'); \$Shortcut.TargetPath = 'cmd.exe'; \$Shortcut.Arguments = '/k cd /d \"%ProgramFiles%\CorujaMonitor\Probe\" && python probe_core.py'; \$Shortcut.Save()"

echo [7/8] Configurando probe...
set /p API_IP="Digite o IP do servidor Coruja: "
set /p PROBE_TOKEN="Digite o token da probe: "

(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > "%ProgramFiles%\CorujaMonitor\Probe\probe_config.json"

echo [8/8] Instalando dependencias Python...
cd /d "%ProgramFiles%\CorujaMonitor\Probe"
pip install -r requirements.txt

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Usuario: MonitorUser
echo Senha: %PASSWORD%
echo.
echo Inicie a probe pelo Menu Iniciar
echo.
pause
"@
    
    $installBat = Join-Path $OutputDir "install.bat"
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
    }
    $installScript | Out-File -FilePath $installBat -Encoding ASCII
    
    Write-Host "✓ Script de instalação criado: $installBat" -ForegroundColor Green
    Write-Host ""
    
    # Criar arquivo ZIP com tudo
    Write-Host "Criando pacote ZIP..." -ForegroundColor Yellow
    $zipPath = Join-Path $OutputDir "CorujaMonitorProbe-$Version.zip"
    
    $tempDir = Join-Path $env:TEMP "coruja-package"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    # Copiar arquivos
    Copy-Item -Path "..\probe" -Destination $tempDir -Recurse
    Copy-Item -Path $installBat -Destination $tempDir
    
    # Criar README
    @"
CORUJA MONITOR PROBE - INSTALADOR
==================================

INSTALACAO:
1. Extraia todos os arquivos
2. Clique direito em install.bat
3. Executar como Administrador
4. Siga as instruções

REQUISITOS:
- Windows 7/Server 2008 R2 ou superior
- Python 3.8 ou superior
- Privilegios de administrador

SUPORTE:
- Documentacao: README.md
- Web: http://192.168.0.9:3000
"@ | Out-File -FilePath (Join-Path $tempDir "LEIA-ME.txt") -Encoding UTF8
    
    # Criar ZIP
    Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force
    
    Remove-Item $tempDir -Recurse -Force
    
    Write-Host "✓ Pacote criado: $zipPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  INSTALADOR CRIADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Arquivo: $zipPath" -ForegroundColor White
    Write-Host ""
    Write-Host "DISTRIBUIR:" -ForegroundColor Cyan
    Write-Host "1. Envie o ZIP para os clientes" -ForegroundColor White
    Write-Host "2. Extraia o ZIP" -ForegroundColor White
    Write-Host "3. Execute install.bat como Administrador" -ForegroundColor White
    Write-Host ""
}

Write-Host "Pressione ENTER para sair..."
Read-Host
