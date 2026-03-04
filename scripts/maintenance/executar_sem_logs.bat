@echo off
echo ========================================
echo   CORRECAO COMPLETA - SEM LOGS
echo ========================================
echo.

echo [1/6] Parando processos Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 3 >nul
echo   OK

echo [2/6] Fechando incidentes...
docker-compose exec -T api python fechar_incidentes_resolvidos.py 2>nul | findstr /C:"Encontrados" /C:"Fechando" /C:"Fechados" /C:"Ainda"
echo   OK

echo [3/6] Reiniciando worker...
docker-compose restart worker >nul 2>&1
echo   OK

echo [4/6] Reiniciando API...
docker-compose restart api >nul 2>&1
echo   OK

echo [5/6] Aguardando servicos...
timeout /t 10 >nul
echo   OK

echo [6/6] Iniciando probe...
start "Coruja Probe" cmd /k "cd /d %CD% && python probe\probe_core.py"
timeout /t 2 >nul
echo   OK

echo.
echo ========================================
echo   CONCLUIDO!
echo ========================================
echo.
echo Verifique a janela "Coruja Probe" que foi aberta
echo Aguarde 60 segundos para primeira coleta
echo.
pause
