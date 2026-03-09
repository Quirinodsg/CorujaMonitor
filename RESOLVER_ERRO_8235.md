# 🔧 Resolver Erro 8235 - Shell Execute Failed

## ❌ Problema

Ao executar o instalador EXE no servidor, aparece o erro:

```
Shell Execute EX falhou; código 8235
A referral was returned from the server
```

## 🔍 Causa

O erro 8235 acontece quando o Inno Setup tenta executar comandos que dependem do Active Directory ou rede durante a instalação. Isso é comum em:

- Servidores com Active Directory
- Ambientes corporativos com GPO restritivo
- Servidores em domínio
- Comandos que tentam acessar recursos de rede

No nosso caso, os comandos problemáticos são:
1. Download do Python (acesso à internet)
2. Instalação do Python (pode tentar verificar AD)
3. Configuração do Firewall via netsh (pode consultar GPO)

## ✅ Solução 1: Instalador Simples (Recomendado)

Use o instalador simples que NÃO executa comandos de rede:

### Gerar Instalador Simples

```powershell
cd "C:\Users\andre.quirino\Coruja Monitor"
.\GERAR_INSTALADOR_SIMPLES.ps1
```

Isso gera: `installer\output\CorujaMonitorProbe-Simples-v1.0.0.exe`

### Características do Instalador Simples

✅ Apenas copia arquivos
✅ Cria atalhos
✅ Registra no Windows
✅ NÃO executa comandos de rede
✅ NÃO baixa Python
✅ NÃO configura firewall
✅ Abre instruções pós-instalação

### Passos Pós-Instalação

Após instalar, execute manualmente:

#### 1. Instalar Python

```powershell
# Baixar Python
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile "python-installer.exe"

# Instalar
.\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
```

#### 2. Instalar Dependências

```powershell
python -m pip install --upgrade pip
python -m pip install psutil httpx pywin32 pysnmp pyyaml
```

#### 3. Configurar Firewall (WMI)

```powershell
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
```

#### 4. Configurar Probe

```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
.\configurar_probe.bat
```

#### 5. Instalar Serviço

```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
.\install.bat
```

## ✅ Solução 2: Instalação Manual (ZIP)

Se o instalador simples também falhar, use instalação manual:

### Baixar Arquivos

```powershell
cd C:\
git clone https://github.com/Quirinodsg/CorujaMonitor.git
cd CorujaMonitor\probe
```

### Instalar Python

```powershell
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile "python.exe"
.\python.exe /quiet InstallAllUsers=1 PrependPath=1
```

### Instalar Dependências

```powershell
python -m pip install psutil httpx pywin32 pysnmp pyyaml
```

### Configurar

```powershell
.\configurar_probe.bat
```

### Instalar Serviço

```powershell
.\install.bat
```

## ✅ Solução 3: Desabilitar Verificação de Rede (Avançado)

Se você tem acesso de administrador de domínio:

### Via GPO

```
1. gpedit.msc
2. Configuração do Computador
3. Modelos Administrativos
4. Sistema
5. Logon
6. "Sempre aguardar a rede na inicialização do computador" = Desabilitado
```

### Via Registro

```powershell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v SyncForegroundPolicy /t REG_DWORD /d 0 /f
```

## 📊 Comparação de Instaladores

| Característica | Completo | Simples | Manual (ZIP) |
|----------------|----------|---------|--------------|
| Instala Python | ✅ | ❌ | ❌ |
| Configura Firewall | ✅ | ❌ | ❌ |
| Funciona em AD | ❌ | ✅ | ✅ |
| Erro 8235 | ❌ | ✅ | ✅ |
| Interface Gráfica | ✅ | ✅ | ❌ |
| Atalhos | ✅ | ✅ | ❌ |
| Desinstalação | ✅ | ✅ | ⚠️ |
| Recomendado para | Workgroup | AD/Domínio | Testes |

## 🎯 Recomendação

Para servidores corporativos com Active Directory:

1. **Use o Instalador Simples** (`CorujaMonitorProbe-Simples-v1.0.0.exe`)
2. Execute os passos pós-instalação manualmente
3. Documente o processo para próximas instalações

## 📝 Script Completo Pós-Instalação

Salve como `pos_instalacao.ps1` e execute como Administrador:

```powershell
# Script de Pós-Instalação Coruja Monitor Probe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📦 PÓS-INSTALAÇÃO CORUJA MONITOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "1️⃣ Verificando Python..." -ForegroundColor Yellow
$pythonInstalled = $false
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python instalado: $pythonVersion" -ForegroundColor Green
    $pythonInstalled = $true
} catch {
    Write-Host "   ❌ Python não encontrado" -ForegroundColor Red
}

if (-not $pythonInstalled) {
    Write-Host ""
    Write-Host "   📥 Baixando Python 3.11..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
    
    Write-Host "   📦 Instalando Python..." -ForegroundColor Yellow
    Start-Process -FilePath "$env:TEMP\python-installer.exe" -ArgumentList "/quiet","InstallAllUsers=1","PrependPath=1" -Wait
    
    Write-Host "   ✅ Python instalado!" -ForegroundColor Green
    
    # Atualizar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 2. Instalar Dependências
Write-Host ""
Write-Host "2️⃣ Instalando dependências Python..." -ForegroundColor Yellow
python -m pip install --quiet --upgrade pip
python -m pip install --quiet psutil httpx pywin32 pysnmp pyyaml
Write-Host "   ✅ Dependências instaladas!" -ForegroundColor Green

# 3. Configurar Firewall
Write-Host ""
Write-Host "3️⃣ Configurando firewall (WMI)..." -ForegroundColor Yellow
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes | Out-Null
Write-Host "   ✅ Firewall configurado!" -ForegroundColor Green

# 4. Instruções Finais
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ PÓS-INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configurar Probe:" -ForegroundColor Yellow
Write-Host "   cd 'C:\Program Files\CorujaMonitor\Probe'" -ForegroundColor White
Write-Host "   .\configurar_probe.bat" -ForegroundColor White
Write-Host ""
Write-Host "2. Instalar como Serviço:" -ForegroundColor Yellow
Write-Host "   cd 'C:\Program Files\CorujaMonitor\Probe'" -ForegroundColor White
Write-Host "   .\install.bat" -ForegroundColor White
Write-Host ""
Write-Host "Pressione ENTER para sair..."
Read-Host
```

## 🔍 Diagnóstico

Se ainda tiver problemas, execute:

```powershell
# Verificar Python
python --version

# Verificar dependências
python -c "import psutil, httpx, win32api, pysnmp, yaml; print('OK')"

# Verificar firewall
netsh advfirewall firewall show rule name=all | findstr "WMI"

# Verificar serviço
sc query CorujaProbe
```

## 📞 Suporte

- Interface Web: http://192.168.31.161:3000
- Login: admin@coruja.com / admin123
- Logs: `C:\Program Files\CorujaMonitor\Probe\logs\`

