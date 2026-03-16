@echo off
echo ========================================
echo INSTALAR PYSNMP NA SRVSONDA001
echo ========================================
echo.

cd "C:\Program Files\CorujaMonitor\Probe"

echo Instalando pysnmp...
python -m pip install pysnmp

echo.
echo ========================================
echo TESTANDO INSTALACAO
echo ========================================
echo.

python -c "from pysnmp.hlapi import *; print('✓ pysnmp instalado com sucesso!')"

echo.
echo ========================================
echo TESTANDO SNMP COLLECTOR
echo ========================================
echo.

python TESTAR_SNMP_MANUALMENTE.py

echo.
echo ========================================
echo INSTALACAO CONCLUIDA
echo ========================================
echo.
echo Agora reinicie a probe:
echo 1. Pare a probe (Ctrl+C)
echo 2. Execute: iniciar_probe.bat
echo.
pause
