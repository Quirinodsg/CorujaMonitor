#!/bin/bash

echo "========================================"
echo "📦 COMMIT INSTALADOR + BASE 109 ITENS"
echo "========================================"
echo ""

cd "/c/Users/andre.quirino/Coruja Monitor"

echo "📁 Adicionando arquivos ao Git..."
echo ""

# Instalador Inno Setup
echo "   • Instalador Inno Setup (EXE)"
git add installer/CorujaProbe.iss
git add installer/output/CorujaMonitorProbe-Setup-v1.0.0.exe
git add installer/output/InstalarCorujaProbe.bat
git add installer/output/DesinstalarCorujaProbe.bat
git add installer/output/README.txt
git add GERAR_INSTALADOR_INNO.ps1
git add GERAR_INSTALADOR_AGORA.ps1

# Scripts MSI/WiX
echo "   • Scripts MSI/WiX"
git add installer/CorujaProbe_Complete.wxs
git add installer/build-msi-complete.ps1
git add installer/gerar_msi_completo.ps1

# Base de Conhecimento 109 itens
echo "   • Base de Conhecimento 109 itens"
git add api/popular_109_itens_completo.py
git add popular_base_109_itens.sh
git add EXECUTAR_POPULAR_109_ITENS.txt
git add RESUMO_POPULAR_109_ITENS.md 2>/dev/null || true
git add commit_popular_109_itens.ps1 2>/dev/null || true

# Documentação
echo "   • Documentação"
git add RESOLVER_ERRO_POLITICAS_MSI.md
git add RESUMO_MSI_COMPLETO_E_BASE_109.md
git add CRIAR_MSI_COMPLETO.txt 2>/dev/null || true
git add commit_msi_completo.ps1 2>/dev/null || true
git add COMMIT_INSTALADOR_COMPLETO.ps1
git add COMMIT_INSTALADOR_GIT_BASH.sh

echo ""
echo "💾 Fazendo commit..."

git commit -m "feat: Instalador EXE profissional com Python + Base 109 itens

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
- Erro: system administrator has set policies to prevent installation
- Instalação em ambientes corporativos com GPO restritivo
- Falta de Python no sistema (instala automaticamente)
- Base de conhecimento incompleta (restaura 109 itens)
- Deploy em massa via GPO/SCCM/Intune

TAMANHO INSTALADOR: ~25 MB (EXE) + download Python (~25 MB)
COMPATIBILIDADE: Windows 7/Server 2008 R2 ou superior (64-bit)
REQUISITOS: Privilégios de administrador, conexão internet (para Python)"

echo ""
echo "🚀 Enviando para GitHub..."
git push origin master

echo ""
echo "========================================"
echo "✅ COMMIT CONCLUÍDO!"
echo "========================================"
echo ""
echo "📦 ARQUIVOS ENVIADOS:"
echo ""
echo "INSTALADOR:"
echo "   • CorujaMonitorProbe-Setup-v1.0.0.exe (EXE profissional)"
echo "   • InstalarCorujaProbe.bat (alternativa BAT)"
echo "   • DesinstalarCorujaProbe.bat"
echo "   • README.txt"
echo ""
echo "SCRIPTS:"
echo "   • GERAR_INSTALADOR_INNO.ps1"
echo "   • GERAR_INSTALADOR_AGORA.ps1"
echo "   • installer/CorujaProbe.iss"
echo ""
echo "BASE 109 ITENS:"
echo "   • api/popular_109_itens_completo.py"
echo "   • popular_base_109_itens.sh"
echo ""
echo "DOCUMENTAÇÃO:"
echo "   • RESOLVER_ERRO_POLITICAS_MSI.md"
echo "   • RESUMO_MSI_COMPLETO_E_BASE_109.md"
echo "   • EXECUTAR_POPULAR_109_ITENS.txt"
echo ""
echo "🌐 PRÓXIMOS PASSOS:"
echo ""
echo "1. DISTRIBUIR INSTALADOR:"
echo "   • Baixe do GitHub: installer/output/CorujaMonitorProbe-Setup-v1.0.0.exe"
echo "   • Envie para clientes"
echo "   • Execute como Administrador"
echo ""
echo "2. POPULAR BASE NO LINUX:"
echo "   cd /home/administrador/CorujaMonitor"
echo "   git pull"
echo "   chmod +x popular_base_109_itens.sh"
echo "   ./popular_base_109_itens.sh"
echo ""
echo "Pressione ENTER para sair..."
read
