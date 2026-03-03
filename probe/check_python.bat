@echo off
title Verificar Python
color 0A

echo.
echo ========================================
echo   VERIFICACAO DO PYTHON
echo ========================================
echo.

REM Tentar python
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python encontrado:
    python --version
    echo.
    echo Python esta instalado corretamente!
    echo.
    echo Proximos passos:
    echo 1. Execute: setup_wizard.bat
    echo.
    pause
    exit /b 0
)

REM Tentar py
py --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python encontrado via 'py':
    py --version
    echo.
    echo Python esta instalado, mas nao esta no PATH.
    echo.
    echo Solucao:
    echo 1. Reinstale o Python
    echo 2. Marque "Add Python to PATH"
    echo 3. Ou use 'py' em vez de 'python'
    echo.
    pause
    exit /b 0
)

REM Python nao encontrado
echo [ERRO] Python NAO encontrado!
echo.
echo Para instalar o Python:
echo.
echo 1. Acesse: https://www.python.org/downloads/
echo 2. Baixe Python 3.11 ou superior
echo 3. Durante a instalacao:
echo    - Marque "Add Python to PATH"
echo    - Clique em "Install Now"
echo 4. Apos instalar, REINICIE o PowerShell
echo 5. Execute este script novamente
echo.
echo Deseja abrir o site do Python agora? (S/N)
set /p OPEN="Resposta: "
if /i "%OPEN%"=="S" start https://www.python.org/downloads/
echo.
pause
exit /b 1
