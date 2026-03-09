@echo off
REM ========================================
REM INSTALADOR COMPLETO CORUJA MONITOR PROBE
REM Instala Python + Dependencias + Probe
REM Versao: 1.0.3 - TUDO EM UM
REM ========================================

echo.
echo ========================================
echo   CORUJA MONITOR PROBE
echo   INSTALADOR COMPLETO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique direito neste arquivo e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

:menu
cls
echo.
echo ========================================
echo   CORUJA MONITOR PROBE
echo   INSTALADOR COMPLETO
echo ========================================
echo.
echo Escolha uma opcao:
echo.
echo   1 - Instalacao Completa (Recomendado)
echo   2 - Instalar apenas Python
echo   3 - Instalar apenas Dependencias
echo   4 - Instalar apenas Probe
echo   5 - Verificar Instalacao
echo   0 - Sair
echo.
echo ========================================
echo.
set /p OPCAO="Digite o numero da opcao: "

if "%OPCAO%"=="1" goto :instalacao_completa
if "%OPCAO%"=="2" goto :instalar_python_menu
if "%OPCAO%"=="3" goto :instalar_deps_menu
if "%OPCAO%"=="4" goto :instalar_probe_menu
if "%OPCAO%"=="5" goto :verificar
if "%OPCAO%"=="0" exit /b 0

echo.
echo Opcao invalida! Tente novamente.
timeout /t 2 >nul
goto :menu

REM ========================================
REM OPCAO 1: INSTALACAO COMPLETA
REM ========================================
:instalacao_completa
cls
echo.
echo ========================================
echo   INSTALACAO COMPLETA
echo ========================================
echo.
echo Sera instalado:
echo   1. Python 3.11 (se necessario)
echo   2. Dependencias Python
echo   3. Arquivos da Probe
echo   4. Firewall
echo   5. Atalhos
echo.
echo Tempo estimado: 5-10 minutos
echo.
pause

REM ========================================
REM PASSO 1: PYTHON
REM ========================================
echo.
echo [1/7] Verificando Python...

REM Tentar python no PATH
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python ja instalado no PATH
    python --version
    goto :install_deps
)

REM Tentar Python 3.11 no local padrao
"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python 3.11 encontrado
    "C:\Program Files\Python311\python.exe" --version
    echo    [INFO] Adicionando ao PATH...
    set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
    goto :install_deps
)

REM Tentar Python 3.10
"C:\Program Files\Python310\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python 3.10 encontrado
    "C:\Program Files\Python310\python.exe" --version
    echo    [INFO] Adicionando ao PATH...
    set "PATH=%PATH%;C:\Program Files\Python310;C:\Program Files\Python310\Scripts"
    goto :install_deps
)

echo    [INFO] Python nao encontrado - sera instalado

echo    [INFO] Python nao encontrado
echo    [INFO] Baixando Python 3.11.8...
echo.

if not exist "python-3.11.8-amd64.exe" (
    echo    Baixando de python.org (25 MB)...
    echo    Aguarde 1-3 minutos...
    echo.
    
    powershell -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Write-Host '    Baixando...'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-3.11.8-amd64.exe' -UseBasicParsing -TimeoutSec 300; Write-Host '    Download concluido!' } catch { Write-Host '    Erro no download!' }}"
    
    if not exist "python-3.11.8-amd64.exe" (
        color 0C
        echo.
        echo    ========================================
        echo    [ERRO] Falha ao baixar Python!
        echo    ========================================
        echo.
        echo    SOLUCAO:
        echo    1. Baixe manualmente:
        echo       https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
        echo.
        echo    2. Salve o arquivo nesta pasta:
        echo       %CD%
        echo.
        echo    3. Execute este instalador novamente
        echo.
        echo    ========================================
        echo.
        pause
        exit /b 1
    )
)

echo.
echo    [INFO] Instalando Python 3.11.8...
echo    Aguarde 2-5 minutos...
echo    NAO FECHE ESTA JANELA!
echo.

start /wait python-3.11.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

echo    Aguardando conclusao...
timeout /t 15 /nobreak >nul

set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"

"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python instalado!
    "C:\Program Files\Python311\python.exe" --version
) else (
    color 0E
    echo    [AVISO] Python pode nao ter sido instalado
    echo    Continuando...
)

