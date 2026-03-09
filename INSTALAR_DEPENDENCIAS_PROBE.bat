@echo off
chcp 65001 >nul
cls
echo ========================================
echo   INSTALAR DEPENDENCIAS DA PROBE
echo ========================================
echo.

echo Este script vai instalar as dependencias Python
echo necessarias para a probe funcionar.
echo.
echo ========================================
pause
echo.

echo Detectando Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo [OK] Python encontrado: python
    python --version
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
        echo [OK] Python encontrado: py
        py --version
    ) else (
        echo [ERRO] Python nao encontrado!
        echo.
        echo Instale Python 3.8+ de: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   INSTALANDO DEPENDENCIAS...
echo ========================================
echo.

echo Instalando requests...
%PYTHON_CMD% -m pip install requests
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar requests
    pause
    exit /b 1
)
echo [OK] requests instalado

echo.
echo Instalando httpx...
%PYTHON_CMD% -m pip install httpx
echo [OK] httpx instalado

echo.
echo Instalando psutil...
%PYTHON_CMD% -m pip install psutil
echo [OK] psutil instalado

echo.
echo Instalando pyyaml...
%PYTHON_CMD% -m pip install pyyaml
echo [OK] pyyaml instalado

echo.
echo Instalando wmi (opcional - para Windows)...
%PYTHON_CMD% -m pip install wmi
echo [OK] wmi instalado

echo.
echo Instalando pywin32 (opcional - para Windows)...
%PYTHON_CMD% -m pip install pywin32
echo [OK] pywin32 instalado

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.

echo Todas as dependencias foram instaladas!
echo.
echo Proximos passos:
echo.
echo 1. Execute: INICIAR_PROBE.bat
echo 2. Aguarde aparecer: "Server registered successfully"
echo 3. Verifique no dashboard: http://192.168.31.161:3000
echo.
echo ========================================
pause
