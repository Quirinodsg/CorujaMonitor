# Build MSI com Auto-Start Integrado
# Versão atualizada com instalação automática de serviço

param(
    [string]$Version = "1.0.1",
    [string]$OutputDir = ".\output",
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD MSI - CORUJA MONITOR PROBE" -ForegroundColor Cyan
Write-Host "  COM AUTO-START INTEGRADO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar WiX Toolset
Write-Host "[1/8] Verificando WiX Toolset..." -ForegroundColor Yellow
$wixPath = "${env:WIX}bin"
if (-not (Test-Path $wixPath)) {
    Write-Host "ERRO: WiX Toolset não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale WiX Toolset 3.11+:" -ForegroundColor Yellow
    Write-Host "https://wixtoolset.org/releases/" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou use o instalador alternativo:" -ForegroundColor Yellow
    Write-Host ".\build-msi-simple.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}
Write-Host "✓ WiX Toolset encontrado: $wixPath" -ForegroundColor Green
Write-Host ""

# Verificar arquivos necessários
Write-Host "[2/8] Verificando arquivos..." -ForegroundColor Yellow
$requiredFiles = @(
    "..\probe\probe_core.py",
    "..\probe\config.py",
    "..\probe\requirements.txt",
    ".\CorujaProbe.wxs",
    ".\CustomActions.wxs"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "ERRO: Arquivo não encontrado: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Todos os arquivos encontrados" -ForegroundColor Green
Write-Host ""

# Criar diretório de saída
Write-Host "[3/8] Criando diretório de saída..." -ForegroundColor Yellow
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}
Write-Host "✓ Diretório criado: $OutputDir" -ForegroundColor Green
Write-Host ""

# Criar templates se não existirem
Write-Host "[4/8] Preparando templates..." -ForegroundColor Yellow
$templatesDir = ".\templates"
if (-not (Test-Path $templatesDir)) {
    New-Item -ItemType Directory -Path $templatesDir | Out-Null
}

$probeConfigTemplate = @"
{
  "api_url": "http://192.168.0.9:8000",
  "probe_token": "CONFIGURE_DURANTE_INSTALACAO",
  "collection_interval": 60,
  "log_level": "INFO",
  "auto_start": true,
  "service_name": "CorujaMonitorProbe"
}
"@
$probeConfigTemplate | Out-File -FilePath "$templatesDir\probe_config.json" -Encoding UTF8
Write-Host "✓ Templates preparados" -ForegroundColor Green
Write-Host ""

if (-not $SkipBuild) {
    # Compilar WXS
    Write-Host "[5/8] Compilando arquivos WXS..." -ForegroundColor Yellow
    
    & "$wixPath\candle.exe" `
        -dVersion=$Version `
        -dProductVersion=$Version `
        -out "$OutputDir\" `
        ".\CorujaProbe.wxs" `
        ".\CustomActions.wxs"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha ao compilar WXS" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Compilação concluída" -ForegroundColor Green
    Write-Host ""
    
    # Linkar MSI
    Write-Host "[6/8] Criando arquivo MSI..." -ForegroundColor Yellow
    
    & "$wixPath\light.exe" `
        -out "$OutputDir\CorujaMonitorProbe-$Version.msi" `
        -ext WixUIExtension `
        -ext WixUtilExtension `
        "$OutputDir\CorujaProbe.wixobj" `
        "$OutputDir\CustomActions.wixobj"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha ao criar MSI" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ MSI criado com sucesso" -ForegroundColor Green
    Write-Host ""
}

# Criar documentação
Write-Host "[7/8] Criando documentação..." -ForegroundColor Yellow

$readmeContent = @"
CORUJA MONITOR PROBE - INSTALADOR MSI
======================================
Versão: $Version
Data: $(Get-Date -Format "dd/MM/yyyy")

NOVIDADES DESTA VERSÃO:
✓ Auto-start automático via Task Scheduler
✓ Inicia automaticamente quando a máquina ligar
✓ Recuperação automática em caso de falha
✓ Instalação simplificada em um clique

REQUISITOS:
- Windows 7/Server 2008 R2 ou superior (64-bit)
- Python 3.8 ou superior instalado
- Privilégios de administrador
- 100 MB de espaço em disco

INSTALAÇÃO:
1. Clique direito no arquivo MSI
2. Selecione "Executar como administrador"
3. Siga o assistente de instalação
4. Configure IP do servidor e token
5. Aguarde a instalação concluir
6. A probe iniciará automaticamente!

O QUE É INSTALADO:
✓ Arquivos da probe em C:\Program Files\CorujaMonitor\
✓ Usuário MonitorUser para WMI
✓ Configuração de Firewall para WMI
✓ Configuração de DCOM
✓ Dependências Python
✓ Tarefa agendada para auto-start
✓ Atalhos no Menu Iniciar

AUTO-START:
A probe é configurada para iniciar automaticamente:
- 30 segundos após o boot do sistema
- Quando um usuário fizer login
- Recuperação automática se falhar (3 tentativas)

VERIFICAR INSTALAÇÃO:
1. Abra o Agendador de Tarefas
2. Procure por "CorujaMonitorProbe"
3. Verifique se está "Pronto" ou "Em execução"

Ou execute no PowerShell:
  schtasks /query /tn "CorujaMonitorProbe"

GERENCIAR SERVIÇO:
Iniciar:
  schtasks /run /tn "CorujaMonitorProbe"

Parar:
  taskkill /f /im python.exe

Ver status:
  schtasks /query /tn "CorujaMonitorProbe"

Ver logs:
  type "C:\Program Files\CorujaMonitor\Probe\logs\probe.log"

DESINSTALAÇÃO:
1. Painel de Controle → Programas e Recursos
2. Selecione "Coruja Monitor Probe"
3. Clique em "Desinstalar"

Ou via PowerShell:
  msiexec /x CorujaMonitorProbe-$Version.msi

TROUBLESHOOTING:
1. Probe não inicia:
   - Verifique se Python está instalado: python --version
   - Verifique logs em: C:\Program Files\CorujaMonitor\Probe\logs\

2. Erro de permissão:
   - Execute o instalador como Administrador
   - Clique direito → "Executar como administrador"

3. Probe para após alguns minutos:
   - Verifique configuração em probe_config.json
   - Verifique conectividade com servidor
   - Veja logs para detalhes do erro

4. Não aparece no dashboard:
   - Verifique se token está correto
   - Verifique se IP do servidor está correto
   - Teste conectividade: ping IP_SERVIDOR

SUPORTE:
- Documentação: C:\Program Files\CorujaMonitor\Probe\README.md
- Dashboard: http://SEU_IP:3000
- Logs: C:\Program Files\CorujaMonitor\Probe\logs\probe.log

ARQUIVOS IMPORTANTES:
- probe_config.json - Configuração da probe
- wmi_credentials.json - Credenciais WMI
- logs\probe.log - Log de execução

SEGURANÇA:
✓ Usuário MonitorUser criado com senha aleatória
✓ Credenciais armazenadas localmente
✓ Firewall configurado apenas para WMI
✓ Execução com privilégios mínimos necessários

CHANGELOG:
v1.0.1 ($(Get-Date -Format "dd/MM/yyyy"))
- ✓ Adicionado auto-start via Task Scheduler
- ✓ Recuperação automática em falhas
- ✓ Melhorias na instalação
- ✓ Documentação atualizada

v1.0.0
- Versão inicial

======================================
Coruja Monitor © 2026
https://github.com/Quirinodsg/CorujaMonitor
======================================
"@

$readmeContent | Out-File -FilePath "$OutputDir\README.txt" -Encoding UTF8
Write-Host "✓ Documentação criada" -ForegroundColor Green
Write-Host ""

# Criar script de teste
$testScript = @"
@echo off
REM Script de teste pós-instalação

echo ========================================
echo   TESTE DE INSTALACAO - CORUJA PROBE
echo ========================================
echo.

echo [1/5] Verificando arquivos instalados...
if exist "C:\Program Files\CorujaMonitor\Probe\probe_core.py" (
    echo [OK] Arquivos instalados
) else (
    echo [ERRO] Arquivos nao encontrados
)

echo [2/5] Verificando usuario MonitorUser...
net user MonitorUser >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Usuario MonitorUser existe
) else (
    echo [ERRO] Usuario nao encontrado
)

echo [3/5] Verificando tarefa agendada...
schtasks /query /tn "CorujaMonitorProbe" >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Tarefa agendada configurada
    schtasks /query /tn "CorujaMonitorProbe" /fo list | findstr "Status:"
) else (
    echo [ERRO] Tarefa nao encontrada
)

