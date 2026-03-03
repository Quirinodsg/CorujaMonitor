#!/bin/bash
# Build AppImage for Coruja Monitoring (Universal Linux)

set -e

VERSION=${1:-"1.0.0"}
APPDIR="CorujaMonitoring.AppDir"

echo "========================================="
echo "Building AppImage"
echo "Version: $VERSION"
echo "========================================="

# Baixar appimagetool se não existir
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Baixando appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Criar estrutura AppDir
rm -rf ${APPDIR}
mkdir -p ${APPDIR}/usr/bin
mkdir -p ${APPDIR}/usr/lib
mkdir -p ${APPDIR}/usr/share/applications
mkdir -p ${APPDIR}/usr/share/icons/hicolor/256x256/apps

# Copiar aplicação
echo "Copiando arquivos..."
cp -r api probe frontend ai-agent worker ${APPDIR}/usr/bin/
cp docker-compose.yml .env.example ${APPDIR}/usr/bin/
echo "${VERSION}" > ${APPDIR}/usr/bin/version.txt

# Script de execução principal
cat > ${APPDIR}/AppRun << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
cd "$APPDIR/usr/bin"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    zenity --error --text="Python 3 não encontrado!\nInstale Python 3.9 ou superior." 2>/dev/null || \
    echo "ERRO: Python 3 não encontrado. Instale Python 3.9 ou superior."
    exit 1
fi

# Verificar dependências
if [ ! -d "$HOME/.coruja/venv" ]; then
    echo "Primeira execução - instalando dependências..."
    mkdir -p "$HOME/.coruja"
    python3 -m venv "$HOME/.coruja/venv"
    source "$HOME/.coruja/venv/bin/activate"
    pip install -r api/requirements.txt --quiet
else
    source "$HOME/.coruja/venv/bin/activate"
fi

# Iniciar aplicação
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

python3 probe/probe_core.py &
PROBE_PID=$!

python3 ai-agent/main.py &
AI_PID=$!

# Abrir navegador
sleep 3
xdg-open http://localhost:3000 2>/dev/null || \
firefox http://localhost:3000 2>/dev/null || \
google-chrome http://localhost:3000 2>/dev/null

# Aguardar
wait $API_PID $PROBE_PID $AI_PID
EOF

chmod +x ${APPDIR}/AppRun

# Desktop entry
cat > ${APPDIR}/coruja-monitoring.desktop << EOF
[Desktop Entry]
Name=Coruja Monitoring
Exec=AppRun
Icon=coruja-monitoring
Type=Application
Categories=System;Monitor;Network;
Terminal=false
Comment=Sistema de Monitoramento de Infraestrutura com IA
EOF

# Link simbólico para desktop entry
ln -sf usr/share/applications/coruja-monitoring.desktop ${APPDIR}/

# Ícone (placeholder)
cat > ${APPDIR}/coruja-monitoring.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <circle cx="128" cy="128" r="120" fill="#3b82f6"/>
  <text x="128" y="160" font-size="120" text-anchor="middle" fill="white">🦉</text>
</svg>
EOF

ln -sf coruja-monitoring.svg ${APPDIR}/.DirIcon

# Gerar AppImage
echo "Gerando AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage ${APPDIR} CorujaMonitoring-${VERSION}-x86_64.AppImage

echo "✓ AppImage criado: CorujaMonitoring-${VERSION}-x86_64.AppImage"
ls -lh CorujaMonitoring-${VERSION}-x86_64.AppImage

echo ""
echo "Para executar:"
echo "  chmod +x CorujaMonitoring-${VERSION}-x86_64.AppImage"
echo "  ./CorujaMonitoring-${VERSION}-x86_64.AppImage"
