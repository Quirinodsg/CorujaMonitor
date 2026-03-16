# 🎯 SOLUÇÃO CORRETA: WMI com Credenciais Centralizadas

**Data**: 11/03/2026 15:15  
**Problema**: Ter que configurar firewall em cada máquina é inviável  
**Solução**: Usar credenciais de domínio como o PRTG

---

## ✅ COMO O PRTG FAZ (CORRETO)

### 1. Credenciais Centralizadas
- **1 usuário de domínio** com permissões WMI
- Configurado UMA VEZ no PRTG
- Usado para TODOS os servidores Windows

### 2. Sem Configuração por Máquina
- Não precisa abrir firewall manualmente
- Não precisa instalar agente
- Funciona via WMI remoto com credenciais

### 3. Permissões Necessárias
- Usuário membro de: **Administrators** ou **Performance Monitor Users**
- Permissões WMI: **Remote Enable**
- Firewall: Aberto via GPO (Group Policy) no domínio

---

## 🔧 IMPLEMENTAÇÃO NO CORUJA MONITOR

### Opção 1: Credenciais Globais (Recomendado)
Configurar UMA VEZ credenciais que servem para TODOS os servidores.

### Opção 2: Credenciais por Servidor
Para casos específicos onde cada servidor precisa de credenciais diferentes.

---

## 📋 PASSO A PASSO: CONFIGURAÇÃO CORRETA

### 1. Criar Usuário de Serviço no Active Directory

```powershell
# No Domain Controller
New-ADUser -Name "svc_monitor" `
  -SamAccountName "svc_monitor" `
  -UserPrincipalName "svc_monitor@SEUDOMINIO.local" `
  -AccountPassword (ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force) `
  -Enabled $true `
  -PasswordNeverExpires $true `
  -CannotChangePassword $true
```

### 2. Adicionar aos Grupos Necessários

```powershell
# Adicionar ao grupo de administradores locais via GPO
# OU adicionar ao grupo Performance Monitor Users
Add-ADGroupMember -Identity "Domain Admins" -Members "svc_monitor"
```

### 3. Configurar Firewall via GPO (Group Policy)

```
1. Abrir: Group Policy Management (gpmc.msc)
2. Criar nova GPO: "Firewall - WMI Monitoring"
3. Editar GPO:
   Computer Configuration > 
   Policies > 
   Windows Settings > 
   Security Settings > 
   Windows Firewall with Advanced Security > 
   Inbound Rules

4. Habilitar regras:
   - Windows Management Instrumentation (WMI-In)
   - File and Printer Sharing (SMB-In)
   - Remote Administration (RPC)

5. Aplicar GPO na OU dos servidores
```

### 4. Configurar no Coruja Monitor (Frontend)

```
1. Ir em: Configurações > Credenciais WMI
2. Adicionar credencial global:
   - Nome: "Domínio Principal"
   - Usuário: SEUDOMINIO\svc_monitor
   - Senha: SenhaForte123!
   - Domínio: SEUDOMINIO.local
   - Usar como padrão: ✓

3. Ao adicionar servidor:
   - Marcar: "Usar credencial padrão"
   - OU selecionar credencial específica
```

---

## 🔍 DIAGNÓSTICO: Testar Conectividade WMI

### PowerShell (SRVSONDA001)

```powershell
# Testar com credenciais
$username = "SEUDOMINIO\svc_monitor"
$password = ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($username, $password)

# Testar WMI
Get-WmiObject -Class Win32_OperatingSystem `
  -ComputerName "192.168.31.110" `
  -Credential $cred

# Testar CPU
Get-WmiObject -Class Win32_Processor `
  -ComputerName "192.168.31.110" `
  -Credential $cred | 
  Select-Object Name, LoadPercentage

# Testar Memória
Get-WmiObject -Class Win32_OperatingSystem `
  -ComputerName "192.168.31.110" `
  -Credential $cred | 
  Select-Object TotalVisibleMemorySize, FreePhysicalMemory
```

