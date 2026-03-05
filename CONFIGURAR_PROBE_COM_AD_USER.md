# 🔐 Configurar Probe com Usuário do Active Directory

## 👤 Usuário Criado

**Usuário:** `coruja.monitor`  
**Tipo:** Domain Admin  
**Domínio:** Seu domínio AD  
**Propósito:** Monitoramento WMI remoto

---

## ✅ Vantagens de Usar Usuário do AD

- ✅ Gerenciamento centralizado no AD
- ✅ Políticas de senha do domínio aplicadas
- ✅ Auditoria centralizada
- ✅ Fácil revogação de acesso
- ✅ Não precisa criar usuário local em cada máquina
- ✅ Funciona em todo o domínio

---

## 🚀 Configuração da Probe

### Opção 1: Instalação Manual com Usuário AD

#### 1. Editar config.py

Abra o arquivo de configuração:
```
C:\Program Files\CorujaMonitor\Probe\config.py
```

Adicione as credenciais do AD:
```python
# Configuração WMI para monitoramento remoto
WMI_CONFIG = {
    'domain': 'SEU_DOMINIO',  # Ex: 'EMPRESA' ou 'empresa.local'
    'username': 'coruja.monitor',
    'password': 'SENHA_DO_USUARIO',
    'use_domain_user': True
}

# URL da API
API_URL = 'http://192.168.31.161:8000'

# Token da probe (obter no dashboard)
PROBE_TOKEN = 'seu_token_aqui'
```

#### 2. Configurar Task Scheduler com Usuário AD

Execute como Administrador:
```batch
schtasks /create /tn "CorujaMonitorProbe" ^
  /tr "cmd /c cd /d \"C:\Program Files\CorujaMonitor\Probe\" && python probe_core.py" ^
  /sc onstart ^
  /delay 0000:30 ^
  /rl highest ^
  /ru "DOMINIO\coruja.monitor" ^
  /rp "SENHA_DO_USUARIO" ^
  /f
```

**Importante:** Substitua:
- `DOMINIO` pelo nome do seu domínio
- `SENHA_DO_USUARIO` pela senha real

#### 3. Iniciar a Probe

```batch
schtasks /run /tn "CorujaMonitorProbe"
```

---

### Opção 2: Script de Instalação Automatizada

Crie um arquivo `instalar_probe_ad.bat`:

```batch
@echo off
REM Instalação da Probe com usuário do AD

echo ========================================
echo INSTALACAO CORUJA PROBE - USUARIO AD
echo ========================================
echo.

REM Configurações
set DOMINIO=SEU_DOMINIO
set USUARIO=coruja.monitor
set SENHA=SENHA_DO_USUARIO
set API_URL=http://192.168.31.161:8000
set PROBE_TOKEN=SEU_TOKEN_AQUI

echo [1/5] Criando diretórios...
if not exist "C:\Program Files\CorujaMonitor\Probe" mkdir "C:\Program Files\CorujaMonitor\Probe"
if not exist "C:\Program Files\CorujaMonitor\Probe\logs" mkdir "C:\Program Files\CorujaMonitor\Probe\logs"
if not exist "C:\Program Files\CorujaMonitor\Probe\collectors" mkdir "C:\Program Files\CorujaMonitor\Probe\collectors"

echo [2/5] Copiando arquivos...
REM Copiar arquivos da probe aqui
REM xcopy /s /y probe\*.* "C:\Program Files\CorujaMonitor\Probe\"

echo [3/5] Configurando credenciais AD...
(
echo # Configuracao Coruja Monitor Probe
echo.
echo WMI_CONFIG = {
echo     'domain': '%DOMINIO%',
echo     'username': '%USUARIO%',
echo     'password': '%SENHA%',
echo     'use_domain_user': True
echo }
echo.
echo API_URL = '%API_URL%'
echo PROBE_TOKEN = '%PROBE_TOKEN%'
) > "C:\Program Files\CorujaMonitor\Probe\config.py"

echo [4/5] Instalando dependencias Python...
cd /d "C:\Program Files\CorujaMonitor\Probe"
pip install -r requirements.txt

echo [5/5] Configurando auto-start com usuario AD...
schtasks /create /tn "CorujaMonitorProbe" ^
  /tr "cmd /c cd /d \"C:\Program Files\CorujaMonitor\Probe\" && python probe_core.py" ^
  /sc onstart ^
  /delay 0000:30 ^
  /rl highest ^
  /ru "%DOMINIO%\%USUARIO%" ^
  /rp "%SENHA%" ^
  /f

echo.
echo [6/5] Iniciando probe...
schtasks /run /tn "CorujaMonitorProbe"

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Probe configurada com usuario: %DOMINIO%\%USUARIO%
echo.
echo Verificar status:
echo   schtasks /query /tn "CorujaMonitorProbe"
echo   tasklist ^| findstr python
echo.
pause
```

