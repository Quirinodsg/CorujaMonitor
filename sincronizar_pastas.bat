@echo off
echo ========================================
echo Sincronizando Pastas Coruja Monitor
echo ========================================
echo.

set "PASTA1=C:\Users\andre.quirino\Coruja Monitor"
set "PASTA2=C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor"

echo Origem: %PASTA1%
echo Destino: %PASTA2%
echo.

REM ========================================
REM Sincronizar Documentacao (arquivos .md)
REM ========================================
echo [1/5] Sincronizando documentacao (.md)...

xcopy "%PASTA1%\*.md" "%PASTA2%\" /Y /D >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Documentacao sincronizada
) else (
    echo ⚠ Erro ao sincronizar documentacao
)

REM ========================================
REM Sincronizar Scripts (.bat)
REM ========================================
echo [2/5] Sincronizando scripts (.bat)...

xcopy "%PASTA1%\*.bat" "%PASTA2%\" /Y /D >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Scripts sincronizados
) else (
    echo ⚠ Erro ao sincronizar scripts
)

REM ========================================
REM Sincronizar Pasta API
REM ========================================
echo [3/5] Sincronizando pasta API...

xcopy "%PASTA1%\api\*.py" "%PASTA2%\api\" /Y /D /S >nul 2>&1
xcopy "%PASTA1%\api\*.txt" "%PASTA2%\api\" /Y /D /S >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ API sincronizada
) else (
    echo ⚠ Erro ao sincronizar API
)

REM ========================================
REM Sincronizar Pasta Probe
REM ========================================
echo [4/5] Sincronizando pasta Probe...

xcopy "%PASTA1%\probe\*.py" "%PASTA2%\probe\" /Y /D /S >nul 2>&1
xcopy "%PASTA1%\probe\*.bat" "%PASTA2%\probe\" /Y /D /S >nul 2>&1
xcopy "%PASTA1%\probe\*.txt" "%PASTA2%\probe\" /Y /D /S >nul 2>&1
xcopy "%PASTA1%\probe\*.md" "%PASTA2%\probe\" /Y /D /S >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Probe sincronizada
) else (
    echo ⚠ Erro ao sincronizar Probe
)

REM ========================================
REM Sincronizar Frontend
REM ========================================
echo [5/5] Sincronizando Frontend...

xcopy "%PASTA1%\frontend\src\components\*.js" "%PASTA2%\frontend\src\components\" /Y /D /S >nul 2>&1
xcopy "%PASTA1%\frontend\src\components\*.css" "%PASTA2%\frontend\src\components\" /Y /D /S >nul 2>&1
xcopy "%PASTA1%\frontend\src\data\*.js" "%PASTA2%\frontend\src\data\" /Y /D /S >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Frontend sincronizado
) else (
    echo ⚠ Erro ao sincronizar Frontend
)

echo.
echo ========================================
echo Sincronizacao Concluida!
echo ========================================
echo.
echo Arquivos sincronizados de:
echo   %PASTA1%
echo.
echo Para:
echo   %PASTA2%
echo.
echo Agora ambas as pastas estao atualizadas!
echo.
pause
