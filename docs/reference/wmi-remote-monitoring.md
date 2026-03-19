# Monitoramento WMI Remoto (Agentless)

## 📋 Visão Geral

O Coruja Monitor suporta dois modos de monitoramento:

### 1. Modo Sonda (Atual - Recomendado)
- ✅ Sonda instalada em cada servidor
- ✅ Coleta local usando `psutil`
- ✅ Não precisa credenciais
- ✅ Mais seguro e confiável
- ❌ Precisa instalar em cada servidor

### 2. Modo WMI Remoto (Agentless)
- ✅ 1 sonda monitora múltiplos servidores
- ✅ Não precisa instalar nada nos servidores remotos
- ⚠️ Precisa credenciais de administrador
- ⚠️ Precisa configurar firewall e WMI
- ⚠️ Menos seguro (credenciais trafegam na rede)

## 🔧 Configuração do Servidor Remoto (Windows)

### Passo 1: Habilitar WMI

```powershell
# Executar como Administrador

# 1. Habilitar serviço WMI
Set-Service -Name Winmgmt -StartupType Automatic
Start-Service -Name Winmgmt

# 2. Habilitar Remote Registry (necessário para WMI remoto)
Set-Service -Name RemoteRegistry -StartupType Automatic
Start-Service -Name RemoteRegistry

# 3. Verificar se WMI está funcionando localmente
Get-WmiObject -Class Win32_OperatingSystem
```

### Passo 2: Configurar Firewall

```powershell
# Habilitar regras de firewall para WMI

# Porta 135 (RPC Endpoint Mapper)
New-NetFirewallRule -DisplayName "WMI-In-TCP-135" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 135 `
    -Action Allow

# Porta 445 (SMB - necessária para DCOM)
New-NetFirewallRule -DisplayName "WMI-In-TCP-445" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 445 `
    -Action Allow

# Habilitar WMI no firewall (regra pré-definida)
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"

# Verificar regras
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*WMI*"}
```

### Passo 3: Configurar Permissões DCOM

```powershell
# Executar dcomcnfg.exe manualmente:

# 1. Abrir: dcomcnfg.exe
# 2. Navegar: Component Services > Computers > My Computer
# 3. Clicar com botão direito em "My Computer" > Properties
# 4. Aba "COM Security"
# 5. Em "Access Permissions", clicar "Edit Limits"
# 6. Adicionar o usuário que será usado para monitoramento
# 7. Dar permissões: Local Access e Remote Access
# 8. Em "Launch and Activation Permissions", clicar "Edit Limits"
# 9. Adicionar o mesmo usuário
# 10. Dar permissões: Local Launch, Remote Launch, Local Activation, Remote Activation
```

### Passo 4: Configurar Permissões WMI

```powershell
# Dar permissões WMI para o usuário de monitoramento

# 1. Abrir: wmimgmt.msc
# 2. Clicar com botão direito em "WMI Control (Local)" > Properties
# 3. Aba "Security"
# 4. Expandir "Root" e selecionar "CIMV2"
# 5. Clicar "Security"
# 6. Adicionar o usuário de monitoramento
# 7. Dar permissões:
#    - Enable Account
#    - Remote Enable
#    - Read Security
```

### Passo 5: Criar Usuário de Monitoramento (Recomendado)

```powershell
# Criar usuário dedicado para monitoramento (mais seguro)

# 1. Criar usuário local
$Password = ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force
New-LocalUser -Name "CorujaMonitor" `
    -Password $Password `
    -Description "Usuario para monitoramento WMI remoto" `
    -PasswordNeverExpires

# 2. Adicionar ao grupo Administrators (necessário para WMI completo)
Add-LocalGroupMember -Group "Administrators" -Member "CorujaMonitor"

# OU criar usuário com permissões mínimas (mais seguro, mas limitado)
# Adicionar aos grupos: "Distributed COM Users", "Performance Monitor Users"
Add-LocalGroupMember -Group "Distributed COM Users" -Member "CorujaMonitor"
Add-LocalGroupMember -Group "Performance Monitor Users" -Member "CorujaMonitor"
```

## 🔐 Segurança e Boas Práticas

### Opção 1: Usuário Administrador Local (Mais Simples)
```
Usuário: Administrator
Senha: [senha do administrador]
Domínio: [deixar vazio para máquina local]
```

**Prós:**
- ✅ Configuração mais simples
- ✅ Acesso completo a todas as métricas

**Contras:**
- ❌ Menos seguro (usa conta privilegiada)
- ❌ Senha do administrador exposta

### Opção 2: Usuário Dedicado (Recomendado)
```
Usuário: CorujaMonitor
Senha: [senha forte gerada]
Domínio: [deixar vazio]
```

**Prós:**
- ✅ Mais seguro (conta dedicada)
- ✅ Pode ser desabilitada sem afetar administração
- ✅ Auditoria mais fácil

**Contras:**
- ⚠️ Configuração mais complexa
- ⚠️ Precisa configurar permissões DCOM e WMI

### Opção 3: Conta de Domínio (Empresarial)
```
Usuário: DOMAIN\svc_monitoring
Senha: [senha gerenciada pelo AD]
Domínio: DOMAIN
```

**Prós:**
- ✅ Gerenciamento centralizado no Active Directory
- ✅ Políticas de senha do domínio
- ✅ Pode usar Group Policy para configurar WMI

**Contras:**
- ⚠️ Requer infraestrutura de domínio
- ⚠️ Mais complexo de configurar

## 🧪 Testar Conexão WMI

### Teste Local (no próprio servidor)
```powershell
# Testar WMI localmente
Get-WmiObject -Class Win32_OperatingSystem

