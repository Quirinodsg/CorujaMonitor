@echo off
echo Reiniciando apenas a API...
docker compose restart api
echo.
echo Aguardando 5 segundos...
timeout /t 5 /nobreak
echo.
echo API reiniciada!
pause
