# Script para testar o sistema de grupos hierarquicos

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE: Sistema de Grupos Hierarquicos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Fazer login
Write-Host "1. Fazendo login..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=admin@coruja.com&password=admin123"

$token = $loginResponse.access_token
$headers = @{
    "Authorization" = "Bearer $token"
}

Write-Host "Login realizado com sucesso!" -ForegroundColor Green
Write-Host ""

# Listar grupos existentes
Write-Host "2. Listando grupos existentes..." -ForegroundColor Yellow
$grupos = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method GET `
    -Headers $headers

Write-Host "Total de grupos: $($grupos.Count)" -ForegroundColor Green
if ($grupos.Count -gt 0) {
    foreach ($grupo in $grupos) {
        $indent = "  " * $grupo.level
        Write-Host "$indent$($grupo.icon) $($grupo.name) (ID: $($grupo.id), Sensores: $($grupo.sensor_count))" -ForegroundColor Cyan
    }
}
Write-Host ""

# Criar grupo raiz
Write-Host "3. Criando grupo raiz Producao..." -ForegroundColor Yellow
$grupoProducao = @{
    name = "Producao"
    description = "Servidores de producao"
    icon = "🏭"
    color = "#f44336"
} | ConvertTo-Json

$producaoResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $grupoProducao

Write-Host "Grupo criado: ID $($producaoResponse.id)" -ForegroundColor Green
Write-Host ""

# Criar subgrupo
Write-Host "4. Criando subgrupo Datacenter SP dentro de Producao..." -ForegroundColor Yellow
$subgrupo = @{
    name = "Datacenter SP"
    parent_id = $producaoResponse.id
    description = "Servidores no datacenter de Sao Paulo"
    icon = "🏢"
    color = "#2196f3"
} | ConvertTo-Json

$subgrupoResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $subgrupo

Write-Host "Subgrupo criado: ID $($subgrupoResponse.id)" -ForegroundColor Green
Write-Host ""

# Criar outro grupo raiz
Write-Host "5. Criando grupo raiz Homologacao..." -ForegroundColor Yellow
$grupoHomolog = @{
    name = "Homologacao"
    description = "Ambiente de testes"
    icon = "🧪"
    color = "#ff9800"
} | ConvertTo-Json

$homologResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $grupoHomolog

Write-Host "Grupo criado: ID $($homologResponse.id)" -ForegroundColor Green
Write-Host ""

# Listar estrutura hierarquica
Write-Host "6. Listando estrutura hierarquica completa..." -ForegroundColor Yellow
$gruposAtualizados = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method GET `
    -Headers $headers

Write-Host "Estrutura de grupos:" -ForegroundColor Green
foreach ($grupo in $gruposAtualizados) {
    $indent = "  " * $grupo.level
    $parentInfo = if ($grupo.parent_id) { " (Pai: ID $($grupo.parent_id))" } else { " (Raiz)" }
    Write-Host "$indent$($grupo.icon) $($grupo.name)$parentInfo - $($grupo.sensor_count) sensores" -ForegroundColor Cyan
}
Write-Host ""

# Mover subgrupo
Write-Host "7. Movendo Datacenter SP para Homologacao..." -ForegroundColor Yellow
$moverBody = @{
    new_parent_id = $homologResponse.id
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups/$($subgrupoResponse.id)/move" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $moverBody

Write-Host "Grupo movido com sucesso!" -ForegroundColor Green
Write-Host ""

# Listar estrutura apos mover
Write-Host "8. Estrutura apos mover o grupo..." -ForegroundColor Yellow
$gruposFinais = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method GET `
    -Headers $headers

foreach ($grupo in $gruposFinais) {
    $indent = "  " * $grupo.level
    $parentInfo = if ($grupo.parent_id) { " (Pai: ID $($grupo.parent_id))" } else { " (Raiz)" }
    Write-Host "$indent$($grupo.icon) $($grupo.name)$parentInfo" -ForegroundColor Cyan
}
Write-Host ""

# Excluir grupo
Write-Host "9. Excluindo grupo Datacenter SP..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups/$($subgrupoResponse.id)" `
    -Method DELETE `
    -Headers $headers

Write-Host "Grupo excluido com sucesso!" -ForegroundColor Green
Write-Host ""

# Estrutura final
Write-Host "10. Estrutura final apos exclusao..." -ForegroundColor Yellow
$gruposFinais2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/sensor-groups" `
    -Method GET `
    -Headers $headers

foreach ($grupo in $gruposFinais2) {
    $indent = "  " * $grupo.level
    Write-Host "$indent$($grupo.icon) $($grupo.name)" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "TODOS OS TESTES CONCLUIDOS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse o sistema em: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Va em Servidores para ver os botoes de gerenciamento de grupos" -ForegroundColor Cyan
Write-Host ""
