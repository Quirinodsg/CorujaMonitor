# Gerar Instalador Coruja Probe - Executar da Raiz do Projeto
# Execute: .\GERAR_INSTALADOR_AGORA.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GERAR INSTALADOR CORUJA PROBE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar caminho correto
$projectRoot = $PSScriptRoot
Write-Host "📁 Diretório do projeto: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Criar pasta output
$outputDir = Join-Path $projectRoot "installer\output"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Host "✓ Pasta output criada" -ForegroundColor Green
}

Write-Host "📝 Gerando instalador..." -ForegroundColor Yellow
Write-Host ""

# Criar instalador BAT
$installerContent = @'
@echo off
REM ========================================
REM INSTALADOR CORUJA MONITOR PROBE v1.0.0
REM ========================================

echo.
echo ========================================
echo   CORUJA MONITOR PROBE - INSTALACAO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique direito e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

echo [1/8] Criando diretorios...
set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

echo [2/8] Copiando arquivos...
xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

echo [3/8] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo    [AVISO] Python nao encontrado!
    echo    Instale Python 3.8+ de: https://www.python.org/downloads/
    echo    Ou continue e instale depois
    pause
)

echo [4/8] Instalando dependencias...
python -m pip install --quiet psutil httpx pywin32 pysnmp pyyaml 2>nul

echo [5/8] Criando atalhos...
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo [6/8] Configurando firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

echo [7/8] Registrando instalacao...
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.0" /f >nul 2>&1

echo [8/8] Concluindo...

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Instalado em: %INSTALL_DIR%
echo.
echo PROXIMOS PASSOS:
echo 1. Configure: "Configurar Coruja Probe" (Desktop)
echo 2. Digite IP do servidor: 192.168.31.161
echo 3. Digite o token da probe
echo 4. Instale como servico (opcional)
echo.
pause
'@

$installerPath = Join-Path $outputDir "InstalarCorujaProbe.bat"
$installerContent | Out-File -FilePath $installerPath -Encoding ASCII

Write-Host "✓ Instalador criado: InstalarCorujaProbe.bat" -ForegroundColor Green

# Criar desinstalador
$uninstallerContent = @'
@echo off
REM Desinstalador Coruja Monitor Probe

echo.
echo ========================================
echo   DESINSTALAR CORUJA MONITOR PROBE
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

echo Parando servico...
sc stop CorujaProbe >nul 2>&1
sc delete CorujaProbe >nul 2>&1

echo Removendo arquivos...
rmdir /s /q "%ProgramFiles%\CorujaMonitor" 2>nul

echo Removendo atalhos...
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk" >nul 2>&1
del "%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1

echo Removendo registro...
reg delete "HKLM\SOFTWARE\CorujaMonitor" /f >nul 2>&1

echo.
echo Desinstalacao concluida!
pause
'@

$uninstallerPath = Join-Path $outputDir "DesinstalarCorujaProbe.bat"
$uninstallerContent | Out-File -FilePath $uninstallerPath -Encoding ASCII

Write-Host "✓ Desinstalador criado: DesinstalarCorujaProbe.bat" -ForegroundColor Green

# Criar README
$readmeContent = @"
CORUJA MONITOR PROBE - INSTALADOR v1.0.0
=========================================

INSTALACAO:
1. Clique direito em "InstalarCorujaProbe.bat"
2. Selecione "Executar como Administrador"
3. Aguarde a instalacao
4. Configure usando o atalho no Desktop

REQUISITOS:
- Windows 7/Server 2008 R2 ou superior
- Python 3.8+ (sera solicitado se nao instalado)
- Privilegios de administrador

APOS INSTALACAO:
1. Clique em "Configurar Coruja Probe" (Desktop)
2. Digite IP: 192.168.31.161
3. Digite token da probe
4. Instale como servico (opcional)

LOCALIZACAO:
C:\Program Files\CorujaMonitor\Probe\

DESINSTALACAO:
Execute "DesinstalarCorujaProbe.bat" como Admin

SUPORTE:
http://192.168.31.161:3000
admin@coruja.com / admin123
"@

$readmePath = Join-Path $outputDir "README.txt"
$readmeContent | Out-File -FilePath $readmePath -Encoding UTF8

Write-Host "✓ README criado: README.txt" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  INSTALADOR GERADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 ARQUIVOS:" -ForegroundColor Cyan
Write-Host "   $outputDir" -ForegroundColor White
Write-Host ""
Write-Host "📋 COMO USAR:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Abra a pasta:" -ForegroundColor White
Write-Host "   explorer `"$outputDir`"" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Clique direito em InstalarCorujaProbe.bat" -ForegroundColor White
Write-Host "3. Executar como Administrador" -ForegroundColor White
Write-Host ""

# Abrir pasta automaticamente
Start-Process explorer.exe -ArgumentList $outputDir

Write-Host "✓ Pasta aberta automaticamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione ENTER para sair..."
Read-Host
