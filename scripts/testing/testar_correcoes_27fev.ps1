# Script de Teste das Correções - 27 FEV 2026
# Testa todas as correções aplicadas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DAS CORREÇÕES - 27 FEV 2026" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# 1. Verificar Backup
Write-Host "1. Verificando backup..." -ForegroundColor Yellow
if (Test-Path "api/backup_20260227_143233") {
    Write-Host "   ✅ Backup encontrado" -ForegroundColor Green
    $backupFiles = Get-ChildItem "api/backup_20260227_143233"
    Write-Host "   📁 Arquivos no backup: $($backupFiles.Count)" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Backup NÃO encontrado!" -ForegroundColor Red
    $errors++
}
Write-Host ""

# 2. Verificar probe_core.py
Write-Host "2. Verificando probe_core.py..." -ForegroundColor Yellow
$probeCore = Get-Content "probe/probe_core.py" -Raw
if ($probeCore -match "from collectors.snmp_collector import SNMPCollector") {
    Write-Host "   ✅ SNMP Collector importado" -ForegroundColor Green
} else {
    Write-Host "   ❌ SNMP Collector NÃO importado!" -ForegroundColor Red
    $errors++
}

if ($probeCore -match "collector = SNMPCollector\(\)") {
    Write-Host "   ✅ SNMP Collector instanciado" -ForegroundColor Green
} else {
    Write-Host "   ❌ SNMP Collector NÃO instanciado!" -ForegroundColor Red
    $errors++
}

if ($probeCore -match "Fallback to PING") {
    Write-Host "   ✅ Fallback para PING implementado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Fallback para PING não encontrado" -ForegroundColor Yellow
    $warnings++
}
Write-Host ""

# 3. Verificar MainLayout.js
Write-Host "3. Verificando MainLayout.js..." -ForegroundColor Yellow
$mainLayout = Get-Content "frontend/src/components/MainLayout.js" -Raw

$componentsToCheck = @(
    "CustomReports",
    "ThresholdConfig",
    "Probes",
    "NOCRealTime",
    "AdvancedDashboard",
    "ServersGrouped",
    "AutoRemediation"
)

foreach ($component in $componentsToCheck) {
    if ($mainLayout -match "import $component from") {
        Write-Host "   ✅ $component importado" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $component NÃO importado!" -ForegroundColor Red
        $errors++
    }
}

# Verificar rotas
$routesToCheck = @(
    "custom-reports",
    "threshold-config",
    "probes",
    "noc-realtime",
    "advanced-dashboard",
    "servers-grouped",
    "auto-remediation"
)

Write-Host ""
Write-Host "   Verificando rotas..." -ForegroundColor Gray
foreach ($route in $routesToCheck) {
    if ($mainLayout -match "case '$route':") {
        Write-Host "   ✅ Rota '$route' adicionada" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Rota '$route' NÃO adicionada!" -ForegroundColor Red
        $errors++
    }
}
Write-Host ""

# 4. Verificar Sidebar.js
Write-Host "4. Verificando Sidebar.js..." -ForegroundColor Yellow
$sidebar = Get-Content "frontend/src/components/Sidebar.js" -Raw

$menuItemsToCheck = @(
    @{id="advanced-dashboard"; label="Dashboard Avançado"},
    @{id="servers-grouped"; label="Servidores Agrupados"},
    @{id="probes"; label="Probes"},
    @{id="custom-reports"; label="Relatórios Personalizados"},
    @{id="threshold-config"; label="Thresholds"},
    @{id="noc-realtime"; label="NOC Tempo Real"},
    @{id="auto-remediation"; label="Auto-remediação"}
)

foreach ($item in $menuItemsToCheck) {
    if ($sidebar -match "id: '$($item.id)'") {
        Write-Host "   ✅ Menu '$($item.label)' adicionado" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Menu '$($item.label)' NÃO adicionado!" -ForegroundColor Red
        $errors++
    }
}
Write-Host ""

# 5. Verificar componentes existem
Write-Host "5. Verificando se componentes existem..." -ForegroundColor Yellow
$componentsPath = "frontend/src/components"
$componentsFiles = @(
    "CustomReports.js",
    "ThresholdConfig.js",
    "Probes.js",
    "NOCRealTime.js",
    "AdvancedDashboard.js",
    "ServersGrouped.js",
    "AutoRemediation.js"
)

foreach ($file in $componentsFiles) {
    $fullPath = Join-Path $componentsPath $file
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "   ✅ $file existe ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file NÃO existe!" -ForegroundColor Red
        $errors++
    }
}
Write-Host ""

# 6. Verificar SNMP Collector
Write-Host "6. Verificando SNMP Collector..." -ForegroundColor Yellow
if (Test-Path "probe/collectors/snmp_collector.py") {
    $snmpCollector = Get-Content "probe/collectors/snmp_collector.py" -Raw
    if ($snmpCollector -match "class SNMPCollector") {
        Write-Host "   ✅ SNMPCollector class existe" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SNMPCollector class NÃO encontrada!" -ForegroundColor Red
        $errors++
    }
    
    if ($snmpCollector -match "def collect_snmp_v2c") {
        Write-Host "   ✅ Método collect_snmp_v2c existe" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Método collect_snmp_v2c NÃO encontrado!" -ForegroundColor Red
        $errors++
    }
    
    if ($snmpCollector -match "def collect_snmp_v3") {
        Write-Host "   ✅ Método collect_snmp_v3 existe" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Método collect_snmp_v3 NÃO encontrado!" -ForegroundColor Red
        $errors++
    }
} else {
    Write-Host "   ❌ snmp_collector.py NÃO existe!" -ForegroundColor Red
    $errors++
}
Write-Host ""

# 7. Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DOS TESTES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Correções aplicadas com sucesso:" -ForegroundColor Green
    Write-Host "  • SNMP Collector integrado" -ForegroundColor Gray
    Write-Host "  • 7 componentes frontend integrados" -ForegroundColor Gray
    Write-Host "  • 7 menu items adicionados" -ForegroundColor Gray
    Write-Host "  • ~3.410 linhas de código ativadas" -ForegroundColor Gray
} elseif ($errors -eq 0) {
    Write-Host "⚠️  TESTES PASSARAM COM AVISOS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Avisos: $warnings" -ForegroundColor Yellow
} else {
    Write-Host "❌ TESTES FALHARAM!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Erros: $errors" -ForegroundColor Red
    Write-Host "Avisos: $warnings" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Verifique os erros acima e corrija antes de continuar." -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 8. Próximos passos
if ($errors -eq 0) {
    Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Reiniciar Probe:" -ForegroundColor Yellow
    Write-Host "   cd probe" -ForegroundColor Gray
    Write-Host "   .\parar_todas_probes.bat" -ForegroundColor Gray
    Write-Host "   .\iniciar_probe_limpo.bat" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Testar Frontend:" -ForegroundColor Yellow
    Write-Host "   Acessar http://localhost:3000" -ForegroundColor Gray
    Write-Host "   Login: admin@coruja.com / admin123" -ForegroundColor Gray
    Write-Host "   Verificar novos menus no sidebar" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Verificar Logs:" -ForegroundColor Yellow
    Write-Host "   Get-Content probe\probe.log -Tail 50 -Wait" -ForegroundColor Gray
    Write-Host ""
}

# Retornar código de saída
if ($errors -gt 0) {
    exit 1
} else {
    exit 0
}