echo [4/5] Verificando se probe esta rodando...
tasklist | findstr python.exe >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Probe em execucao
) else (
    echo [INFO] Probe nao esta rodando
    echo Execute: schtasks /run /tn "CorujaMonitorProbe"
)

echo [5/5] Verificando logs...
if exist "C:\Program Files\CorujaMonitor\Probe\logs\probe.log" (
    echo [OK] Log encontrado
    echo.
    echo Ultimas 5 linhas:
    powershell Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\probe.log" -Tail 5
) else (
    echo [INFO] Log ainda nao criado
)

echo.
echo ========================================
echo TESTE CONCLUIDO
echo ========================================
echo.
pause
"@

$testScript | Out-File -FilePath "$OutputDir\testar-instalacao.bat" -Encoding ASCII
Write-Host "✓ Script de teste criado" -ForegroundColor Green
Write-Host ""

# Resumo
Write-Host "[8/8] Finalizando..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  BUILD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivos criados:" -ForegroundColor Cyan
Write-Host "  MSI: $OutputDir\CorujaMonitorProbe-$Version.msi" -ForegroundColor White
Write-Host "  README: $OutputDir\README.txt" -ForegroundColor White
Write-Host "  Teste: $OutputDir\testar-instalacao.bat" -ForegroundColor White
Write-Host ""
Write-Host "Tamanho do MSI:" -ForegroundColor Cyan
if (Test-Path "$OutputDir\CorujaMonitorProbe-$Version.msi") {
    $size = (Get-Item "$OutputDir\CorujaMonitorProbe-$Version.msi").Length / 1MB
    Write-Host "  $([math]::Round($size, 2)) MB" -ForegroundColor White
}
Write-Host ""
Write-Host "NOVIDADES DESTA VERSÃO:" -ForegroundColor Yellow
Write-Host "  ✓ Auto-start automático via Task Scheduler" -ForegroundColor Green
Write-Host "  ✓ Inicia 30s após boot do sistema" -ForegroundColor Green
Write-Host "  ✓ Recuperação automática em falhas" -ForegroundColor Green
Write-Host "  ✓ Instalação simplificada" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "  1. Teste o instalador:" -ForegroundColor White
Write-Host "     msiexec /i $OutputDir\CorujaMonitorProbe-$Version.msi" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Após instalar, execute o teste:" -ForegroundColor White
Write-Host "     $OutputDir\testar-instalacao.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Distribua o MSI para os clientes" -ForegroundColor White
Write-Host ""
Write-Host "ASSINATURA DIGITAL (Opcional):" -ForegroundColor Cyan
Write-Host "  .\sign-msi.ps1 -MsiPath $OutputDir\CorujaMonitorProbe-$Version.msi" -ForegroundColor Gray
Write-Host ""

Write-Host "Pressione ENTER para sair..."
Read-Host
