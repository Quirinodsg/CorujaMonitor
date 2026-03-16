@echo off
echo ========================================
echo CORRIGIR DEPENDENCIAS PYSNMP
echo ========================================
echo.

cd "C:\Program Files\CorujaMonitor\Probe"

echo Reinstalando pyasn1...
pip uninstall pyasn1 -y
pip install pyasn1==0.4.8

echo.
echo Reinstalando pysnmp...
pip uninstall pysnmp -y
pip install pysnmp==4.4.12

echo.
echo ========================================
echo TESTANDO
echo ========================================
echo.

python -c "from pysnmp.hlapi import *; print('✓ pysnmp funcionando!')"

echo.
echo ========================================
echo TESTE COMPLETO
echo ========================================
echo.

python TESTAR_SNMP_DETALHADO.py

echo.
pause