**Para usar:**
1. Edite o arquivo e configure:
   - `DOMINIO`
   - `SENHA`
   - `API_URL`
   - `PROBE_TOKEN`
2. Execute como Administrador

---

### Opção 3: PowerShell Script (Mais Seguro)

Crie `instalar_probe_ad.ps1`:

```powershell
# Instalação Coruja Probe com usuário AD
# Execute como Administrador

param(
    [Parameter(Mandatory=$true)]
    [string]$Dominio,
    
    [Parameter(Mandatory=$true)]
    [string]$Usuario = "coruja.monitor",
    
    [Parameter(Mandatory=$true)]
    [SecureString]$Senha,
    
    [Parameter(Mandatory=$true)]
    [string]$ApiUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$ProbeToken
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACAO CORUJA PROBE - USUARIO AD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Converter senha segura para texto
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Senha)
$SenhaTexto = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Criar diretórios
Write-Host "[1/5] Criando diretórios..." -ForegroundColor Yellow
$probeDir = "C:\Program Files\CorujaMonitor\Probe"
New-Item -ItemType Directory -Path $probeDir -Force | Out-Null
New-Item -ItemType Directory -Path "$probeDir\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$probeDir\collectors" -Force | Out-Null
Write-Host "   OK" -ForegroundColor Green

# Criar config.py
Write-Host "[2/5] Configurando credenciais AD..." -ForegroundColor Yellow
$configContent = @"
# Configuracao Coruja Monitor Probe

WMI_CONFIG = {
    'domain': '$Dominio',
    'username': '$Usuario',
    'password': '$SenhaTexto',
    'use_domain_user': True
}

API_URL = '$ApiUrl'
PROBE_TOKEN = '$ProbeToken'
"@
$configContent | Out-File -FilePath "$probeDir\config.py" -Encoding UTF8
Write-Host "   OK" -ForegroundColor Green

# Instalar dependências
Write-Host "[3/5] Instalando dependencias Python..." -ForegroundColor Yellow
Set-Location $probeDir
pip install -r requirements.txt | Out-Null
Write-Host "   OK" -ForegroundColor Green

# Configurar Task Scheduler
Write-Host "[4/5] Configurando auto-start..." -ForegroundColor Yellow
$taskCommand = "cmd /c cd /d `"$probeDir`" && python probe_core.py"
$taskUser = "$Dominio\$Usuario"

schtasks /create /tn "CorujaMonitorProbe" `
  /tr $taskCommand `
  /sc onstart `
  /delay 0000:30 `
  /rl highest `
  /ru $taskUser `
  /rp $SenhaTexto `
  /f | Out-Null
Write-Host "   OK" -ForegroundColor Green

# Iniciar probe
Write-Host "[5/5] Iniciando probe..." -ForegroundColor Yellow
schtasks /run /tn "CorujaMonitorProbe" | Out-Null
Start-Sleep -Seconds 3
Write-Host "   OK" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Probe configurada com usuario: $taskUser" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verificar status:" -ForegroundColor Yellow
Write-Host "  schtasks /query /tn `"CorujaMonitorProbe`"" -ForegroundColor White
Write-Host "  tasklist | findstr python" -ForegroundColor White
Write-Host ""
```

**Para usar:**
```powershell
$senha = Read-Host "Senha do usuario coruja.monitor" -AsSecureString

.\instalar_probe_ad.ps1 `
  -Dominio "SEU_DOMINIO" `
  -Usuario "coruja.monitor" `
  -Senha $senha `
  -ApiUrl "http://192.168.31.161:8000" `
  -ProbeToken "SEU_TOKEN_AQUI"
```

