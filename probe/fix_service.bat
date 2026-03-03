@echo off
title Corrigir Servico do Probe
color 0A

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    echo Clique com botao direito e "Executar como administrador"
    pause
    exit /b 1
)

echo.
echo ========================================
echo   CORRIGIR SERVICO DO PROBE
echo ========================================
echo.

echo [1] Parando servico...
net stop CorujaProbe 2>nul
timeout /t 2 /nobreak >nul

echo [2] Removendo servico antigo...
python probe_service.py remove 2>nul
timeout /t 2 /nobreak >nul

echo [3] Limpando logs antigos...
del probe.log 2>nul
del probe_service.log 2>nul

echo [4] Instalando servico corrigido...
python probe_service.py install
if errorlevel 1 (
    echo [ERRO] Falha ao instalar!
    pause
    exit /b 1
)

echo [5] Configurando inicio automatico...
sc config CorujaProbe start= auto

echo [6] Iniciando servico...
net start CorujaProbe

echo.
echo [7] Aguardando 5 segundos...
timeout /t 5 /nobreak

echo.
echo [8] Verificando logs...
if exist probe.log (
    echo === probe.log ===
    type probe.log
    echo.
)
if exist probe_service.log (
    echo === probe_service.log ===
    type probe_service.log
    echo.
)

echo.
echo [9] Status final:
sc query CorujaProbe

echo.
echo ========================================
echo   CONCLUIDO
echo ========================================
echo.
echo Aguarde 1 minuto e verifique no frontend
echo se o probe ficou VERDE
echo.
pause
