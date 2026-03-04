# Script de Atualização e Reinício do Sistema Coruja
# Executado automaticamente após aplicar uma atualização

param(
    [int]$DelaySeconds = 5
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Coruja Monitoring - Auto Update" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Aguardar para garantir que a API finalizou
Write-Host "Aguardando $DelaySeconds segundos para finalizar processos..." -ForegroundColor Yellow
Start-Sleep -Seconds $DelaySeconds

try {
    # Parar todos os serviços
    Write-Host "Parando serviços..." -ForegroundColor Yellow
    
    $processes = @("python", "uvicorn", "node")
    foreach ($proc in $processes) {
        Get-Process -Name $proc -ErrorAction SilentlyContinue | Where-Object {
            $_.Path -like "*coruja*"
        } | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "✓ Serviços parados" -ForegroundColor Green
    
    # Verificar se há requirements.txt novos
    if (Test-Path "api/requirements.txt") {
        Write-Host "Atualizando dependências Python..." -ForegroundColor Yellow
        pip install -r api/requirements.txt --upgrade --quiet
        Write-Host "✓ Dependências Python atualizadas" -ForegroundColor Green
    }
    
    # Verificar se há package.json novos
    if (Test-Path "frontend/package.json") {
        Write-Host "Atualizando dependências Node.js..." -ForegroundColor Yellow
        Push-Location frontend
        npm install --silent
        Pop-Location
        Write-Host "✓ Dependências Node.js atualizadas" -ForegroundColor Green
    }
    
    # Executar migrações de banco de dados se existirem
    if (Test-Path "api/migrations") {
        Write-Host "Executando migrações de banco de dados..." -ForegroundColor Yellow
        python -c "from api.database import run_migrations; run_migrations()" 2>$null
        Write-Host "✓ Migrações executadas" -ForegroundColor Green
    }
    
    # Limpar cache Python
    Write-Host "Limpando cache..." -ForegroundColor Yellow
    Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "✓ Cache limpo" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Atualização Concluída!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Reiniciar sistema
    Write-Host "Reiniciando sistema..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    
    if (Test-Path "restart.bat") {
        Start-Process -FilePath "restart.bat" -NoNewWindow
    } else {
        # Fallback: iniciar manualmente
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000" -NoNewWindow
    }
    
    Write-Host "✓ Sistema reiniciado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Acesse o sistema em: http://localhost:3000" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "❌ Erro durante atualização: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tentando reverter para backup..." -ForegroundColor Yellow
    
    # Tentar reverter para último backup
    $lastBackup = Get-ChildItem -Path "backups" -Directory | Sort-Object CreationTime -Descending | Select-Object -First 1
    
    if ($lastBackup) {
        Write-Host "Revertendo para: $($lastBackup.Name)" -ForegroundColor Yellow
        
        # Restaurar arquivos
        Copy-Item -Path "$($lastBackup.FullName)\*" -Destination "." -Recurse -Force
        
        Write-Host "✓ Sistema revertido" -ForegroundColor Green
        
        # Reiniciar
        if (Test-Path "restart.bat") {
            Start-Process -FilePath "restart.bat" -NoNewWindow
        }
    } else {
        Write-Host "❌ Nenhum backup encontrado para reverter" -ForegroundColor Red
    }
    
    exit 1
}
