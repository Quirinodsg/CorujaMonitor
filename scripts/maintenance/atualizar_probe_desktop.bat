@echo off
echo ========================================
echo Atualizando Probe no Desktop
echo ========================================
echo.

REM Parar processo Python da probe
echo Parando probe...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Copiar arquivo corrigido
echo Copiando probe_core.py corrigido...
copy /Y "probe\probe_core.py" "%USERPROFILE%\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe\probe_core.py"

echo.
echo ========================================
echo Probe atualizada com sucesso!
echo ========================================
echo.
echo Agora execute manualmente:
echo cd "%USERPROFILE%\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe"
echo python probe_core.py
echo.
pause