REM ========================================
REM PASSO 2: DEPENDENCIAS
REM ========================================
:install_deps
echo.
echo [2/7] Instalando dependencias Python...

set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% neq 0 (
    color 0E
    echo    [ERRO] Python nao encontrado!
    echo    Instale Python manualmente e execute novamente
    pause
    exit /b 1
)

echo    Atualizando pip...
"%PYTHON_EXE%" -m pip install --quiet --upgrade pip 2>nul

echo    Instalando psutil...
"%PYTHON_EXE%" -m pip install --quiet psutil 2>nul

echo    Instalando httpx...
"%PYTHON_EXE%" -m pip install --quiet httpx 2>nul

echo    Instalando pywin32...
"%PYTHON_EXE%" -m pip install --quiet pywin32 2>nul

echo    Instalando pysnmp...
"%PYTHON_EXE%" -m pip install --quiet pysnmp 2>nul

echo    Instalando pyyaml...
"%PYTHON_EXE%" -m pip install --quiet pyyaml 2>nul

echo    [OK] Dependencias instaladas!

REM ========================================
REM PASSO 3: COPIAR ARQUIVOS
REM ========================================
echo.
echo [3/7] Copiando arquivos da Probe...

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.md" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "probe\requirements.txt" "%INSTALL_DIR%\" >nul 2>&1

echo    [OK] Arquivos copiados

REM ========================================
REM PASSO 4: FIREWALL
REM ========================================
echo.
echo [4/7] Configurando firewall (WMI)...

netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
echo    [OK] Firewall configurado

REM ========================================
REM PASSO 5: ATALHOS
REM ========================================
echo.
echo [5/7] Criando atalhos...

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Instalar Servico Coruja.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\install.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

echo    [OK] Atalhos criados

REM ========================================
REM PASSO 6: REGISTRO
REM ========================================
echo.
echo [6/7] Registrando instalacao...

reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.3" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallDate /t REG_SZ /d "%DATE% %TIME%" /f >nul 2>&1

echo    [OK] Instalacao registrada

REM ========================================
REM PASSO 7: VERIFICAR
REM ========================================
echo.
echo [7/7] Verificando instalacao...

set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Python: 
    "%PYTHON_EXE%" --version
) else (
    echo    [AVISO] Python nao encontrado
)

"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    echo    [OK] Dependencias OK
) else (
    echo    [AVISO] Algumas dependencias faltando
)

if exist "%INSTALL_DIR%\probe_core.py" (
    echo    [OK] Arquivos instalados
) else (
    echo    [ERRO] Arquivos nao encontrados
)

REM ========================================
REM CONCLUSAO
REM ========================================
echo.
color 0A
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Instalado em: %INSTALL_DIR%
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. CONFIGURAR PROBE:
echo.
echo    No Desktop, clique duas vezes em:
echo    "Configurar Coruja Probe"
echo.
echo    Digite:
echo    - IP do servidor: 192.168.31.161
echo    - Token da probe: (fornecido pelo admin)
echo.
echo 2. INSTALAR COMO SERVICO (Opcional):
echo.
echo    Menu Iniciar ^> Procure por:
echo    "Instalar Servico Coruja"
echo.
echo    Isso faz a probe iniciar automaticamente
echo    com o Windows
echo.
echo 3. VERIFICAR LOGS (se necessario):
echo.
echo    Pasta: %INSTALL_DIR%\logs
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para voltar ao menu...
pause >nul
goto :menu

REM ========================================
REM OPCAO 2: INSTALAR APENAS PYTHON
REM ========================================
:instalar_python_menu
cls
echo.
echo ========================================
echo   INSTALAR PYTHON 3.11
echo ========================================
echo.
echo Verificando Python...

REM Tentar python no PATH
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python ja instalado no PATH
    python --version
    echo.
    echo Pressione qualquer tecla para voltar ao menu...
    pause >nul
    goto :menu
)

REM Tentar Python 3.11 no local padrao
"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python 3.11 encontrado
    "C:\Program Files\Python311\python.exe" --version
    echo.
    echo [INFO] Adicionando ao PATH...
    set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
    echo [OK] Python adicionado ao PATH
    echo.
    echo Pressione qualquer tecla para voltar ao menu...
    pause >nul
    goto :menu
)

