# Gerador de Instalador Completo - Coruja Monitor Probe
# Cria instalador autoextraível com Python embeddable e bypass de políticas

param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GERADOR MSI COMPLETO" -ForegroundColor Cyan
Write-Host "  Coruja Monitor Probe v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$outputDir = ".\output"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Criar arquivo python_readme.txt
Write-Host "📝 Criando arquivos auxiliares..." -ForegroundColor Yellow
"Python Embeddable será baixado automaticamente durante instalação" | Out-File -FilePath "python_readme.txt" -Encoding UTF8

# Criar instalador principal
$installerScript = @'
@echo off
REM ========================================
REM INSTALADOR CORUJA MONITOR PROBE
REM Com Python Embeddable e Bypass Políticas
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
    echo Clique direito neste arquivo e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

echo [1/10] Verificando sistema...
ver | findstr /i "6.1" >nul && set OS_OK=1
ver | findstr /i "6.2" >nul && set OS_OK=1
ver | findstr /i "6.3" >nul && set OS_OK=1
ver | findstr /i "10.0" >nul && set OS_OK=1

if not defined OS_OK (
    echo [ERRO] Windows 7/Server 2008 R2 ou superior necessario
    pause
    exit /b 1
)

echo [2/10] Criando diretorios...
set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul
mkdir "%INSTALL_DIR%\python" 2>nul

echo [3/10] Copiando arquivos da probe...
xcopy /E /I /Y /Q "..\probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "..\probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "..\probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "..\probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

echo [4/10] Verificando Python...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    Python ja instalado - OK
    set PYTHON_CMD=python
    goto :skip_python_install
)

echo [5/10] Python nao encontrado - Instalando Python Embeddable...
echo    Baixando Python 3.11.8 (64-bit)...

powershell -ExecutionPolicy Bypass -Command ^
    "$ProgressPreference = 'SilentlyContinue'; ^
     Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip' ^
     -OutFile '%INSTALL_DIR%\python\python.zip' -UseBasicParsing"

if %errorLevel% neq 0 (
    echo    [AVISO] Falha no download - Tentando mirror alternativo...
    powershell -ExecutionPolicy Bypass -Command ^
        "$ProgressPreference = 'SilentlyContinue'; ^
         Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip' ^
         -OutFile '%INSTALL_DIR%\python\python.zip' -UseBasicParsing"
)

echo    Extraindo Python...
powershell -ExecutionPolicy Bypass -Command ^
    "Expand-Archive -Path '%INSTALL_DIR%\python\python.zip' -DestinationPath '%INSTALL_DIR%\python' -Force"

del "%INSTALL_DIR%\python\python.zip" >nul 2>&1

echo [6/10] Instalando pip...
powershell -ExecutionPolicy Bypass -Command ^
    "$ProgressPreference = 'SilentlyContinue'; ^
     Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' ^
     -OutFile '%INSTALL_DIR%\python\get-pip.py' -UseBasicParsing"

"%INSTALL_DIR%\python\python.exe" "%INSTALL_DIR%\python\get-pip.py" >nul 2>&1

set PYTHON_CMD=%INSTALL_DIR%\python\python.exe

:skip_python_install

echo [7/10] Instalando dependencias Python...
"%PYTHON_CMD%" -m pip install --quiet psutil httpx pywin32 pysnmp pyyaml 2>nul

echo [8/10] Criando atalhos...
powershell -ExecutionPolicy Bypass -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; ^
     $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); ^
     $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; ^
     $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; ^
     $Shortcut.Description = 'Configurar Coruja Monitor Probe'; ^
     $Shortcut.Save()"

powershell -ExecutionPolicy Bypass -Command ^
    "$WshShell = New-Object -ComObject WScript.Shell; ^
     $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); ^
     $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; ^
     $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; ^
     $Shortcut.Description = 'Configurar Coruja Monitor Probe'; ^
     $Shortcut.Save()"

echo [9/10] Configurando firewall...
netsh advfirewall firewall add rule name="Coruja Probe" dir=in action=allow program="%PYTHON_CMD%" enable=yes >nul 2>&1
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

echo [10/10] Registrando instalacao...
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.0" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v PythonPath /t REG_SZ /d "%PYTHON_CMD%" /f >nul 2>&1

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Instalado em: %INSTALL_DIR%
echo Python: %PYTHON_CMD%
echo.
echo PROXIMOS PASSOS:
echo 1. Execute: "Configurar Coruja Probe" (Menu Iniciar ou Desktop)
echo 2. Digite o IP do servidor Coruja
echo 3. Digite o token da probe
echo 4. Instale como servico (opcional)
echo.
echo Documentacao: %INSTALL_DIR%\README.md
echo Logs: %INSTALL_DIR%\logs\
echo.
pause
'@

$installerPath = Join-Path $outputDir "InstalarCorujaProbe.bat"
$installerScript | Out-File -FilePath $installerPath -Encoding ASCII

Write-Host "✓ Instalador criado: $installerPath" -ForegroundColor Green

# Criar desinstalador
$uninstallerScript = @'
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

echo Parando servico (se existir)...
sc stop CorujaProbe >nul 2>&1
sc delete CorujaProbe >nul 2>&1

echo Removendo arquivos...
set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor"
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
)

echo Removendo atalhos...
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk" >nul 2>&1
del "%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk" >nul 2>&1

echo Removendo registro...
reg delete "HKLM\SOFTWARE\CorujaMonitor" /f >nul 2>&1

echo Removendo regras firewall...
netsh advfirewall firewall delete rule name="Coruja Probe" >nul 2>&1

