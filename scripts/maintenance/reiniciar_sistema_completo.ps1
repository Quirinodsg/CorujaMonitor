# Script para reiniciar todo o sistema Coruja Monitor
Write-Host "🦉 Reiniciando Sistema Coruja Monitor..." -ForegroundColor Cyan

# 1. Parar todos os processos Python (probe)
Write-Host "`n1️⃣ Parando probe..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null
Start-Sleep -Seconds 2

# 2. Parar processos Node (frontend)
Write-Host "2️⃣ Parando frontend..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 3. Reiniciar containers Docker
Write-Host "3️⃣ Reiniciando containers Docker..." -ForegroundColor Yellow
docker compose restart
Start-Sleep -Seconds 5

# 4. Iniciar probe em background
Write-Host "4️⃣ Iniciando probe..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd probe; python probe_core.py" -WindowStyle Minimized

# 5. Iniciar frontend em background
Write-Host "5️⃣ Iniciando frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start" -WindowStyle Minimized

Write-Host "`n✅ Sistema reiniciado com sucesso!" -ForegroundColor Green
Write-Host "📊 Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "`nAguarde 30 segundos para tudo inicializar..." -ForegroundColor Yellow
