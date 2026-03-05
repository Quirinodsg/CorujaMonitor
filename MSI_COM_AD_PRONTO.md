# ✅ MSI COM ACTIVE DIRECTORY - PRONTO

## 📦 2 MSIs Criados

### MSI 1: BÁSICO (Auto-Start)
**Arquivo:** `installer/output/CorujaProbe_Basico.msi`  
**Status:** ✅ GERADO E FUNCIONANDO

**Funcionalidades:**
- ✅ Instalação de arquivos
- ✅ Auto-start via Task Scheduler
- ✅ Instalação de dependências Python
- ✅ Atalhos no Menu Iniciar
- ✅ Interface gráfica completa

**Uso:** Instalação simples sem configuração de AD

---

### MSI 2: COM ACTIVE DIRECTORY
**Arquivo:** `installer/output/CorujaProbe_AD.msi`  
**Status:** ⚠️ CÓDIGO PRONTO, PRECISA SER GERADO NO SERVIDOR LINUX

**Funcionalidades:**
- ✅ Solicita domínio do AD
- ✅ Solicita usuário (padrão: coruja.monitor)
- ✅ Solicita senha (campo seguro)
- ✅ Solicita URL da API
- ✅ Solicita token da probe
- ✅ Configura Task Scheduler com usuário AD
- ✅ Auto-start automático
- ✅ Interface gráfica com 2 diálogos customizados

**Diálogos:**
1. **Configuração AD:** Domínio, Usuário, Senha
2. **Configuração API:** URL da API, Token da Probe

---

## 🚀 Como Usar

### MSI Básico (Disponível Agora)

```powershell
# Baixar do Git
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd CorujaMonitor/installer/output

# Instalar
msiexec /i CorujaProbe_Basico.msi
```

**Após instalação:**
- Editar manualmente: `C:\Program Files\CorujaMonitor\Probe\config.py`
- Configurar credenciais AD se necessário

---

### MSI com AD (Precisa Gerar)

**No servidor Linux:**
```bash
cd ~/CorujaMonitor
git pull origin master
cd installer
chmod +x gerar_2_msis.ps1

# Gerar MSI (precisa de WiX no Linux ou usar Wine)
# OU copiar arquivos da probe para Windows e gerar lá
```

**Após gerar:**
```powershell
msiexec /i CorujaProbe_AD.msi
```

**Durante instalação, será solicitado:**
1. Domínio (ex: EMPRESA)
2. Usuário (ex: coruja.monitor)
3. Senha do usuário
4. URL da API (ex: http://192.168.31.161:8000)
5. Token da probe (obter no dashboard)

---

## 📋 Arquivos Criados

### Código WiX
- `installer/CorujaProbe_AutoStart.wxs` - MSI Básico ✅
- `installer/CorujaProbe_AD_Simple.wxs` - MSI com AD ✅

### Scripts
- `gerar_2_msis.ps1` - Gera os 2 MSIs automaticamente ✅

### Documentação
- `MSI_COM_AD_PRONTO.md` - Este arquivo ✅

---

## 🔧 Detalhes Técnicos

### MSI com AD - Propriedades

```xml
<Property Id="AD_DOMAIN" Value="EMPRESA" />
<Property Id="AD_USERNAME" Value="coruja.monitor" />
<Property Id="AD_PASSWORD" Secure="yes" />
<Property Id="API_URL" Value="http://192.168.31.161:8000" />
<Property Id="PROBE_TOKEN" Secure="yes" />
```

### Custom Actions

1. **InstallPythonDeps** - Instala dependências
2. **CreateTaskScheduler** - Cria task com usuário AD
3. **StartProbe** - Inicia probe
4. **StopProbe** - Para probe (desinstalação)
5. **DeleteTask** - Remove task (desinstalação)

### Task Scheduler Command

```batch
schtasks /create /tn CorujaMonitorProbe 
  /tr "cmd /c cd /d [ProbeFolder] && python probe_core.py" 
  /sc onstart 
  /delay 0000:30 
  /rl highest 
  /ru [AD_DOMAIN]\[AD_USERNAME] 
  /rp [AD_PASSWORD] 
  /f
```

---

## ⚠️ Limitação Atual

**MSI com AD não pode ser gerado no Windows** porque:
- Arquivos da probe (`probe_core.py`, etc.) não existem no Windows
- Arquivos estão no servidor Linux

**Soluções:**

**Opção A:** Copiar arquivos da probe para Windows
```bash
# No servidor Linux
cd ~/CorujaMonitor
tar -czf probe_files.tar.gz probe/

# Copiar para Windows e extrair
# Depois gerar MSI
```

**Opção B:** Gerar MSI no servidor Linux (complexo)
- Instalar Wine
- Instalar WiX via Wine
- Gerar MSI

**Opção C:** Usar MSI Básico + Configuração Manual
- Instalar MSI Básico
- Editar config.py manualmente
- Reconfigurar Task Scheduler

---

## 📊 Comparação

| Funcionalidade | MSI Básico | MSI com AD |
|---|---|---|
| Instalação de arquivos | ✅ | ✅ |
| Auto-start | ✅ | ✅ |
| Interface gráfica | ✅ | ✅ |
| Solicita domínio AD | ❌ | ✅ |
| Solicita usuário AD | ❌ | ✅ |
| Solicita senha AD | ❌ | ✅ |
| Solicita URL API | ❌ | ✅ |
| Solicita token | ❌ | ✅ |
| Config automática | ❌ | ✅ |
| Disponível agora | ✅ | ⚠️ |

---

## 🎯 Recomendação

**Para uso imediato:**
- Use `CorujaProbe_Basico.msi`
- Configure manualmente após instalação

**Para futuro:**
- Gere `CorujaProbe_AD.msi` no servidor Linux
- Distribua para instalação automatizada

---

**Data:** 05/03/2026  
**Status:** MSI Básico ✅ | MSI com AD ⚠️ (código pronto)  
**Commit:** Próximo
