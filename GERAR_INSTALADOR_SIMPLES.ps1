# Gerar Instalador Simples (sem comandos de rede)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📦 GERAR INSTALADOR SIMPLES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $innoSetupPath)) {
    Write-Host "❌ Inno Setup não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Procurando em outros locais..." -ForegroundColor Yellow
    
    $alternativePaths = @(
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
    )
    
    foreach ($path in $alternativePaths) {
        if (Test-Path $path) {
            $innoSetupPath = $path
            Write-Host "✅ Encontrado em: $path" -ForegroundColor Green
            break
        }
    }
    
    if (-not (Test-Path $innoSetupPath)) {
        Write-Host ""
        Write-Host "❌ Inno Setup não encontrado em nenhum local!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Instale o Inno Setup 6:" -ForegroundColor Yellow
        Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Pressione ENTER para sair..."
        Read-Host
        exit 1
    }
}

Write-Host "✅ Inno Setup encontrado: $innoSetupPath" -ForegroundColor Green
Write-Host ""

Set-Location "C:\Users\andre.quirino\Coruja Monitor\installer"

Write-Host "🔨 Compilando instalador simples..." -ForegroundColor Yellow
Write-Host ""

& $innoSetupPath "CorujaProbe_Simples.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ INSTALADOR GERADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Arquivo gerado:" -ForegroundColor Cyan
    Write-Host "   installer\output\CorujaMonitorProbe-Simples-v1.0.0.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 DIFERENÇAS DA VERSÃO SIMPLES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   ✅ NÃO executa comandos de rede (evita erro 8235)" -ForegroundColor Green
    Write-Host "   ✅ NÃO baixa Python automaticamente" -ForegroundColor Green
    Write-Host "   ✅ NÃO configura firewall automaticamente" -ForegroundColor Green
    Write-Host "   ✅ Apenas copia arquivos e cria atalhos" -ForegroundColor Green
    Write-Host "   ✅ Abre instruções pós-instalação" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 INSTRUÇÕES PÓS-INSTALAÇÃO:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   1. Instalar Python manualmente" -ForegroundColor White
    Write-Host "   2. Instalar dependências: pip install psutil httpx pywin32 pysnmp pyyaml" -ForegroundColor White
    Write-Host "   3. Configurar firewall: netsh advfirewall firewall set rule..." -ForegroundColor White
    Write-Host "   4. Configurar probe: configurar_probe.bat" -ForegroundColor White
    Write-Host "   5. Instalar serviço: install.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 QUANDO USAR:" -ForegroundColor Yellow
    Write-Host "   • Servidores com Active Directory" -ForegroundColor White
    Write-Host "   • Ambientes corporativos com GPO restritivo" -ForegroundColor White
    Write-Host "   • Quando o instalador completo dá erro 8235" -ForegroundColor White
    Write-Host ""
    
    # Abrir pasta output
    explorer.exe "output"
    
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ ERRO NA COMPILAÇÃO!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique os erros acima." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pressione ENTER para sair..."
Read-Host
