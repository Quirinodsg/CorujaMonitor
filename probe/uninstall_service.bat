@echo off
echo Uninstalling Coruja Probe Service...

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Stop service
echo Stopping service...
python probe_service.py stop

REM Uninstall service
echo Uninstalling service...
python probe_service.py remove

echo.
echo Coruja Probe Service uninstalled successfully!
echo.
pause
