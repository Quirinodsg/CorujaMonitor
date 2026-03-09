@echo off
REM ========================================
REM INSTALADOR COMPLETO CORUJA MONITOR PROBE
REM Instala Python + Dependencias + Probe
REM ========================================

echo.
echo ========================================
echo   CORUJA MONITOR PROBE - INSTALACAO COMPLETA
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

echo Este instalador vai:
echo   1. Instalar Python 3.11 (se necessario)
echo   2. Instalar dependencias Python
echo   3. Copiar arquivos da Probe
echo   4. Configurar firewall
echo   5. Criar atalhos
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM PASSO 1: VERIFICAR/INSTALAR PYTHON
REM ========================================
echo.
echo [1/7] Verificando Python...

python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python ja instalado
    python --version
    goto :install_deps
)

echo    [AVISO] Python nao encontrado
echo    [INFO] Instalando Python 3.11...
echo.

REM Verificar se o instalador Python existe
if not exist "python-3.11.8-amd64.exe" (
    echo    [INFO] Baixando Python 3.11.8...
    echo    Aguarde, isso pode demorar alguns minutos...
    echo.
    
    REM Tentar baixar com PowerShell
    powershell -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Baixando de python.org...'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-3.11.8-amd64.exe' -UseBasicParsing; Write-Host 'Download concluido!'}"
    
    if not exist "python-3.11.8-amd64.exe" (
        echo    [ERRO] Falha ao baixar Python!
        echo.
        echo    SOLUCAO:
        echo    1. Baixe manualmente: https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
        echo    2. Coloque o arquivo nesta pasta
        echo    3. Execute este instalador novamente
        echo.
        pause
        exit /b 1
    )
    echo    [OK] Download concluido
)

echo.
echo    [INFO] Instalando Python 3.11.8...
echo    Aguarde, isso pode demorar 2-5 minutos...
echo    NAO FECHE ESTA JANELA!
echo.

REM Instalar Python com log
start /wait python-3.11.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 /log python_install.log

echo    [INFO] Aguardando conclusao da instalacao...
timeout /t 10 /nobreak >nul

REM Atualizar PATH
set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
set "PATH=%PATH%;C:\Program Files\Python311\python.exe"

REM Verificar se Python foi instalado
"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python instalado com sucesso!
) else (
    echo    [AVISO] Python pode nao ter sido instalado corretamente
    echo    Verifique o log: python_install.log
    echo.
    echo    Tentando continuar...
)

REM ========================================
REM PASSO 2: INSTALAR DEPENDENCIAS
REM ========================================
:install_deps
echo.
echo [2/7] Instalando dependencias Python...

REM Definir caminho do Python
set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

REM Verificar Python
"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% neq 0 (
    echo    [ERRO] Python nao encontrado!
    echo.
    echo    SOLUCAO:
    echo    1. Instale Python manualmente: https://www.python.org/downloads/
    echo    2. Marque "Add Python to PATH" durante instalacao
    echo    3. Execute este instalador novamente
    echo.
    pause
    exit /b 1
)

echo    [OK] Python encontrado
"%PYTHON_EXE%" --version

REM Atualizar pip
echo    [INFO] Atualizando pip...
"%PYTHON_EXE%" -m pip install --quiet --upgrade pip

REM Instalar dependencias
echo    - psutil (monitoramento sistema)
"%PYTHON_EXE%" -m pip install --quiet psutil

echo    - httpx (comunicacao HTTP)
"%PYTHON_EXE%" -m pip install --quiet httpx

echo    - pywin32 (WMI Windows)
"%PYTHON_EXE%" -m pip install --quiet pywin32

echo    - pysnmp (SNMP)
"%PYTHON_EXE%" -m pip install --quiet pysnmp

echo    - pyyaml (configuracao)
"%PYTHON_EXE%" -m pip install --quiet pyyaml

echo    [OK] Dependencias instaladas!

REM ========================================
REM PASSO 3: COPIAR ARQUIVOS
REM ========================================
echo.
echo [3/7] Copiando arquivos da Probe...

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

REM Criar diretorios
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

REM Copiar arquivos Python
xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

REM Copiar scripts BAT
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1

REM Copiar documentacao
xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.md" "%INSTALL_DIR%\" >nul 2>&1

echo    [OK] Arquivos copiados para: %INSTALL_DIR%

REM ========================================
REM PASSO 4: CONFIGURAR FIREWALL
REM ========================================
echo.
echo [4/7] Configurando firewall (WMI)...

netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

if %errorLevel% equ 0 (
    echo    [OK] Firewall configurado
) else (
    echo    [AVISO] Nao foi possivel configurar firewall
)

REM ========================================
REM PASSO 5: CRIAR ATALHOS
REM ========================================
echo.
echo [5/7] Criando atalhos...

REM Atalho Menu Iniciar - Configurar
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Configurar conexao com servidor'; $Shortcut.Save()" >nul 2>&1

REM Atalho Menu Iniciar - Instalar Servico
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Instalar Servico Coruja.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\install.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Instalar probe como servico Windows'; $Shortcut.Save()" >nul 2>&1

REM Atalho Desktop (todos os usuários)
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%PUBLIC%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Configurar Coruja Monitor Probe'; $Shortcut.Save()" >nul 2>&1

REM Atalho Desktop (usuário atual)
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Configurar Coruja Monitor Probe'; $Shortcut.Save()" >nul 2>&1

echo    [OK] Atalhos criados

REM ========================================
REM PASSO 6: REGISTRAR INSTALACAO
REM ========================================
echo.
echo [6/7] Registrando instalacao...

reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.0" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallDate /t REG_SZ /d "%DATE% %TIME%" /f >nul 2>&1

echo    [OK] Instalacao registrada

REM ========================================
REM PASSO 7: VERIFICAR INSTALACAO
REM ========================================
echo.
echo [7/7] Verificando instalacao...

REM Definir caminho do Python
set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

REM Verificar Python
"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python funcionando
    "%PYTHON_EXE%" --version
) else (
    echo    [ERRO] Python nao encontrado
    echo    Instale manualmente: https://www.python.org/downloads/
)

REM Verificar dependencias
"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Dependencias instaladas
) else (
    echo    [AVISO] Algumas dependencias podem estar faltando
    echo    Execute: "%PYTHON_EXE%" -m pip install psutil httpx pywin32 pysnmp pyyaml
)

REM Verificar arquivos
if exist "%INSTALL_DIR%\probe_core.py" (
    echo    [OK] Arquivos da probe instalados
) else (
    echo    [ERRO] Arquivos da probe nao encontrados
)

REM ========================================
REM CONCLUSAO
REM ========================================
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Instalado em: %INSTALL_DIR%
echo.
echo PROXIMOS PASSOS:
echo.
echo 1. CONFIGURAR PROBE:
echo    - Execute: "Configurar Coruja Probe" (atalho no Desktop)
echo    - Digite IP do servidor: 192.168.31.161
echo    - Digite o token da probe
echo.
echo 2. INSTALAR COMO SERVICO (Opcional):
echo    - Execute: "Instalar Servico Coruja" (Menu Iniciar)
echo    - Probe iniciara automaticamente com Windows
echo.
echo 3. VERIFICAR LOGS:
echo    - Pasta: %INSTALL_DIR%\logs
echo.
echo ========================================
echo.
pause
