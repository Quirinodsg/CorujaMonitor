# Commit Instalador Completo + Base 109 Itens

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📦 COMMIT INSTALADOR + BASE 109 ITENS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\andre.quirino\Coruja Monitor"

Write-Host "📁 Adicionando arquivos ao Git..." -ForegroundColor Yellow
Write-Host ""

# Instalador Inno Setup
Write-Host "   • Instalador Inno Setup (EXE)" -ForegroundColor Gray
git add installer/CorujaProbe.iss
git add installer/output/CorujaMonitorProbe-Setup-v1.0.0.exe
git add installer/output/InstalarCorujaProbe.bat
git add installer/output/DesinstalarCorujaProbe.bat
git add installer/output/README.txt
git add GERAR_INSTALADOR_INNO.ps1
git add GERAR_INSTALADOR_AGORA.ps1

# Scripts MSI/WiX
Write-Host "   • Scripts MSI/WiX" -ForegroundColor Gray
git add installer/CorujaProbe_Complete.wxs
git add installer/build-msi-complete.ps1
git add installer/gerar_msi_completo.ps1

# Base de Conhecimento 109 itens
Write-Host "   • Base de Conhecimento 109 itens" -ForegroundColor Gray
git add api/popular_109_itens_completo.py
git add popular_base_109_itens.sh
git add EXECUTAR_POPULAR_109_ITENS.txt
git add RESUMO_POPULAR_109_ITENS.md
git add commit_popular_109_itens.ps1

# Documentação
Write-Host "   • Documentação" -ForegroundColor Gray
git add RESOLVER_ERRO_POLITICAS_MSI.md
git add RESUMO_MSI_COMPLETO_E_BASE_109.md
git add CRIAR_MSI_COMPLETO.txt
git add commit_msi_completo.ps1
git add COMMIT_INSTALADOR_COMPLETO.ps1

Write-Host ""
Write-Host "💾 Fazendo commit..." -ForegroundColor Yellow

$commitMessage = @"
feat: Instalador EXE profissional com Python + Base 109 itens

INSTALADOR COMPLETO (Inno Setup):
- CorujaMonitorProbe-Setup-v1.0.0.exe (instalador EXE profissional)
- Instala Python 3.11 automaticamente se não existir
- Baixa Python de python.org durante instalação
- Instala dependências: psutil, httpx, pywin32, pysnmp, pyyaml
- Cria atalhos: Desktop + Menu Iniciar
- Configura firewall (WMI) automaticamente
- Registra no Windows (HKLM\SOFTWARE\CorujaMonitor)
- Interface gráfica profissional
- Desinstalação limpa
- Funciona igual a MSI

INSTALADOR BAT (Alternativo):
- InstalarCorujaProbe.bat (instalação via script)
- DesinstalarCorujaProbe.bat (desinstalação)
- README.txt (instruções completas)
- Mesma funcionalidade do EXE

SCRIPTS DE GERAÇÃO:
- GERAR_INSTALADOR_INNO.ps1 (compila Inno Setup)
- GERAR_INSTALADOR_AGORA.ps1 (gera BAT)
- installer/CorujaProbe.iss (script Inno Setup)
- installer/CorujaProbe_Complete.wxs (WiX para MSI)
- installer/build-msi-complete.ps1 (build WiX)

BASE DE CONHECIMENTO 109 ITENS:
- api/popular_109_itens_completo.py (script Python)
- popular_base_109_itens.sh (executor Linux)
- 109+ itens cobrindo toda infraestrutura TI
- Categorias: Windows (15), Linux (15), Docker (10), Azure (10),
  Rede (10), UPS (5), AC (5), Web (10), Windows Avançado (9),
  Linux Avançado (10), Banco de Dados (10)

DOCUMENTAÇÃO:
- RESOLVER_ERRO_POLITICAS_MSI.md (troubleshooting completo)
- RESUMO_MSI_COMPLETO_E_BASE_109.md (resumo executivo)
- CRIAR_MSI_COMPLETO.txt (guia de criação MSI)
- EXECUTAR_POPULAR_109_ITENS.txt (instruções base)
- RESUMO_POPULAR_109_ITENS.md (detalhes 109 itens)

RESOLVE:
- Erro: "system administrator has set policies to prevent installation"
- Instalação em ambientes corporativos com GPO restritivo
- Falta de Python no sistema (instala automaticamente)
- Base de conhecimento incompleta (restaura 109 itens)
- Deploy em massa via GPO/SCCM/Intune

TAMANHO INSTALADOR: ~25 MB (EXE) + download Python (~25 MB)
COMPATIBILIDADE: Windows 7/Server 2008 R2 ou superior (64-bit)
REQUISITOS: Privilégios de administrador, conexão internet (para Python)
"@

git commit -m $commitMessage

Write-Host ""
Write-Host "🚀 Enviando para GitHub..." -ForegroundColor Yellow
git push origin master

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ COMMIT CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 ARQUIVOS ENVIADOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "INSTALADOR:" -ForegroundColor Yellow
Write-Host "   • CorujaMonitorProbe-Setup-v1.0.0.exe (EXE profissional)" -ForegroundColor White
Write-Host "   • InstalarCorujaProbe.bat (alternativa BAT)" -ForegroundColor White
Write-Host "   • DesinstalarCorujaProbe.bat" -ForegroundColor White
Write-Host "   • README.txt" -ForegroundColor White
Write-Host ""
Write-Host "SCRIPTS:" -ForegroundColor Yellow
Write-Host "   • GERAR_INSTALADOR_INNO.ps1" -ForegroundColor White
Write-Host "   • GERAR_INSTALADOR_AGORA.ps1" -ForegroundColor White
Write-Host "   • installer/CorujaProbe.iss" -ForegroundColor White
Write-Host ""
Write-Host "BASE 109 ITENS:" -ForegroundColor Yellow
Write-Host "   • api/popular_109_itens_completo.py" -ForegroundColor White
Write-Host "   • popular_base_109_itens.sh" -ForegroundColor White
Write-Host ""
Write-Host "DOCUMENTAÇÃO:" -ForegroundColor Yellow
Write-Host "   • RESOLVER_ERRO_POLITICAS_MSI.md" -ForegroundColor White
Write-Host "   • RESUMO_MSI_COMPLETO_E_BASE_109.md" -ForegroundColor White
Write-Host "   • EXECUTAR_POPULAR_109_ITENS.txt" -ForegroundColor White
Write-Host ""
Write-Host "🌐 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. DISTRIBUIR INSTALADOR:" -ForegroundColor Yellow
Write-Host "   • Baixe do GitHub: installer/output/CorujaMonitorProbe-Setup-v1.0.0.exe" -ForegroundColor White
Write-Host "   • Envie para clientes" -ForegroundColor White
Write-Host "   • Execute como Administrador" -ForegroundColor White
Write-Host ""
Write-Host "2. POPULAR BASE NO LINUX:" -ForegroundColor Yellow
Write-Host "   cd /home/administrador/CorujaMonitor" -ForegroundColor White
Write-Host "   git pull" -ForegroundColor White
Write-Host "   chmod +x popular_base_109_itens.sh" -ForegroundColor White
Write-Host "   ./popular_base_109_itens.sh" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER para sair..."
Read-Host