# Deve retornar informações do sistema operacional
```

### Teste Remoto (de outro servidor)
```powershell
# Testar WMI remotamente
$credential = Get-Credential  # Digitar usuário e senha

Get-WmiObject -Class Win32_OperatingSystem `
    -ComputerName "192.168.0.38" `
    -Credential $credential

# Deve retornar informações do servidor remoto
```

### Teste com WMIC (linha de comando)
```cmd
REM Testar com wmic.exe
wmic /node:192.168.0.38 /user:Administrator /password:SenhaAqui os get caption

REM Deve retornar o nome do sistema operacional
```

## 📝 Configuração no Coruja Monitor

### 1. Executar Migração do Banco de Dados
```bash
cd api
python migrate_wmi_credentials.py
```

### 2. Adicionar Servidor com WMI na Interface

**Campos necessários:**
- **Hostname/IP**: 192.168.0.38
- **Protocolo de Monitoramento**: WMI
- **Usuário WMI**: Administrator (ou CorujaMonitor)
- **Senha WMI**: [senha do usuário]
- **Domínio WMI**: [deixar vazio para local, ou DOMAIN para domínio]
- **Habilitar WMI**: ✓ Sim

### 3. Configurar Sonda para Coletar via WMI

A sonda central irá:
1. Detectar servidores com `wmi_enabled = true`
2. Usar as credenciais armazenadas (criptografadas)
3. Conectar via WMI remoto
4. Coletar métricas (CPU, memória, disco, serviços)
5. Enviar para a API

## 🔒 Criptografia de Senhas

As senhas WMI são armazenadas criptografadas no banco de dados usando **Fernet** (criptografia simétrica).

### Gerar Chave de Criptografia
```python
from cryptography.fernet import Fernet

# Gerar chave (executar uma vez)
key = Fernet.generate_key()
print(key.decode())  # Salvar no .env como WMI_ENCRYPTION_KEY
```

### Adicionar no .env
```bash
# Chave para criptografar senhas WMI
WMI_ENCRYPTION_KEY=sua_chave_gerada_aqui
```

### Criptografar/Descriptografar Senhas
```python
from cryptography.fernet import Fernet
import os

# Carregar chave do ambiente
key = os.getenv('WMI_ENCRYPTION_KEY').encode()
cipher = Fernet(key)

# Criptografar senha
password = "SenhaForte123!"
encrypted = cipher.encrypt(password.encode())
print(encrypted.decode())  # Salvar no banco

# Descriptografar senha
decrypted = cipher.decrypt(encrypted)
print(decrypted.decode())  # Usar para conectar WMI
```

## 🚨 Troubleshooting

### Erro: "Access Denied"
**Causa**: Usuário sem permissões suficientes
**Solução**: 
- Verificar se usuário está no grupo Administrators
- Configurar permissões DCOM e WMI (passos 3 e 4)

### Erro: "RPC Server Unavailable"
**Causa**: Firewall bloqueando portas ou serviço WMI parado
**Solução**:
- Verificar firewall (passo 2)
- Verificar se serviço Winmgmt está rodando
- Testar conectividade: `Test-NetConnection -ComputerName 192.168.0.38 -Port 135`

### Erro: "The network path was not found"
**Causa**: Porta 445 (SMB) bloqueada ou serviço parado
**Solução**:
- Habilitar porta 445 no firewall
- Verificar se serviço "Server" está rodando
- Verificar se compartilhamento administrativo está habilitado

### Erro: "Invalid namespace"
**Causa**: Namespace WMI incorreto
**Solução**:
- Usar namespace padrão: `root\cimv2`
- Verificar se WMI não está corrompido: `winmgmt /verifyrepository`

## 📊 Comparação: Sonda vs WMI Remoto

| Característica | Sonda Local | WMI Remoto |
|----------------|-------------|------------|
| Instalação | Em cada servidor | 1 sonda central |
| Credenciais | Não precisa | Administrador |
| Segurança | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Configuração | Simples | Complexa |
| Firewall | Não precisa | Portas 135, 445 |
| Performance | Melhor | Boa |
| Confiabilidade | Alta | Média |
| Manutenção | Baixa | Média |
| Recomendado para | Produção | Testes/Lab |

## 🎯 Recomendação

**Para Produção**: Use o modo **Sonda Local**
- Mais seguro
- Mais confiável
- Mais fácil de manter
- Não expõe credenciais

**Para Testes/Lab**: Use **WMI Remoto**
- Rápido para testar
- Não precisa instalar em cada máquina
- Útil para monitoramento temporário

## 📚 Referências

- [Microsoft: WMI Security](https://docs.microsoft.com/en-us/windows/win32/wmisdk/securing-wmi-namespaces)
- [Microsoft: DCOM Security](https://docs.microsoft.com/en-us/windows/win32/com/dcom-security-enhancements)
- [PowerShell: Get-WmiObject](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-wmiobject)
