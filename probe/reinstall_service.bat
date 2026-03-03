@echo off
title Reinstalar Servico Coruja Probe
color 0A

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   REINSTALAR SERVICO CORUJA PROBE
echo ========================================
echo.

echo [1] Parando servico (se estiver rodando)...
net stop CorujaProbe 2>nul
timeout /t 2 /nobreak >nul
echo.

echo [2] Removendo servico antigo...
python probe_service.py remove
timeout /t 2 /nobreak >nul
echo.

echo [3] Instalando servico novamente...
python probe_service.py install
if errorlevel 1 (
    echo [ERRO] Falha ao instalar servico!
    pause
    exit /b 1
)
echo [OK] Servico instalado
echo.

echo [4] Configurando servico para iniciar automaticamente...
sc config CorujaProbe start= auto
echo.

echo [5] Iniciando servico...
net start CorujaProbe
if errorlevel 1 (
    echo.
    echo [AVISO] Servico nao iniciou automaticamente
    echo Verificando logs...
    echo.
    if exist probe_service.log (
        echo === Log do Servico ===
        type probe_service.log
    )
    echo.
    echo Execute: .\diagnostico.bat para mais informacoes
) else (
    echo [OK] Servico iniciado com sucesso!
)
echo.

echo [6] Status final:
sc query CorujaProbe
echo.

echo ========================================
echo   CONCLUIDO
echo ========================================
echo.
pause