### Python (Probe)

```python
import wmi

# Conectar com credenciais
connection = wmi.WMI(
    computer="192.168.31.110",
    user=r"SEUDOMINIO\svc_monitor",
    password="SenhaForte123!"
)

# Testar coleta
for cpu in connection.Win32_Processor():
    print(f"CPU: {cpu.Name}, Load: {cpu.LoadPercentage}%")

for os in connection.Win32_OperatingSystem():
    print(f"OS: {os.Caption}, Uptime: {os.LastBootUpTime}")
```

---

## 🚀 IMPLEMENTAÇÃO NO CÓDIGO

### 1. Adicionar Tabela de Credenciais (models.py)

```python
class WMICredential(Base):
    __tablename__ = "wmi_credentials"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String(255))  # "Domínio Principal"
    username = Column(String(255))  # "DOMINIO\usuario"
    password_encrypted = Column(Text)  # Senha criptografada
    domain = Column(String(255))  # "DOMINIO.local"
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 2. Atualizar Probe para Usar Credenciais

```python
# probe/collectors/wmi_remote_collector.py

def collect_wmi_metrics(server):
    # Buscar credenciais do servidor
    if server.wmi_enabled and server.wmi_username:
        # Usar credenciais específicas do servidor
        username = server.wmi_username
        password = decrypt_password(server.wmi_password_encrypted)
        domain = server.wmi_domain
    else:
        # Usar credenciais padrão (global)
        cred = get_default_wmi_credential(server.tenant_id)
        username = cred.username
        password = decrypt_password(cred.password_encrypted)
        domain = cred.domain
    
    # Conectar via WMI
    connection = wmi.WMI(
        computer=server.ip_address,
        user=username,
        password=password
    )
    
    # Coletar métricas...
```

---

## ✅ VANTAGENS DESTA ABORDAGEM

1. **Configuração Única**: 1 usuário para todos os servidores
2. **Sem Tocar nos Servidores**: Firewall via GPO
3. **Escalável**: Adicionar 100 servidores = 0 configuração manual
4. **Seguro**: Credenciais criptografadas no banco
5. **Flexível**: Pode ter credenciais diferentes por servidor se necessário

---

## 🎯 PRÓXIMOS PASSOS

### 1. Criar Usuário de Serviço no AD
- Nome: svc_monitor
- Senha forte
- Adicionar ao grupo correto

### 2. Configurar GPO para Firewall
- Habilitar WMI em todos os servidores
- Aplicar na OU correta

### 3. Implementar Tabela de Credenciais
- Criar migração do banco
- Adicionar interface no frontend
- Atualizar probe para usar credenciais

### 4. Testar Conectividade
- PowerShell: Get-WmiObject com credenciais
- Python: wmi.WMI() com credenciais
- Verificar coleta de métricas

---

## 📝 COMANDOS RÁPIDOS

### Testar WMI com Credenciais (PowerShell)

```powershell
$cred = Get-Credential  # Digitar DOMINIO\svc_monitor
Get-WmiObject Win32_OperatingSystem -ComputerName 192.168.31.110 -Credential $cred
```

### Verificar Permissões WMI

```powershell
# No servidor alvo
wmimgmt.msc
# Root > CIMV2 > Security
# Verificar se svc_monitor tem "Remote Enable"
```

### Verificar Firewall

```powershell
# No servidor alvo
Get-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)" | 
  Select-Object DisplayName, Enabled
```

---

## ⚠️ IMPORTANTE

**NÃO PRECISA**:
- ❌ Abrir firewall manualmente em cada servidor
- ❌ Instalar agente em cada servidor
- ❌ Configurar WMI em cada servidor

**PRECISA**:
- ✅ 1 usuário de domínio com permissões
- ✅ GPO para firewall (aplica em todos)
- ✅ Configurar credenciais no Coruja Monitor

---

**Esta é a abordagem correta, igual ao PRTG!**
