# Soluções para WMI "Access Denied"

## Problema Atual

WMI nativo dá erro "Access denied" mesmo usando credencial Domain Admin:
```
<x_wmi: Unexpected COM Error (-2147352567, 'Exception occurred.', 
(0, 'SWbemLocator', 'Access is denied. ', None, 0, -2147024891), None)>
```

## Cenários e Soluções

### Cenário A: Problema de Permissões DCOM/WMI

**Sintomas:**
- WMI local funciona ✅
- WMI remoto COM credenciais falha ❌
- WMI remoto SEM credenciais (contexto atual) pode funcionar ✅

**Causa:**
- Servidor de destino (SRVHVSPRD010) não tem permissões DCOM/WMI configuradas
- Mesmo Domain Admin precisa de permissões explícitas no namespace WMI

**Solução:**
Configurar permissões WMI no SRVHVSPRD010:

```powershell
# No SRVHVSPRD010, executar como Administrador:

# 1. Abrir wmimgmt.msc
# 2. Clicar com botão direito em "WMI Control (Local)" → Properties
# 3. Aba "Security"
# 4. Expandir "Root" → Selecionar "CIMV2"
# 5. Clicar em "Security"
# 6. Adicionar "Techbiz\coruja.monitor"
# 7. Dar permissões:
#    - Execute Methods
#    - Enable Account
#    - Remote Enable
#    - Read Security

# OU via script:
$namespace = Get-WmiObject -Namespace "root" -Class "__SystemSecurity"
$sd = $namespace.GetSecurityDescriptor().Descriptor

# Adicionar ACE para Techbiz\coruja.monitor
$trustee = ([wmiclass]"Win32_Trustee").CreateInstance()
$trustee.Domain = "Techbiz"
$trustee.Name = "coruja.monitor"

$ace = ([wmiclass]"Win32_Ace").CreateInstance()
$ace.AccessMask = 131097  # Execute Methods + Enable Account + Remote Enable
$ace.AceFlags = 0
$ace.AceType = 0
$ace.Trustee = $trustee

$sd.DACL += $ace.psobject.baseobject
$namespace.SetSecurityDescriptor($sd)
```

**Configurar DCOM:**
```powershell
# No SRVHVSPRD010:
dcomcnfg

# 1. Component Services → Computers → My Computer
# 2. Botão direito → Properties
# 3. Aba "COM Security"
# 4. "Access Permissions" → Edit Limits
# 5. Adicionar "Techbiz\coruja.monitor" com "Local Access" e "Remote Access"
# 6. "Launch and Activation Permissions" → Edit Limits
# 7. Adicionar "Techbiz\coruja.monitor" com todas as permissões
```

---

### Cenário B: Biblioteca WMI Python Ignora Credenciais

**Sintomas:**
- WMI local funciona ✅
- WMI remoto COM credenciais falha ❌
- WMI remoto SEM credenciais funciona ✅ (se probe rodar como Domain Admin)
- win32com direto funciona ✅

**Causa:**
- Biblioteca `wmi` Python pode ter bug ou limitação
- Credenciais não são passadas corretamente para o COM

**Solução 1: Usar win32com diretamente**

Modificar `wmi_native_collector.py` para usar `win32com.client` em vez de `wmi`:

```python
import win32com.client

def connect(self):
    try:
        locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        
        self.connection = locator.ConnectServer(
            self.hostname,
            "root\\cimv2",
            self.full_username,
            self.password
        )
        
        return True
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False

def collect_cpu(self):
    query = "SELECT LoadPercentage FROM Win32_Processor"
    results = self.connection.ExecQuery(query)
    # ... processar resultados
```

**Solução 2: Executar probe como usuário do domínio**

Configurar serviço da probe para rodar como `Techbiz\coruja.monitor`:

```powershell
# No SRVSONDA001:
sc.exe config "CorujaProbe" obj= "Techbiz\coruja.monitor" password= "Dj8SXoXie!o6Tkc@"
sc.exe stop "CorujaProbe"
sc.exe start "CorujaProbe"
```

Neste caso, WMI usaria automaticamente as credenciais do processo.

---

### Cenário C: Problema de Rede/Firewall

**Sintomas:**
- Tudo falha ❌
- Timeout ou "RPC server unavailable"

**Causa:**
- Firewall bloqueando portas WMI
- Rede não permite comunicação DCOM

**Solução:**

Verificar conectividade:
```powershell
# Testar porta 135 (RPC)
Test-NetConnection -ComputerName SRVHVSPRD010.ad.techbiz.com.br -Port 135

# Testar WMI via PowerShell
Get-WmiObject -Class Win32_OperatingSystem -ComputerName SRVHVSPRD010.ad.techbiz.com.br
```

Liberar firewall no SRVHVSPRD010:
```powershell
# Habilitar regra de firewall para WMI
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"

# OU criar regra manualmente
New-NetFirewallRule -DisplayName "WMI-In" -Direction Inbound -Protocol TCP -LocalPort 135 -Action Allow
New-NetFirewallRule -DisplayName "WMI-DCOM-In" -Direction Inbound -Protocol TCP -LocalPort RPC -Action Allow
```

---

### Cenário D: GPO Bloqueando WMI Remoto

**Sintomas:**
- WMI local funciona ✅
- WMI remoto falha mesmo com permissões corretas ❌
- Erro "Access denied" persistente

**Causa:**
- GPO do domínio bloqueando acesso WMI remoto
- Política de segurança restritiva

**Solução:**

Verificar GPO:
```powershell
# No SRVHVSPRD010:
gpresult /H gpresult.html

# Procurar por:
# - "Windows Management Instrumentation (WMI)"
# - "DCOM"
# - "Remote Access"
```

Criar exceção na GPO ou adicionar usuário a grupo permitido.

---

## Alternativa: Usar SNMP

Se WMI continuar problemático, considerar usar SNMP:

**Vantagens:**
- Mais simples
- Funciona em Windows e Linux
- Não precisa de credenciais de domínio

**Desvantagens:**
- Menos métricas disponíveis
- Precisa instalar SNMP no Windows

**Instalação SNMP no Windows:**
```powershell
# No SRVHVSPRD010:
Add-WindowsFeature SNMP-Service
Set-Service SNMP -StartupType Automatic
Start-Service SNMP

# Configurar community string
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\SNMP\Parameters\ValidCommunities" -Name "public" -Value 4
```

---

## Recomendação

1. **Primeiro:** Executar diagnóstico completo (`testar_wmi_nativo_diagnostico.py`)
2. **Identificar** qual cenário se aplica
3. **Aplicar** solução correspondente
4. **Se falhar:** Considerar alternativa SNMP

---

**Data:** 13/03/2026  
**Status:** Aguardando diagnóstico