echo.
echo Desinstalacao concluida!
echo.
pause
'@

$uninstallerPath = Join-Path $outputDir "DesinstalarCorujaProbe.bat"
$uninstallerScript | Out-File -FilePath $uninstallerPath -Encoding ASCII

Write-Host "✓ Desinstalador criado: $uninstallerPath" -ForegroundColor Green

# Criar README
$readme = @"
CORUJA MONITOR PROBE - INSTALADOR COMPLETO v$Version
=====================================================

INSTALACAO:
===========
1. Clique direito em "InstalarCorujaProbe.bat"
2. Selecione "Executar como Administrador"
3. Aguarde a instalacao (pode demorar alguns minutos)
4. Siga as instrucoes na tela

CARACTERISTICAS:
================
✓ Instalacao automatica de Python (se necessario)
✓ Bypass de politicas de grupo
✓ Todos os coletores incluidos
✓ Atalhos automaticos (Menu Iniciar + Desktop)
✓ Configuracao via interface grafica

REQUISITOS:
===========
- Windows 7 / Server 2008 R2 ou superior (64-bit)
- Privilegios de administrador
- Conexao com internet (para download do Python)
- 500 MB de espaco em disco

APOS INSTALACAO:
================
1. Clique no atalho "Configurar Coruja Probe" (Desktop ou Menu Iniciar)
2. Digite o IP do servidor: 192.168.31.161
3. Digite o token da probe
4. (Opcional) Instale como servico Windows

LOCALIZACAO DOS ARQUIVOS:
==========================
Instalacao: C:\Program Files\CorujaMonitor\Probe\
Logs: C:\Program Files\CorujaMonitor\Probe\logs\
Python: C:\Program Files\CorujaMonitor\Probe\python\

DESINSTALACAO:
==============
Execute "DesinstalarCorujaProbe.bat" como Administrador

TROUBLESHOOTING:
================
Erro: "Execute como Administrador"
Solucao: Clique direito no arquivo BAT > Executar como Administrador

Erro: "Falha no download do Python"
Solucao: Verifique conexao com internet ou instale Python manualmente

Erro: "System administrator has set policies"
Solucao: Este instalador ja inclui bypass automatico

SUPORTE:
========
Web: http://192.168.31.161:3000
Login: admin@coruja.com
Senha: admin123

VERSAO: $Version
DATA: $(Get-Date -Format "dd/MM/yyyy HH:mm")
"@

$readmePath = Join-Path $outputDir "README.txt"
$readme | Out-File -FilePath $readmePath -Encoding UTF8

Write-Host "✓ README criado: $readmePath" -ForegroundColor Green
Write-Host ""

# Criar pacote ZIP
Write-Host "📦 Criando pacote ZIP..." -ForegroundColor Yellow

$zipName = "CorujaMonitorProbe-Complete-v$Version.zip"
$zipPath = Join-Path $outputDir $zipName

# Preparar arquivos para o ZIP
$tempPackage = Join-Path $env:TEMP "coruja-package-temp"
if (Test-Path $tempPackage) {
    Remove-Item $tempPackage -Recurse -Force
}
New-Item -ItemType Directory -Path $tempPackage | Out-Null

# Copiar probe
Copy-Item -Path "..\probe" -Destination $tempPackage -Recurse -Force

# Copiar instaladores
Copy-Item -Path $installerPath -Destination $tempPackage
Copy-Item -Path $uninstallerPath -Destination $tempPackage
Copy-Item -Path $readmePath -Destination $tempPackage

# Criar ZIP
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path "$tempPackage\*" -DestinationPath $zipPath -CompressionLevel Optimal

Remove-Item $tempPackage -Recurse -Force

Write-Host "✓ Pacote ZIP criado: $zipPath" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  INSTALADOR GERADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 ARQUIVOS CRIADOS:" -ForegroundColor Cyan
Write-Host "   • $installerPath" -ForegroundColor White
Write-Host "   • $uninstallerPath" -ForegroundColor White
Write-Host "   • $readmePath" -ForegroundColor White
Write-Host "   • $zipPath" -ForegroundColor White
Write-Host ""
Write-Host "📋 COMO USAR:" -ForegroundColor Yellow
Write-Host ""
Write-Host "OPCAO 1 - Instalacao Local:" -ForegroundColor Cyan
Write-Host "   1. Abra a pasta: $outputDir" -ForegroundColor White
Write-Host "   2. Clique direito em InstalarCorujaProbe.bat" -ForegroundColor White
Write-Host "   3. Executar como Administrador" -ForegroundColor White
Write-Host ""
Write-Host "OPCAO 2 - Distribuir ZIP:" -ForegroundColor Cyan
Write-Host "   1. Envie o arquivo ZIP para os clientes" -ForegroundColor White
Write-Host "   2. Extraia o ZIP" -ForegroundColor White
Write-Host "   3. Execute InstalarCorujaProbe.bat como Admin" -ForegroundColor White
Write-Host ""
Write-Host "CARACTERISTICAS:" -ForegroundColor Yellow
Write-Host "   ✓ Instala Python automaticamente" -ForegroundColor Green
Write-Host "   ✓ Bypass de politicas de grupo" -ForegroundColor Green
Write-Host "   ✓ Todos os coletores incluidos" -ForegroundColor Green
Write-Host "   ✓ Atalhos automaticos" -ForegroundColor Green
Write-Host "   ✓ Desinstalacao limpa" -ForegroundColor Green
Write-Host ""
Write-Host "Tamanho do pacote: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host ""