REM Tentar Python 3.10
"C:\Program Files\Python310\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python 3.10 encontrado
    "C:\Program Files\Python310\python.exe" --version
    echo.
    echo [INFO] Adicionando ao PATH...
    set "PATH=%PATH%;C:\Program Files\Python310;C:\Program Files\Python310\Scripts"
    echo [OK] Python adicionado ao PATH
    echo.
    echo Pressione qualquer tecla para voltar ao menu...
    pause >nul
    goto :menu
)

echo [INFO] Python nao encontrado - sera instalado
echo.
echo Baixando Python 3.11.8...
echo.

if not exist "python-3.11.8-amd64.exe" (
    echo Baixando de python.org (25 MB)...
    echo Aguarde 1-3 minutos...
    echo.
    
    powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Write-Host 'Baixando...'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-3.11.8-amd64.exe' -UseBasicParsing -TimeoutSec 300; Write-Host 'Download concluido!' } catch { Write-Host 'Erro no download: ' + $_.Exception.Message }"
    
    if not exist "python-3.11.8-amd64.exe" (
        color 0C
        echo.
        echo ========================================
        echo [ERRO] Falha ao baixar Python!
        echo ========================================
        echo.
        echo SOLUCAO:
        echo 1. Baixe manualmente:
        echo    https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
        echo.
        echo 2. Salve o arquivo nesta pasta:
        echo    %CD%
        echo.
        echo 3. Execute este instalador novamente
        echo.
        echo ========================================
        echo.
        pause
        goto :menu
    )
)

echo.
echo [INFO] Instalando Python 3.11.8...
echo Aguarde 2-5 minutos...
echo NAO FECHE ESTA JANELA!
echo.

start /wait python-3.11.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

echo Aguardando conclusao...
timeout /t 15 /nobreak >nul

set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"

"C:\Program Files\Python311\python.exe" --version >nul 2>&1
if %errorLevel% equ 0 (
    color 0A
    echo [OK] Python instalado com sucesso!
    "C:\Program Files\Python311\python.exe" --version
) else (
    color 0E
    echo [AVISO] Python pode nao ter sido instalado corretamente
)

echo.
echo Pressione qualquer tecla para voltar ao menu...
pause >nul
goto :menu

REM ========================================
REM OPCAO 3: INSTALAR APENAS DEPENDENCIAS
REM ========================================
:instalar_deps_menu
cls
echo.
echo ========================================
echo   INSTALAR DEPENDENCIAS PYTHON
echo ========================================
echo.

set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale Python primeiro (opcao 2 do menu)
    echo.
    pause
    goto :menu
)

echo Python encontrado:
"%PYTHON_EXE%" --version
echo.
echo Instalando dependencias...
echo.

echo [1/6] Atualizando pip...
"%PYTHON_EXE%" -m pip install --quiet --upgrade pip 2>nul

echo [2/6] Instalando psutil...
"%PYTHON_EXE%" -m pip install --quiet psutil 2>nul

echo [3/6] Instalando httpx...
"%PYTHON_EXE%" -m pip install --quiet httpx 2>nul

echo [4/6] Instalando pywin32...
"%PYTHON_EXE%" -m pip install --quiet pywin32 2>nul

echo [5/6] Instalando pysnmp...
"%PYTHON_EXE%" -m pip install --quiet pysnmp 2>nul

echo [6/6] Instalando pyyaml...
"%PYTHON_EXE%" -m pip install --quiet pyyaml 2>nul

echo.
color 0A
echo [OK] Dependencias instaladas com sucesso!
echo.
echo Pressione qualquer tecla para voltar ao menu...
pause >nul
goto :menu

REM ========================================
REM OPCAO 4: INSTALAR APENAS PROBE
REM ========================================
:instalar_probe_menu
cls
echo.
echo ========================================
echo   INSTALAR ARQUIVOS DA PROBE
echo ========================================
echo.

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

echo Copiando arquivos para:
echo %INSTALL_DIR%
echo.

mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\collectors" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

echo [1/5] Copiando arquivos Python...
xcopy /E /I /Y /Q "probe\*.py" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "%INSTALL_DIR%\collectors\" >nul 2>&1

