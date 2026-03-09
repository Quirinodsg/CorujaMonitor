@echo off
setlocal enabledelayedexpansion
title Verificar Servidor Cadastrado
color 0B

echo.
echo ========================================
echo   VERIFICAR SERVIDOR NO DASHBOARD
echo ========================================
echo.

set "SERVER_IP=192.168.31.161"
set "TOKEN=qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8"

echo Consultando servidores cadastrados...
echo.

powershell -Command ^
"$headers = @{'Authorization' = 'Bearer %TOKEN%'}; ^
try { ^
    $response = Invoke-RestMethod -Uri 'http://%SERVER_IP%:3000/api/v1/servers' -Headers $headers -Method Get; ^
    Write-Host '[OK] Servidores encontrados:' -ForegroundColor Green; ^
    Write-Host ''; ^
    foreach ($server in $response) { ^
        Write-Host 'Nome: ' $server.name; ^
        Write-Host 'IP: ' $server.ip_address; ^
        Write-Host 'Probe: ' $server.probe_name; ^
        Write-Host 'Status: ' $server.status; ^
        Write-Host '---'; ^
    } ^
} catch { ^
    Write-Host '[ERRO] Nao foi possivel consultar servidores' -ForegroundColor Red; ^
    Write-Host $_.Exception.Message; ^
}"

echo.
echo ========================================
echo   INSTRUCOES
echo ========================================
echo.
echo Se NAO aparecer WIN-15GM8UTRS4K:
echo.
echo 1. Acesse: http://%SERVER_IP%:3000
echo 2. Login: admin@coruja.com / admin123
echo 3. Menu: Servidores
echo 4. Clique: + Novo Servidor
echo 5. Preencha:
echo    - Nome: WIN-15GM8UTRS4K
echo    - IP: 127.0.0.1
echo    - Tenant: Techbiz
echo    - Probe: WIN-15GM8UTRS4K
echo 6. Salvar
echo.
echo Se JA aparecer WIN-15GM8UTRS4K:
echo.
echo - Verifique se o nome da Probe esta correto
echo - Deve ser: WIN-15GM8UTRS4K
echo - Se estiver diferente, edite o servidor
echo.
echo ========================================
echo.
pause