---

## 🔒 Segurança

### Permissões Necessárias

O usuário `coruja.monitor` precisa de:

1. **WMI Access** em todas as máquinas:
   ```batch
   REM Executar em cada máquina ou via GPO
   wmic /namespace:\\root\cimv2 path __SystemSecurity call GetSD
   ```

2. **DCOM Permissions**:
   - Component Services → Computers → My Computer
   - Propriedades → COM Security
   - Adicionar `coruja.monitor` com permissões de acesso

3. **Firewall Rules**:
   ```batch
   netsh advfirewall firewall add rule name="WMI-In" dir=in action=allow protocol=TCP localport=135
   netsh advfirewall firewall add rule name="WMI-In-DCOM" dir=in action=allow protocol=TCP localport=any remoteport=any
   ```

### Aplicar via GPO (Recomendado)

Crie uma GPO para aplicar em todas as máquinas:

1. **Computer Configuration → Policies → Windows Settings → Security Settings**
2. **Local Policies → User Rights Assignment**
3. Adicionar `DOMINIO\coruja.monitor` em:
   - Access this computer from the network
   - Log on as a batch job

---

## 🧪 Testar Configuração

### 1. Testar Credenciais AD

```batch
runas /user:DOMINIO\coruja.monitor cmd
```

### 2. Testar WMI Remoto

```powershell
$cred = Get-Credential -UserName "DOMINIO\coruja.monitor"
Get-WmiObject -Class Win32_OperatingSystem -ComputerName "MAQUINA_REMOTA" -Credential $cred
```

### 3. Verificar Task Scheduler

```batch
schtasks /query /tn "CorujaMonitorProbe" /v /fo list
```

### 4. Ver Logs

```batch
type "C:\Program Files\CorujaMonitor\Probe\logs\probe.log"
```

---

## 🔧 Troubleshooting

### Erro: Access Denied

**Causa:** Usuário sem permissões WMI

**Solução:**
```batch
REM Adicionar ao grupo Administrators (temporário para teste)
net localgroup Administrators DOMINIO\coruja.monitor /add

REM Ou configurar permissões WMI específicas
wmimgmt.msc
```

### Erro: Task Scheduler não inicia

**Causa:** Senha incorreta ou expirada

**Solução:**
```batch
REM Recriar task com senha atualizada
schtasks /delete /tn "CorujaMonitorProbe" /f
schtasks /create /tn "CorujaMonitorProbe" ... (comando completo)
```

### Erro: Cannot connect to remote machine

**Causa:** Firewall bloqueando WMI

**Solução:**
```batch
REM Habilitar regras de firewall para WMI
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
```

---

## 📊 Monitoramento

### Verificar Status da Probe

```batch
REM Status do Task Scheduler
schtasks /query /tn "CorujaMonitorProbe"

REM Processo rodando
tasklist | findstr python

REM Logs em tempo real
powershell Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\probe.log" -Wait -Tail 20
```

### Dashboard

Acesse: `http://192.168.31.161:3000`
- Gerenciamento → Probes
- Verificar status "Online"
- Ver última coleta de dados

---

## 🎯 Checklist de Implementação

- [ ] Usuário `coruja.monitor` criado no AD
- [ ] Usuário é Domain Admin (ou tem permissões WMI)
- [ ] Senha forte configurada
- [ ] Probe instalada com credenciais AD
- [ ] Task Scheduler configurado com usuário AD
- [ ] Firewall configurado para WMI
- [ ] DCOM permissions configuradas
- [ ] Testado WMI remoto
- [ ] Probe aparece online no dashboard
- [ ] Logs sendo gerados corretamente

---

## 📚 Próximos Passos

1. **Testar em uma máquina** primeiro
2. **Criar GPO** para aplicar configurações WMI em todas as máquinas
3. **Distribuir probe** via MSI ou script
4. **Monitorar logs** para verificar funcionamento
5. **Documentar** máquinas monitoradas

---

**Data:** 05/03/2026  
**Usuário AD:** coruja.monitor  
**Tipo:** Domain Admin  
**Status:** ✅ PRONTO PARA USO