echo [2/5] Copiando scripts BAT...
xcopy /E /I /Y /Q "probe\*.bat" "%INSTALL_DIR%\" >nul 2>&1

echo [3/5] Copiando documentacao...
xcopy /E /I /Y /Q "probe\*.txt" "%INSTALL_DIR%\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.md" "%INSTALL_DIR%\" >nul 2>&1
copy /Y "probe\requirements.txt" "%INSTALL_DIR%\" >nul 2>&1

echo [4/5] Configurando firewall...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

echo [5/5] Criando atalhos...
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Configurar Coruja Probe.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\configurar_probe.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%ProgramData%\Microsoft\Windows\Start Menu\Programs\Instalar Servico Coruja.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\install.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" >nul 2>&1

reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallPath /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v Version /t REG_SZ /d "1.0.3" /f >nul 2>&1
reg add "HKLM\SOFTWARE\CorujaMonitor\Probe" /v InstallDate /t REG_SZ /d "%DATE% %TIME%" /f >nul 2>&1

echo.
color 0A
echo [OK] Probe instalada com sucesso!
echo.
echo Instalado em: %INSTALL_DIR%
echo.
echo Atalhos criados:
echo - Desktop: Configurar Coruja Probe
echo - Menu Iniciar: Configurar Coruja Probe
echo - Menu Iniciar: Instalar Servico Coruja
echo.
echo Pressione qualquer tecla para voltar ao menu...
pause >nul
goto :menu

REM ========================================
REM OPCAO 5: VERIFICAR INSTALACAO
REM ========================================
:verificar
cls
echo.
echo ========================================
echo   VERIFICAR INSTALACAO
echo ========================================
echo.

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"
set "PYTHON_EXE=python"
if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
)

echo [1/3] Verificando Python...
"%PYTHON_EXE%" --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python instalado:
    "%PYTHON_EXE%" --version
) else (
    echo [ERRO] Python nao encontrado
)

echo.
echo [2/3] Verificando dependencias...
"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Todas as dependencias instaladas
) else (
    echo [AVISO] Algumas dependencias faltando
    echo.
    echo Testando individualmente:
    "%PYTHON_EXE%" -c "import psutil" >nul 2>&1 && echo   [OK] psutil || echo   [X] psutil
    "%PYTHON_EXE%" -c "import httpx" >nul 2>&1 && echo   [OK] httpx || echo   [X] httpx
    "%PYTHON_EXE%" -c "import win32api" >nul 2>&1 && echo   [OK] pywin32 || echo   [X] pywin32
    "%PYTHON_EXE%" -c "import pysnmp" >nul 2>&1 && echo   [OK] pysnmp || echo   [X] pysnmp
    "%PYTHON_EXE%" -c "import yaml" >nul 2>&1 && echo   [OK] pyyaml || echo   [X] pyyaml
)

echo.
echo [3/3] Verificando arquivos da Probe...
if exist "%INSTALL_DIR%\probe_core.py" (
    echo [OK] Arquivos instalados em:
    echo     %INSTALL_DIR%
) else (
    echo [ERRO] Arquivos nao encontrados em:
    echo       %INSTALL_DIR%
)

echo.
echo ========================================
echo   RESUMO
echo ========================================
echo.

set "STATUS_OK=0"
"%PYTHON_EXE%" --version >nul 2>&1 && set /a STATUS_OK+=1
"%PYTHON_EXE%" -c "import psutil, httpx, win32api, pysnmp, yaml" >nul 2>&1 && set /a STATUS_OK+=1
if exist "%INSTALL_DIR%\probe_core.py" set /a STATUS_OK+=1

if %STATUS_OK% equ 3 (
    color 0A
    echo [OK] Sistema pronto para uso!
    echo.
    echo Proximos passos:
    echo 1. Execute "Configurar Coruja Probe" no Desktop
    echo 2. Configure IP do servidor e token
    echo 3. Instale como servico (opcional)
) else (
    color 0E
    echo [AVISO] Instalacao incompleta
    echo.
    echo Execute a Instalacao Completa (opcao 1)
)

echo.
echo Pressione qualquer tecla para voltar ao menu...
pause >nul
goto :menu
