#!/bin/bash
# Build Debian Package (.deb) for Coruja Monitoring

set -e

VERSION=${1:-"1.0.0"}
ARCH="amd64"
PKG_NAME="coruja-monitoring_${VERSION}_${ARCH}"

echo "========================================="
echo "Building Debian Package"
echo "Version: $VERSION"
echo "========================================="

# Criar estrutura de diretórios
mkdir -p ${PKG_NAME}/DEBIAN
mkdir -p ${PKG_NAME}/opt/coruja
mkdir -p ${PKG_NAME}/etc/systemd/system
mkdir -p ${PKG_NAME}/usr/share/applications
mkdir -p ${PKG_NAME}/usr/share/icons/hicolor/256x256/apps

# Control file
cat > ${PKG_NAME}/DEBIAN/control << EOF
Package: coruja-monitoring
Version: ${VERSION}
Section: admin
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.9), python3-pip, nodejs (>= 16)
Maintainer: Coruja Team <contato@coruja.com>
Description: Sistema de Monitoramento de Infraestrutura com IA
 Coruja Monitoring é uma solução completa de monitoramento de infraestrutura
 com recursos de IA/ML para análise preditiva e auto-remediação.
 .
 Recursos principais:
  - Monitoramento agentless (WMI, SNMP, SSH)
  - Dashboard em tempo real estilo NOC
  - IA para análise de incidentes
  - Integração com TOPdesk, GLPI
  - Suporte a Kubernetes
EOF

# Postinst script
cat > ${PKG_NAME}/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

# Criar usuário coruja
if ! id -u coruja > /dev/null 2>&1; then
    useradd -r -s /bin/false -d /opt/coruja coruja
fi

# Instalar dependências Python
cd /opt/coruja
pip3 install -r api/requirements.txt --quiet

# Configurar permissões
chown -R coruja:coruja /opt/coruja
chmod +x /opt/coruja/start.sh

# Habilitar e iniciar serviço
systemctl daemon-reload
systemctl enable coruja.service
systemctl start coruja.service

echo "✓ Coruja Monitoring instalado com sucesso!"
echo "  Acesse: http://localhost:3000"
echo "  Logs: journalctl -u coruja -f"
EOF

chmod +x ${PKG_NAME}/DEBIAN/postinst

# Prerm script
cat > ${PKG_NAME}/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

# Parar serviço
systemctl stop coruja.service || true
systemctl disable coruja.service || true
EOF

chmod +x ${PKG_NAME}/DEBIAN/prerm

# Copiar arquivos da aplicação
echo "Copiando arquivos..."
cp -r api probe frontend ai-agent worker ${PKG_NAME}/opt/coruja/
cp docker-compose.yml .env.example ${PKG_NAME}/opt/coruja/
cp version.txt ${PKG_NAME}/opt/coruja/ 2>/dev/null || echo "${VERSION}" > ${PKG_NAME}/opt/coruja/version.txt

# Script de inicialização
cat > ${PKG_NAME}/opt/coruja/start.sh << 'EOF'
#!/bin/bash
cd /opt/coruja

# Iniciar API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Iniciar Frontend (se necessário)
if [ -d "frontend/build" ]; then
    cd frontend
    npx serve -s build -l 3000 &
    cd ..
fi

# Iniciar Probe
python3 probe/probe_core.py &

# Iniciar AI Agent
python3 ai-agent/main.py &

wait
EOF

chmod +x ${PKG_NAME}/opt/coruja/start.sh

# Systemd service
cat > ${PKG_NAME}/etc/systemd/system/coruja.service << EOF
[Unit]
Description=Coruja Monitoring System
After=network.target

[Service]
Type=simple
User=coruja
WorkingDirectory=/opt/coruja
ExecStart=/opt/coruja/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Desktop entry
cat > ${PKG_NAME}/usr/share/applications/coruja-monitoring.desktop << EOF
[Desktop Entry]
Name=Coruja Monitoring
Comment=Sistema de Monitoramento de Infraestrutura
Exec=xdg-open http://localhost:3000
Icon=coruja-monitoring
Terminal=false
Type=Application
Categories=System;Monitor;Network;
EOF

# Ícone (placeholder - substituir por ícone real)
echo "Criando ícone placeholder..."
# TODO: Adicionar ícone real aqui

# Build package
echo "Construindo pacote..."
dpkg-deb --build ${PKG_NAME}

echo "✓ Pacote Debian criado: ${PKG_NAME}.deb"
ls -lh ${PKG_NAME}.deb
