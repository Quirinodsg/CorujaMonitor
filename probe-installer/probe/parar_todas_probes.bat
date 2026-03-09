@echo off
echo ========================================
echo   PARAR TODAS AS PROBES
echo ========================================
echo.

REM Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Este script precisa ser executado como Administrador!
    echo.
    echo Clique com botao direito e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [1/3] Parando tarefa agendada CorujaProbe...
schtasks /End /TN "CorujaProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tarefa agendada parada
) else (
    echo [INFO] Tarefa agendada nao estava rodando
)

echo.
echo [2/3] Matando todos os processos Python...
taskkill /F /IM python.exe >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Processos python.exe finalizados
) else (
    echo [INFO] Nenhum processo python.exe encontrado
)

taskkill /F /IM pythonservice.exe >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Processo pythonservice.exe finalizado
) else (
    echo [INFO] Nenhum processo pythonservice.exe encontrado
)

echo.
echo [3/3] Verificando se ainda ha processos rodando...
tasklist | findstr /I "python" >nul 2>&1
if %errorLevel% equ 0 (
    echo [AVISO] Ainda ha processos Python rodando:
    tasklist | findstr /I "python"
    echo.
    echo Tente reiniciar o computador se necessario
) else (
    echo [OK] Nenhum processo Python rodando
)

echo.
echo ========================================
echo   TODAS AS PROBES FORAM PARADAS
echo ========================================
echo.
echo Agora voce pode iniciar a probe com o comando:
echo   python probe_core.py
echo.
pause
