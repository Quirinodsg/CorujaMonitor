# Plano de Modernização do Sistema Coruja
**Data:** 02/03/2026

## 1. Layout Responsivo e Grid Flexível

### Estrutura Base
```css
/* Grid responsivo para widgets de monitoramento */
.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

/* Sidebar colapsável */
.sidebar {
  transition: width 0.3s ease;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 60px;
  }
  .sidebar.expanded {
    width: 250px;
  }
}

@media (max-width: 768px) {
  .monitoring-grid {
    grid-template-columns: 1fr;
  }
}
```

### Breakpoints Definidos
- Ultrawide: > 2560px
- Desktop: 1920px - 2560px
- Laptop: 1366px - 1920px
- Tablet: 768px - 1366px
- Mobile: < 768px

## 2. Tema Dark Moderno com Glassmorphism

### Paleta de Cores
```css
:root {
  /* Backgrounds */
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  
  /* Glassmorphism */
  --glass-bg: rgba(30, 41, 59, 0.7);
  --glass-border: rgba(148, 163, 184, 0.1);
  
  /* Status Colors (Neon Suave) */
  --status-online: #10b981;      /* Verde esmeralda */
  --status-processing: #3b82f6;  /* Azul elétrico */
  --status-warning: #f59e0b;     /* Âmbar */
  --status-critical: #ef4444;    /* Coral/Vermelho */
  
  /* Typography */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Card com Glassmorphism */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
  border-color: rgba(148, 163, 184, 0.2);
}
```

### Tipografia Hierárquica
```css
h1 { font-size: 2.5rem; font-weight: 700; letter-spacing: -0.02em; }
h2 { font-size: 2rem; font-weight: 600; }
h3 { font-size: 1.5rem; font-weight: 600; }
.metric-value { font-size: 3rem; font-weight: 700; line-height: 1; }
.metric-label { font-size: 0.875rem; opacity: 0.7; text-transform: uppercase; }
```

## 3. Sistema de Atualização Automática

### Arquitetura
```
┌─────────────────────────────────────────┐
│  Frontend: Settings > Updates          │
│  - Check for Updates Button             │
│  - Auto-check on startup (optional)     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend: /api/updates                  │
│  - GET /check: Compare versions         │
│  - POST /download: Fetch release        │
│  - POST /apply: Install & restart       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  GitHub/GitLab API                      │
│  - Fetch latest release tag             │
│  - Download release assets              │
│  - Parse changelog                      │
└─────────────────────────────────────────┘
```

### Implementação Backend (Python/FastAPI)
```python
# api/routers/auto_update.py
from fastapi import APIRouter, HTTPException
import requests
import semver
import subprocess
import os

router = APIRouter(prefix="/api/updates", tags=["updates"])

GITHUB_REPO = "seu-usuario/coruja-monitoring"
CURRENT_VERSION = "1.0.0"  # Ler de version.txt

@router.get("/check")
async def check_updates():
    """Verifica se há atualizações disponíveis"""
    try:
        response = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        latest = response.json()
        
        latest_version = latest["tag_name"].lstrip("v")
        current = semver.VersionInfo.parse(CURRENT_VERSION)
        remote = semver.VersionInfo.parse(latest_version)
        
        return {
            "update_available": remote > current,
            "current_version": CURRENT_VERSION,
            "latest_version": latest_version,
            "changelog": latest["body"],
            "download_url": latest["assets"][0]["browser_download_url"],
            "published_at": latest["published_at"]
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao verificar atualizações: {str(e)}")

@router.post("/download")
async def download_update(download_url: str):
    """Baixa a atualização"""
    try:
        response = requests.get(download_url, stream=True)
        update_file = "updates/coruja-update.zip"
        
        os.makedirs("updates", exist_ok=True)
        with open(update_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return {"status": "downloaded", "file": update_file}
    except Exception as e:
        raise HTTPException(500, f"Erro ao baixar atualização: {str(e)}")

@router.post("/apply")
async def apply_update():
    """Aplica a atualização e reinicia o serviço"""
    try:
        # Extrair arquivos
        subprocess.run(["powershell", "-Command", 
                       "Expand-Archive -Path updates/coruja-update.zip -DestinationPath . -Force"])
        
        # Executar script de atualização
        subprocess.Popen(["powershell", "-File", "update_and_restart.ps1"])
        
        return {"status": "updating", "message": "Sistema será reiniciado em 5 segundos"}
    except Exception as e:
        raise HTTPException(500, f"Erro ao aplicar atualização: {str(e)}")
```

