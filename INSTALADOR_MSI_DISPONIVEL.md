# 📦 INSTALADOR MSI DISPONÍVEL NO GIT

## ✅ MSI Enviado com Sucesso!

**Commit:** 32bc03c  
**Data:** 05/03/2026  
**Arquivo:** `installer/output/CorujaProbe.msi`  
**Tamanho:** 319 KB (319.488 bytes)

---

## 📥 Como Baixar

### Opção 1: Clone do Repositório
```bash
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd CorujaMonitor/installer/output
```

### Opção 2: Download Direto do GitHub
1. Acesse: https://github.com/Quirinodsg/CorujaMonitor
2. Navegue até: `installer/output/CorujaProbe.msi`
3. Clique em "Download" ou "Raw"

### Opção 3: Pull em Repositório Existente
```bash
cd CorujaMonitor
git pull origin master
```

O MSI estará em: `installer/output/CorujaProbe.msi`

---

## 🚀 Como Instalar

### Instalação com Interface Gráfica
1. Duplo clique em `CorujaProbe.msi`
2. Siga o assistente de instalação
3. Escolha o diretório de instalação
4. Aguarde a conclusão

### Instalação via Linha de Comando
```powershell
# Instalação interativa
msiexec /i CorujaProbe.msi

# Instalação silenciosa
msiexec /i CorujaProbe.msi /quiet /norestart

# Instalação com log
msiexec /i CorujaProbe.msi /l*v install.log
```

---

## 📋 O que o MSI Instala

### Arquivos Instalados
- `probe_core.py` - Core da probe
- `config.py` - Configuração
- `requirements.txt` - Dependências Python
- **Collectors:**
  - `system_collector.py`
  - `ping_collector.py`
  - `docker_collector.py`
  - `snmp_collector.py`
  - `kubernetes_collector.py`
  - `wmi_remote_collector.py`

### Atalhos Criados
- **Menu Iniciar > Coruja Monitor:**
  - Iniciar Coruja Probe
  - Configurar Probe
  - Desinstalar Coruja Probe

### Diretório de Instalação
```
C:\Program Files\CorujaMonitor\
├── Probe\
│   ├── probe_core.py
│   ├── config.py
│   └── requirements.txt
├── collectors\
│   ├── system_collector.py
│   ├── ping_collector.py
│   └── ...
└── logs\
```

---

## 🔧 Pós-Instalação

### 1. Configurar a Probe
Edite o arquivo de configuração:
```
C:\Program Files\CorujaMonitor\Probe\config.py
```

Configure:
- IP do servidor Coruja Monitor
- Token da probe
- Intervalo de coleta

### 2. Instalar Dependências Python
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
pip install -r requirements.txt
```

### 3. Iniciar a Probe
Use o atalho no Menu Iniciar ou:
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
python probe_core.py
```

---

## 🔄 Gerar Nova Versão do MSI

Se precisar gerar uma nova versão:

```powershell
.\gerar_msi_com_ui.ps1
```

O novo MSI será gerado em: `.\installer\output\CorujaProbe.msi`

Para enviar para o Git:
```powershell
git add installer/output/CorujaProbe.msi
git commit -m "feat: Atualiza instalador MSI"
git push origin master
```

---

## 📊 Informações Técnicas

### Tecnologia
- **WiX Toolset:** 3.11 (versão estável)
- **Interface:** WixUIExtension
- **Formato:** Windows Installer (.msi)
- **Arquitetura:** x64

### Requisitos
- Windows 7 ou superior
- Privilégios de Administrador
- Python 3.8+ (para executar a probe)

### Desinstalação
- Painel de Controle > Programas > Desinstalar
- Ou use o atalho no Menu Iniciar
- Ou: `msiexec /x {ProductCode}`

---

## 🆘 Solução de Problemas

### MSI não abre
- Execute como Administrador
- Verifique se Windows Installer está funcionando
- Tente: `msiexec /i CorujaProbe.msi /l*v log.txt`

### Erro durante instalação
- Verifique o log: `C:\Windows\Temp\MSI*.log`
- Certifique-se de ter privilégios de Administrador
- Desinstale versões anteriores primeiro

### Probe não inicia
- Verifique se Python está instalado
- Instale dependências: `pip install -r requirements.txt`
- Verifique configuração em `config.py`

---

**Última atualização:** 05/03/2026 14:00  
**Versão MSI:** 1.0.0.0  
**Commit:** 32bc03c
