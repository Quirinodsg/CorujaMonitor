# Script de Scan de Segurança Completo
# Executa todos os scans de segurança do Coruja Monitor

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - SECURITY SCAN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
$hasErrors = $false

# 1. Scan de Dependências Python
Write-Host "1️⃣  Scanning Python dependencies..." -ForegroundColor Cyan
Write-Host ""

try {
    Push-Location api
    
    # Instalar safety se necessário
    pip show safety | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Installing safety..." -ForegroundColor Yellow
        pip install safety | Out-Null
    }
    
    # Executar safety check
    $safetyOutput = safety check 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ No vulnerabilities found in Python dependencies" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Vulnerabilities found in Python dependencies!" -ForegroundColor Red
        Write-Host $safetyOutput -ForegroundColor Yellow
        $hasErrors = $true
    }
    
    Pop-Location
} catch {
    Write-Host "   ❌ Error scanning Python dependencies: $_" -ForegroundColor Red
    $hasErrors = $true
}

Write-Host ""

# 2. Scan de Dependências Node.js
Write-Host "2️⃣  Scanning Node.js dependencies..." -ForegroundColor Cyan
Write-Host ""

try {
    Push-Location frontend
    
    # Executar npm audit
    $auditOutput = npm audit 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ No vulnerabilities found in Node.js dependencies" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Vulnerabilities found in Node.js dependencies!" -ForegroundColor Red
        Write-Host $auditOutput -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   💡 Run 'npm audit fix' to fix automatically" -ForegroundColor Cyan
        $hasErrors = $true
    }
    
    Pop-Location
} catch {
    Write-Host "   ❌ Error scanning Node.js dependencies: $_" -ForegroundColor Red
    $hasErrors = $true
}

Write-Host ""

# 3. Verificação de Integridade
Write-Host "3️⃣  Checking file integrity..." -ForegroundColor Cyan
Write-Host ""

try {
    if (Test-Path "checksums.json") {
        python security/integrity_check.py verify
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ File integrity verified" -ForegroundColor Green
        } elseif ($LASTEXITCODE -eq 2) {
            Write-Host "   ⚠️  New files detected" -ForegroundColor Yellow
        } else {
            Write-Host "   ❌ Integrity check failed!" -ForegroundColor Red
            $hasErrors = $true
        }
    } else {
        Write-Host "   ⚠️  No checksums file found. Generating..." -ForegroundColor Yellow
        python security/integrity_check.py generate
        Write-Host "   ✅ Checksums generated" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Error checking integrity: $_" -ForegroundColor Red
    $hasErrors = $true
}

Write-Host ""

# 4. Scan de Secrets
Write-Host "4️⃣  Scanning for exposed secrets..." -ForegroundColor Cyan
Write-Host ""

try {
    # Verificar se há credenciais expostas
    $secretPatterns = @(
        "password\s*=\s*['\"](?!.*\{\{)[^'\"]+['\"]",
        "api[_-]?key\s*=\s*['\"](?!.*\{\{)[^'\"]+['\"]",
        "secret\s*=\s*['\"](?!.*\{\{)[^'\"]+['\"]",
        "token\s*=\s*['\"](?!.*\{\{)[^'\"]+['\"]"
    )
    
    $foundSecrets = $false
    
    foreach ($pattern in $secretPatterns) {
        $matches = Get-ChildItem -Recurse -Include *.py,*.js,*.jsx,*.ts,*.tsx,*.json -Exclude node_modules,__pycache__,.git | 
            Select-String -Pattern $pattern -CaseSensitive:$false
        
        if ($matches) {
            if (-not $foundSecrets) {
                Write-Host "   ❌ Potential secrets found in code!" -ForegroundColor Red
                $foundSecrets = $true
                $hasErrors = $true
            }
            
            foreach ($match in $matches) {
                Write-Host "      $($match.Path):$($match.LineNumber)" -ForegroundColor Yellow
            }
        }
    }
    
    if (-not $foundSecrets) {
        Write-Host "   ✅ No exposed secrets found" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Error scanning for secrets: $_" -ForegroundColor Red
    $hasErrors = $true
}

Write-Host ""

# 5. Windows Defender Scan (opcional)
Write-Host "5️⃣  Windows Defender scan..." -ForegroundColor Cyan
Write-Host ""

try {
    $currentPath = Get-Location
    
    Write-Host "   Starting quick scan of current directory..." -ForegroundColor Gray
    Write-Host "   (This may take a few minutes)" -ForegroundColor Gray
    
    Start-MpScan -ScanType QuickScan -ScanPath $currentPath -ErrorAction SilentlyContinue
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Windows Defender scan completed - No threats found" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Windows Defender scan completed with warnings" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not run Windows Defender scan: $_" -ForegroundColor Yellow
    Write-Host "   (This is optional and can be skipped)" -ForegroundColor Gray
}

Write-Host ""

# 6. Docker Security (se Docker estiver rodando)
Write-Host "6️⃣  Docker security check..." -ForegroundColor Cyan
Write-Host ""

try {
    docker ps | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        # Verificar containers rodando como root
        $rootContainers = docker ps --format "{{.Names}}" | ForEach-Object {
            $user = docker exec $_ whoami 2>$null
            if ($user -eq "root") {
                $_
            }
        }
        
        if ($rootContainers) {
            Write-Host "   ⚠️  Containers running as root:" -ForegroundColor Yellow
            $rootContainers | ForEach-Object {
                Write-Host "      - $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ✅ No containers running as root" -ForegroundColor Green
        }
        
        # Verificar portas expostas
        Write-Host ""
        Write-Host "   Exposed ports:" -ForegroundColor Gray
        docker ps --format "{{.Names}}: {{.Ports}}" | ForEach-Object {
            Write-Host "      $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ⚠️  Docker is not running" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not check Docker security: $_" -ForegroundColor Yellow
}

Write-Host ""

# Resumo Final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SCAN SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($hasErrors) {
    Write-Host "❌ SECURITY ISSUES DETECTED!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please review the issues above and take action." -ForegroundColor Yellow
    Write-Host ""
    exit 1
} else {
    Write-Host "✅ ALL SECURITY CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your system is secure and ready for deployment." -ForegroundColor Green
    Write-Host ""
    exit 0
}