### Script de Atualização (PowerShell)
```powershell
# update_and_restart.ps1
Write-Host "Aguardando 5 segundos para finalizar processos..."
Start-Sleep -Seconds 5

# Parar serviços
Stop-Process -Name "coruja-api" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "coruja-probe" -Force -ErrorAction SilentlyContinue

# Backup da versão atual
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item -Path "api" -Destination "backups/api_$timestamp" -Recurse -Force
Copy-Item -Path "probe" -Destination "backups/probe_$timestamp" -Recurse -Force

# Aplicar novos arquivos (já extraídos)
Write-Host "Arquivos atualizados com sucesso!"

# Reiniciar serviços
Start-Process -FilePath "restart.bat" -NoNewWindow

Write-Host "Sistema atualizado e reiniciado!"
```

## 4. Empacotamento Profissional

### 4.1 Windows MSI (WiX Toolset)

#### Estrutura do Projeto
```xml
<!-- installer/coruja.wxs -->
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Coruja Monitoring System" 
           Language="1033" 
           Version="1.0.0" 
           Manufacturer="Sua Empresa"
           UpgradeCode="YOUR-GUID-HERE">
    
    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />
    
    <Feature Id="ProductFeature" Title="Coruja Monitoring" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentGroupRef Id="ServiceComponents" />
    </Feature>
    
    <!-- Diretórios -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFiles64Folder">
        <Directory Id="INSTALLFOLDER" Name="Coruja Monitoring" />
      </Directory>
    </Directory>
    
    <!-- Componentes -->
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable">
        <File Source="$(var.SourceDir)\coruja-api.exe" KeyPath="yes" />
        <File Source="$(var.SourceDir)\coruja-probe.exe" />
      </Component>
    </ComponentGroup>
    
    <!-- Serviços Windows -->
    <ComponentGroup Id="ServiceComponents" Directory="INSTALLFOLDER">
      <Component Id="CorujaService">
        <ServiceInstall Id="CorujaAPIService"
                       Name="CorujaAPI"
                       DisplayName="Coruja Monitoring API"
                       Description="Serviço de API do Coruja Monitoring"
                       Type="ownProcess"
                       Start="auto"
                       ErrorControl="normal"
                       Account="LocalSystem" />
        <ServiceControl Id="StartCorujaService" 
                       Name="CorujaAPI" 
                       Start="install" 
                       Stop="both" 
                       Remove="uninstall" />
      </Component>
    </ComponentGroup>
  </Product>
</Wix>
```

#### Build Script
```powershell
# build-msi.ps1
$ErrorActionPreference = "Stop"

# Compilar aplicação
Write-Host "Compilando aplicação..."
pyinstaller --onefile --windowed api/main.py -n coruja-api
pyinstaller --onefile probe/probe_core.py -n coruja-probe

# Compilar instalador WiX
Write-Host "Gerando instalador MSI..."
candle.exe installer/coruja.wxs -out installer/coruja.wixobj
light.exe installer/coruja.wixobj -out installer/CorujaMonitoring-1.0.0.msi

Write-Host "Instalador MSI criado: installer/CorujaMonitoring-1.0.0.msi"
```

### 4.2 Linux (DEB/RPM/AppImage)

