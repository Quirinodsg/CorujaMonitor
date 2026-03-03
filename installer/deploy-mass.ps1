# Script para instalação em massa do Coruja Monitor Probe
# Suporta instalação em múltiplas máquinas via rede

param(
    [Parameter(Mandatory=$true)]
    [string]$ComputersFile,
    
    [Parameter(Mandatory=$true)]
    [string]$MsiPath,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiIP,
    
    [Parameter(Mandatory=$true)]
    [string]$ProbeToken,
    
    [string]$InstallType = "WORKGROUP",
    [string]$LogPath = ".\deployment-logs",
    [switch]$Parallel,
    [int]$MaxParallel = 5
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - INSTALAÇÃO EM MASSA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivos
if (-not (Test-Path $ComputersFile)) {
    Write-Host "✗ Arquivo de computadores não encontrado: $ComputersFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $MsiPath)) {
    Write-Host "✗ Arquivo MSI não encontrado: $MsiPath" -ForegroundColor Red
    exit 1
}

# Criar diretório de logs
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath | Out-Null
}

# Ler lista de computadores
$computers = Get-Content $ComputersFile | Where-Object { $_ -and $_ -notmatch '^\s*#' }
$totalComputers = $computers.Count

Write-Host "Configuração:" -ForegroundColor Yellow
Write-Host "  Computadores: $totalComputers" -ForegroundColor White
Write-Host "  MSI: $MsiPath" -ForegroundColor White
Write-Host "  API: $ApiIP" -ForegroundColor White
Write-Host "  Tipo: $InstallType" -ForegroundColor White
Write-Host "  Paralelo: $Parallel" -ForegroundColor White
Write-Host ""

# Função para instalar em um computador
function Install-OnComputer {
    param(
        [string]$ComputerName,
        [string]$MsiPath,
        [string]$ApiIP,
        [string]$ProbeToken,
        [string]$InstallType,
        [string]$LogPath
    )
    
    $logFile = Join-Path $LogPath "$ComputerName-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
    $result = @{
        Computer = $ComputerName
        Success = $false
        Message = ""
        Duration = 0
    }
    
    $startTime = Get-Date
    
    try {
        # Testar conectividade
        Write-Host "[$ComputerName] Testando conectividade..." -ForegroundColor Gray
        if (-not (Test-Connection -ComputerName $ComputerName -Count 1 -Quiet)) {
            throw "Computador não responde ao ping"
        }
        
        # Copiar MSI
        Write-Host "[$ComputerName] Copiando MSI..." -ForegroundColor Gray
        $remotePath = "\\$ComputerName\C$\Temp\CorujaProbe.msi"
        $remoteDir = Split-Path $remotePath -Parent
        
        if (-not (Test-Path $remoteDir)) {
            New-Item -ItemType Directory -Path $remoteDir -Force | Out-Null
        }
        
        Copy-Item -Path $MsiPath -Destination $remotePath -Force
        
        # Instalar remotamente
        Write-Host "[$ComputerName] Instalando..." -ForegroundColor Gray
        $installCmd = "msiexec /i C:\Temp\CorujaProbe.msi /quiet /qn API_IP=$ApiIP PROBE_TOKEN=$ProbeToken INSTALL_TYPE=$InstallType /l*v C:\Temp\coruja-install.log"
        
        $session = New-PSSession -ComputerName $ComputerName -ErrorAction Stop
        Invoke-Command -Session $session -ScriptBlock {
            param($cmd)
            cmd /c $cmd
        } -ArgumentList $installCmd
        
        # Aguardar instalação
        Start-Sleep -Seconds 30
        
        # Verificar instalação
        $installed = Invoke-Command -Session $session -ScriptBlock {
            Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*Coruja*" }
        }
        
        Remove-PSSession $session
        
        if ($installed) {
            $result.Success = $true
            $result.Message = "Instalação concluída com sucesso"
            Write-Host "[$ComputerName] ✓ Sucesso" -ForegroundColor Green
        } else {
            throw "Instalação não detectada após conclusão"
        }
        
    } catch {
        $result.Success = $false
        $result.Message = $_.Exception.Message
        Write-Host "[$ComputerName] ✗ Erro: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $result.Duration = ((Get-Date) - $startTime).TotalSeconds
    
    # Salvar log
    $result | ConvertTo-Json | Out-File -FilePath $logFile
    
    return $result
}

# Executar instalação
$results = @()
$successCount = 0
$failCount = 0

if ($Parallel) {
    Write-Host "Iniciando instalação paralela (máx: $MaxParallel)..." -ForegroundColor Yellow
    Write-Host ""
    
    $jobs = @()
    foreach ($computer in $computers) {
        # Aguardar se atingiu limite de jobs paralelos
        while ((Get-Job -State Running).Count -ge $MaxParallel) {
            Start-Sleep -Seconds 2
        }
        
        $job = Start-Job -ScriptBlock ${function:Install-OnComputer} -ArgumentList @(
            $computer, $MsiPath, $ApiIP, $ProbeToken, $InstallType, $LogPath
        )
        $jobs += $job
    }
    
    # Aguardar todos os jobs
    Write-Host "Aguardando conclusão de todos os jobs..." -ForegroundColor Yellow
    $jobs | Wait-Job | Out-Null
    
    # Coletar resultados
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job
        $results += $result
        
        if ($result.Success) {
            $successCount++
        } else {
            $failCount++
        }
        
        Remove-Job -Job $job
    }
    
} else {
    Write-Host "Iniciando instalação sequencial..." -ForegroundColor Yellow
    Write-Host ""
    
    $current = 0
    foreach ($computer in $computers) {
        $current++
        Write-Host "[$current/$totalComputers] Processando $computer..." -ForegroundColor Cyan
        
        $result = Install-OnComputer -ComputerName $computer `
                                     -MsiPath $MsiPath `
                                     -ApiIP $ApiIP `
                                     -ProbeToken $ProbeToken `
                                     -InstallType $InstallType `
                                     -LogPath $LogPath
        
        $results += $result
        
        if ($result.Success) {
            $successCount++
        } else {
            $failCount++
        }
        
        Write-Host ""
    }
}

# Relatório final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RELATÓRIO FINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total de computadores: $totalComputers" -ForegroundColor White
Write-Host "Sucesso: $successCount" -ForegroundColor Green
Write-Host "Falhas: $failCount" -ForegroundColor Red
Write-Host ""

# Mostrar falhas
if ($failCount -gt 0) {
    Write-Host "Computadores com falha:" -ForegroundColor Red
    $results | Where-Object { -not $_.Success } | ForEach-Object {
        Write-Host "  - $($_.Computer): $($_.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Salvar relatório
$reportPath = Join-Path $LogPath "deployment-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$results | ConvertTo-Json | Out-File -FilePath $reportPath

Write-Host "Relatório salvo em: $reportPath" -ForegroundColor White
Write-Host ""

# Estatísticas
$avgDuration = ($results | Measure-Object -Property Duration -Average).Average
Write-Host "Tempo médio por instalação: $([math]::Round($avgDuration, 2)) segundos" -ForegroundColor White
Write-Host ""

Write-Host "Pressione ENTER para sair..."
Read-Host
