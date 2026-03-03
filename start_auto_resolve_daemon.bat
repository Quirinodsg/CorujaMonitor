@echo off
echo ========================================
echo Iniciando Daemon de Auto-Resolucao
echo ========================================
echo.

cd api
python auto_resolve_simulated_failures.py

pause
