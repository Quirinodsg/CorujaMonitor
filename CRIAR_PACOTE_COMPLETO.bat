@echo off
REM ========================================
REM CRIAR PACOTE INSTALADOR COMPLETO
REM ========================================

echo.
echo ========================================
echo   CRIAR PACOTE INSTALADOR COMPLETO
echo ========================================
echo.

cd /d "C:\Users\andre.quirino\Coruja Monitor"

echo [1/6] Criando estrutura de pastas...
mkdir "probe-installer\probe" 2>nul
mkdir "probe-installer\probe\collectors" 2>nul

echo [2/6] Copiando arquivos Python...
xcopy /E /I /Y /Q "probe\*.py" "probe-installer\probe\" >nul 2>&1
xcopy /E /I /Y /Q "probe\collectors\*.py" "probe-installer\probe\collectors\" >nul 2>&1

echo [3/6] Copiando scripts BAT...
xcopy /E /I /Y /Q "probe\*.bat" "probe-installer\probe\" >nul 2>&1

echo [4/6] Copiando documentacao...
xcopy /E /I /Y /Q "probe\*.md" "probe-installer\probe\" >nul 2>&1
xcopy /E /I /Y /Q "probe\*.txt" "probe-installer\probe\" >nul 2>&1

echo [5/6] Copiando configuracoes...
copy /Y "probe\requirements.txt" "probe-installer\probe\" >nul 2>&1
copy /Y "probe\*.json" "probe-installer\probe\" >nul 2>&1

echo [6/6] Verificando arquivos copiados...

echo.
echo ========================================
echo   PACOTE CRIADO COM SUCESSO!
echo ========================================
echo.
echo Pasta: probe-installer\
echo.
echo CONTEUDO:
echo   - INSTALAR_TUDO.bat (instalador principal)
echo   - DESINSTALAR.bat (desinstalador)
echo   - README.txt (instrucoes)
echo   - probe\ (todos os arquivos da probe)
echo.

REM Contar arquivos
dir /B /S "probe-installer\probe\*.py" 2>nul | find /C ".py" > temp_count.txt
set /p PYTHON_COUNT=<temp_count.txt
del temp_count.txt

dir /B "probe-installer\probe\*.bat" 2>nul | find /C ".bat" > temp_count.txt
set /p BAT_COUNT=<temp_count.txt
del temp_count.txt

dir /B "probe-installer\probe\collectors\*.py" 2>nul | find /C ".py" > temp_count.txt
set /p COLLECTOR_COUNT=<temp_count.txt
del temp_count.txt

echo ESTATISTICAS:
echo   - Arquivos Python: %PYTHON_COUNT%
echo   - Scripts BAT: %BAT_COUNT%
echo   - Coletores: %COLLECTOR_COUNT%
echo.
echo PROXIMO PASSO:
echo   1. Comprima a pasta "probe-installer" em ZIP
echo   2. Distribua o ZIP para os clientes
echo   3. Cliente descompacta e executa INSTALAR_TUDO.bat
echo.
pause
