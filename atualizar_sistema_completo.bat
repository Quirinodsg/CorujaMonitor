@echo off
echo ========================================
echo   ATUALIZACAO COMPLETA DO SISTEMA
echo ========================================
echo.

echo [1/5] Parando probe...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Coruja*" 2>nul
timeout /t 2 >nul

echo [2/5] Fechando incidentes resolvidos...
docker-compose exec -T api python fechar_incidentes_resolvidos.py

echo [3/5] Reiniciando worker...
docker-compose restart worker

echo [4/5] Reiniciando API...
docker-compose restart api

echo [5/5] Aguardando servicos...
timeout /t 5 >nul

echo.
echo ========================================
echo   SISTEMA ATUALIZADO!
echo ========================================
echo.
echo Agora execute: iniciar_probe.bat
echo.
pause
