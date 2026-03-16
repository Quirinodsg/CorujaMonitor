@echo off
echo ========================================
echo TESTAR SNMP DA MAQUINA SONDA
echo ========================================
echo.

cd "C:\Program Files\CorujaMonitor\Probe"

echo [1/3] Testando conectividade basica...
ping -n 1 192.168.31.161
echo.

echo [2/3] Testando porta 161 UDP...
echo Nota: Test-NetConnection nao funciona bem com UDP
echo Vamos testar direto com Python
echo.

echo [3/3] Testando SNMP com Python...
python TESTAR_SNMP_DETALHADO.py

echo.
echo ========================================
echo.
pause
