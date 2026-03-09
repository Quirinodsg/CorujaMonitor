@echo off
setlocal enabledelayedexpansion
title Verificar Metricas Probe
color 0B

echo.
echo ========================================
echo   VERIFICAR METRICAS PROBE
echo   Diagnostico Completo
echo ========================================
echo.

echo [1/7] Verificando se probe esta rodando...
echo.

tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if !errorLevel! equ 0 (
    echo [OK] Python esta rodando
    tasklist | findstr python.exe
) else (
    color 0C
    echo [X] Python NAO esta rodando!
    echo.
    echo A probe precisa estar rodando para enviar metricas.
    echo.
    echo Execute: EXECUTAR_PROBE_DIRETO.bat
    echo.
    pause
    exit /b 1
)

echo.
echo [2/7] Verificando logs da probe...
echo.

if exist "C:\Program Files\CorujaMonitor\Probe\logs\probe.log" (
    echo [OK] Arquivo de log existe
    echo.
    echo Ultimas 10 linhas do log:
    echo ----------------------------------------
    powershell -Command "Get-Content 'C:\Program Files\CorujaMonitor\Probe\logs\probe.log' -Tail 10"
    echo ----------------------------------------
) else (
    color 0E
    echo [X] Arquivo de log NAO existe
    echo.
    echo A probe pode nao ter iniciado corretamente.
)

echo.
echo [3/7] Testando conectividade com servidor...
echo.

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://192.168.31.161:8000/health' -TimeoutSec 5 -UseBasicParsing; Write-Host '[OK] Servidor acessivel' -ForegroundColor Green } catch { Write-Host '[X] Servidor NAO acessivel' -ForegroundColor Red; exit 1 }"

if !errorLevel! neq 0 (
    color 0C
    echo.
    echo Servidor nao esta acessivel!
    echo Verifique se o servidor esta rodando.
    echo.
    pause
    exit /b 1
)

echo.
echo [4/7] Verificando se probe esta registrada...
echo.

powershell -Command "$response = Invoke-RestMethod -Uri 'http://192.168.31.161:8000/api/probes' -Method Get -Headers @{'accept'='application/json'}; if ($response) { Write-Host '[OK] API de probes acessivel' -ForegroundColor Green; $response | ConvertTo-Json } else { Write-Host '[X] Nenhuma probe encontrada' -ForegroundColor Yellow }"

echo.
echo [5/7] Verificando servidores cadastrados...
echo.

powershell -Command "$response = Invoke-RestMethod -Uri 'http://192.168.31.161:8000/api/servers' -Method Get -Headers @{'accept'='application/json'}; if ($response -and $response.Count -gt 0) { Write-Host '[OK] Servidores encontrados:' -ForegroundColor Green; $response | ForEach-Object { Write-Host \"  - $($_.name) ($($_.ip))\" } } else { Write-Host '[X] NENHUM SERVIDOR CADASTRADO!' -ForegroundColor Red; Write-Host ''; Write-Host 'PROBLEMA ENCONTRADO:' -ForegroundColor Yellow; Write-Host 'Voce precisa adicionar servidores no dashboard!' -ForegroundColor Yellow }"

echo.
echo [6/7] Verificando sensores...
echo.

powershell -Command "$response = Invoke-RestMethod -Uri 'http://192.168.31.161:8000/api/sensors' -Method Get -Headers @{'accept'='application/json'}; if ($response -and $response.Count -gt 0) { Write-Host '[OK] Sensores encontrados: ' $response.Count -ForegroundColor Green } else { Write-Host '[X] Nenhum sensor encontrado' -ForegroundColor Yellow }"

echo.
echo [7/7] Verificando metricas recentes...
echo.

powershell -Command "$response = Invoke-RestMethod -Uri 'http://192.168.31.161:8000/api/metrics/recent' -Method Get -Headers @{'accept'='application/json'} -ErrorAction SilentlyContinue; if ($response) { Write-Host '[OK] Metricas encontradas' -ForegroundColor Green } else { Write-Host '[X] Nenhuma metrica recente' -ForegroundColor Yellow }"

echo.
echo ========================================
echo   RESUMO DO DIAGNOSTICO
echo ========================================
echo.
echo Se voce viu:
echo.
echo [X] NENHUM SERVIDOR CADASTRADO
echo.
echo SOLUCAO:
echo 1. Acesse: http://192.168.31.161:8000
echo 2. Menu: Servidores ^> + Novo Servidor
echo 3. Preencha:
echo    Nome: WIN-15GM8UTRS4K
echo    IP: 127.0.0.1
echo    Tenant: Techbiz
echo    Probe: WIN-15GM8UTRS4K
echo 4. Salvar
echo 5. Aguardar 60 segundos
echo 6. Atualizar pagina
echo.
echo ========================================
echo.
pause
