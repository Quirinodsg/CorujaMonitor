# 📊 RESUMO: Situação WMI - 11/03/2026 15:20

## ✅ PROGRESSO ATUAL

### 1. Servidor 192.168.31.110 Adicionado
- ✅ Servidor adicionado no frontend
- ✅ Firewall WMI liberado (4 regras habilitadas)
- ⏳ Aguardando dados (precisa testar conectividade WMI)

### 2. Problema Identificado
- ❌ PowerShell 7+ não tem parâmetro `-Credential` no `Get-CimInstance`
- ❌ `wmic.exe` não existe no Windows Server 2022 (depreciado)
- ✅ Solução: Usar `Get-WmiObject` ou `CimSession`

### 3. Arquitetura Entendida
- **SRVSONDA001** (Windows): NÃO está no domínio (workgroup)
- **SRVCMONITOR001** (Linux): NÃO está no domínio (workgroup)
- **Demais servidores**: ESTÃO no domínio
- **192.168.31.110**: Está no domínio

---

## 🎯 SOLUÇÃO CORRETA (COMO PRTG)

### Abordagem Errada (Anterior)
❌ Configurar firewall manualmente em cada máquina
❌ Entrar em cada servidor para liberar portas
❌ Não escalável

### Abordagem Correta (PRTG)
✅ **1 usuário de domínio** com permissões WMI
✅ Configurado UMA VEZ no sistema
✅ Usado para TODOS os servidores
✅ Firewall via GPO (Group Policy) no domínio
✅ Para workgroup: TrustedHosts configurado uma vez

---

## 📋 PRÓXIMOS PASSOS

### PASSO 1: Testar WMI no Workgroup (AGORA)
**Arquivo**: `RESOLVER_WMI_WORKGROUP_AGORA.txt`

1. **Na SRVSONDA001** (como Administrador):
   ```powershell
   Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.31.*" -Force
   Restart-Service WinRM
   ```

2. **No 192.168.31.110** (como Administrador):
   ```powershell
   Enable-PSRemoting -Force
   Get-Service WinRM  # Deve estar Running
   ```

3. **Testar conectividade** (na SRVSONDA001):
   ```powershell
   $cred = Get-Credential  # Digitar: Administrator
   Get-WmiObject Win32_OperatingSystem -ComputerName 192.168.31.110 -Credential $cred
   ```

4. **Se funcionar**: WMI está OK! ✅

---

### PASSO 2: Implementar Credenciais Centralizadas (FUTURO)
**Arquivo**: `SOLUCAO_WMI_CREDENCIAIS_CENTRALIZADAS.md`

#### 2.1. Criar Tabela no Banco de Dados
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

#### 2.2. Criar API para Gerenciar Credenciais
- `api/routers/wmi_credentials.py`
- Endpoints: GET, POST, PUT, DELETE
- Criptografia de senhas

#### 2.3. Criar Interface no Frontend
- Tela: Configurações > Credenciais WMI
- Adicionar/Editar/Deletar credenciais
- Marcar credencial como padrão
- Ao adicionar servidor: selecionar credencial

#### 2.4. Atualizar Probe para Usar Credenciais
- `probe/collectors/wmi_remote_collector.py`
- Buscar credenciais do banco de dados
- Usar credenciais específicas do servidor OU credenciais padrão
- Conectar via WMI com credenciais

---

### PASSO 3: Configurar Domínio (FUTURO)
**Para servidores no domínio** (mais simples):

1. **Criar usuário de serviço no AD**:
   ```powershell
   New-ADUser -Name "svc_monitor" `
     -SamAccountName "svc_monitor" `
     -UserPrincipalName "svc_monitor@SEUDOMINIO.local" `
     -AccountPassword (ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force) `
     -Enabled $true `
     -PasswordNeverExpires $true
   
   Add-ADGroupMember -Identity "Domain Admins" -Members "svc_monitor"
   ```

2. **Configurar GPO para Firewall**:
   - Abrir: `gpmc.msc`
   - Criar GPO: "Firewall - WMI Monitoring"
   - Habilitar regras WMI em todos os servidores
   - Aplicar na OU dos servidores

3. **Configurar no Coruja Monitor**:
   - Credencial global: `DOMINIO\svc_monitor`
   - Usar para todos os servidores do domínio
   - Não precisa TrustedHosts!
   - Funciona via Kerberos automaticamente!

---

## 🔍 DIAGNÓSTICO: Comandos Úteis

### Verificar TrustedHosts
```powershell
Get-Item WSMan:\localhost\Client\TrustedHosts
```

### Verificar Serviço WinRM
```powershell
Get-Service WinRM
```

### Verificar Firewall WMI
```powershell
Get-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)" | 
  Where-Object {$_.Enabled -eq $true} | 
  Select-Object DisplayName, Enabled
```

### Testar Conectividade WMI
```powershell
$cred = Get-Credential
Get-WmiObject Win32_OperatingSystem -ComputerName 192.168.31.110 -Credential $cred
```

---

## ✅ VANTAGENS DA SOLUÇÃO CORRETA

1. **Configuração Única**: 1 usuário para todos os servidores
2. **Sem Tocar nos Servidores**: Firewall via GPO (domínio) ou TrustedHosts (workgroup)
3. **Escalável**: Adicionar 100 servidores = 0 configuração manual
4. **Seguro**: Credenciais criptografadas no banco
5. **Flexível**: Pode ter credenciais diferentes por servidor se necessário

---

## 📝 ARQUIVOS CRIADOS

1. `TESTAR_WMI_CORRETO_AGORA.txt` - Comandos corretos para testar WMI
2. `SOLUCAO_WMI_CREDENCIAIS_CENTRALIZADAS.md` - Arquitetura completa da solução
3. `IMPLEMENTAR_CREDENCIAIS_WMI_AGORA.txt` - Passo a passo para implementar
4. `RESOLVER_WMI_WORKGROUP_AGORA.txt` - Solução para workgroup (sem domínio)
5. `RESUMO_SITUACAO_WMI_11MAR_15H20.md` - Este arquivo

---

## 🎯 AÇÃO IMEDIATA

**COMECE AQUI**: `RESOLVER_WMI_WORKGROUP_AGORA.txt`

1. Configurar TrustedHosts na SRVSONDA001
2. Habilitar PSRemoting no 192.168.31.110
3. Testar conectividade WMI
4. Se funcionar: WMI está pronto! ✅

**DEPOIS**: Implementar credenciais centralizadas no código

---

## 📊 STATUS DOS SERVIDORES

| Servidor | IP | Domínio | Status WMI | Próximo Passo |
|----------|----|---------|-----------|--------------| 
| SRVSONDA001 | 192.168.31.? | ❌ Workgroup | ⏳ Pendente | Configurar TrustedHosts |
| SRVCMONITOR001 | 192.168.31.161 | ❌ Workgroup | N/A (Linux) | - |
| 192.168.31.110 | 192.168.31.110 | ✅ Domínio | ⏳ Pendente | Testar conectividade |
| Demais | Vários | ✅ Domínio | ⏳ Futuro | Criar usuário AD + GPO |

---

**Última atualização**: 11/03/2026 15:20  
**Próxima ação**: Testar WMI no workgroup (arquivo `RESOLVER_WMI_WORKGROUP_AGORA.txt`)
