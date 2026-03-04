# Script para testar relatórios personalizados
Write-Host "=== TESTE DE RELATÓRIOS PERSONALIZADOS ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se a migração foi executada
Write-Host "1. Verificando migração..." -ForegroundColor Yellow
docker exec coruja-api python -c "from database import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('custom_reports' in inspector.get_table_names())"

# 2. Testar endpoint de templates
Write-Host ""
Write-Host "2. Testando endpoint de templates..." -ForegroundColor Yellow
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBjb3J1amEuY29tIiwiZXhwIjoxNzQwNjEyMDAwfQ.placeholder"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/custom-reports/templates" `
        -Method Get `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
    
    Write-Host "✓ Endpoint funcionando!" -ForegroundColor Green
    Write-Host "Templates encontrados: $($response.Count)" -ForegroundColor Green
    $response | ForEach-Object {
        Write-Host "  - $($_.name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Erro ao acessar endpoint:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# 3. Verificar logs da API
Write-Host ""
Write-Host "3. Últimas linhas do log da API:" -ForegroundColor Yellow
docker logs coruja-api --tail 20

# 4. Verificar se o router está registrado
Write-Host ""
Write-Host "4. Verificando router no main.py..." -ForegroundColor Yellow
docker exec coruja-api grep -n "custom_reports" main.py

Write-Host ""
Write-Host "=== INSTRUÇÕES ===" -ForegroundColor Cyan
Write-Host "1. Se a migração não foi executada, execute:" -ForegroundColor White
Write-Host "   docker exec coruja-api python migrate_custom_reports.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Reinicie a API:" -ForegroundColor White
Write-Host "   docker restart coruja-api" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Recompile o frontend:" -ForegroundColor White
Write-Host "   docker exec coruja-frontend npm run build" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Acesse: http://localhost:3000/reports" -ForegroundColor White
Write-Host "   Credenciais: admin@coruja.com / admin123" -ForegroundColor Gray