#### Debian Package (.deb)
```bash
# build-deb.sh
#!/bin/bash

VERSION="1.0.0"
ARCH="amd64"
PKG_NAME="coruja-monitoring_${VERSION}_${ARCH}"

# Criar estrutura de diretórios
mkdir -p ${PKG_NAME}/DEBIAN
mkdir -p ${PKG_NAME}/opt/coruja
mkdir -p ${PKG_NAME}/etc/systemd/system

# Control file
cat > ${PKG_NAME}/DEBIAN/control << EOF
Package: coruja-monitoring
Version: ${VERSION}
Section: admin
Priority: optional
Architecture: ${ARCH}
Maintainer: Sua Empresa <contato@empresa.com>
Description: Sistema de Monitoramento Coruja
 Sistema completo de monitoramento de infraestrutura com IA
EOF

# Copiar arquivos
cp -r api probe frontend ${PKG_NAME}/opt/coruja/

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

[Install]
WantedBy=multi-user.target
EOF

# Build package
dpkg-deb --build ${PKG_NAME}
```

#### AppImage (Universal Linux)
```bash
# build-appimage.sh
#!/bin/bash

# Usar appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Criar AppDir
mkdir -p CorujaMonitoring.AppDir/usr/bin
mkdir -p CorujaMonitoring.AppDir/usr/share/applications
mkdir -p CorujaMonitoring.AppDir/usr/share/icons

# Desktop entry
cat > CorujaMonitoring.AppDir/coruja-monitoring.desktop << EOF
[Desktop Entry]
Name=Coruja Monitoring
Exec=coruja
Icon=coruja
Type=Application
Categories=System;Monitor;
EOF

# Copiar arquivos
cp -r api probe frontend CorujaMonitoring.AppDir/usr/bin/

# Gerar AppImage
./appimagetool-x86_64.AppImage CorujaMonitoring.AppDir CorujaMonitoring-1.0.0-x86_64.AppImage
```

### 4.3 macOS (.DMG/.PKG)

```bash
# build-dmg.sh
#!/bin/bash

# Criar estrutura .app
mkdir -p "Coruja Monitoring.app/Contents/MacOS"
mkdir -p "Coruja Monitoring.app/Contents/Resources"

# Info.plist
cat > "Coruja Monitoring.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>coruja</string>
    <key>CFBundleIdentifier</key>
    <string>com.empresa.coruja</string>
    <key>CFBundleName</key>
    <string>Coruja Monitoring</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
</dict>
</plist>
EOF

# Criar DMG
hdiutil create -volname "Coruja Monitoring" -srcfolder "Coruja Monitoring.app" -ov -format UDZO CorujaMonitoring-1.0.0.dmg
```

## 5. CI/CD com GitHub Actions

```yaml
# .github/workflows/release.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r api/requirements.txt
          pip install pyinstaller
      
      - name: Build MSI
        run: |
          powershell -File build-msi.ps1
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: installer/*.msi

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build DEB
        run: |
          chmod +x build-deb.sh
          ./build-deb.sh
      
      - name: Build AppImage
        run: |
          chmod +x build-appimage.sh
          ./build-appimage.sh
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-packages
          path: |
            *.deb
            *.AppImage

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build DMG
        run: |
          chmod +x build-dmg.sh
          ./build-dmg.sh
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: macos-installer
          path: *.dmg

  create-release:
    needs: [build-windows, build-linux, build-macos]
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            windows-installer/*.msi
            linux-packages/*.deb
            linux-packages/*.AppImage
            macos-installer/*.dmg
          body_path: CHANGELOG.md
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 6. Próximos Passos

1. **Fase 1 - Layout Responsivo** (2-3 dias)
   - Implementar grid flexível
   - Adicionar media queries
   - Testar em diferentes resoluções

2. **Fase 2 - Tema Dark Moderno** (2-3 dias)
   - Aplicar glassmorphism
   - Implementar paleta de cores
   - Ajustar tipografia

3. **Fase 3 - Sistema de Atualização** (3-4 dias)
   - Backend de verificação
   - Interface de atualização
   - Scripts de aplicação

4. **Fase 4 - Empacotamento** (4-5 dias)
   - Configurar WiX para Windows
   - Scripts para Linux
   - Configurar CI/CD

5. **Fase 5 - Testes e Documentação** (2-3 dias)
   - Testar instaladores
   - Documentar processo
   - Criar guias de usuário

**Tempo Total Estimado:** 13-18 dias úteis
