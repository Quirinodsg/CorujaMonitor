# Arquitetura PRTG - Monitoramento Agentless (1 Sonda Central)

## ✅ IMPLEMENTADO - Arquitetura Estilo PRTG

Agora o Coruja Monitor funciona **exatamente como o PRTG**: 1 sonda central coleta dados de múltiplos servidores remotos sem instalar nada neles!

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│  SONDA CENTRAL (192.168.0.38)                               │
│  - 1 única instalação                                       │
│  - Coleta dados locais (máquina onde está instalada)        │
│  - Coleta dados remotos via WMI/SNMP/PING                   │
│  - Busca lista de servidores da API                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓ HTTPS
              ┌────────────────────────┐
              │   API CORUJA MONITOR   │
              │   - Lista de servidores│
              │   - Credenciais WMI    │
              │   - Recebe métricas    │
              └────────────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Servidor 1    │  │ Servidor 2    │  │ Router SNMP   │
│ 192.168.0.100 │  │ 192.168.0.101 │  │ 192.168.0.1   │
│               │  │               │  │               │
│ ❌ SEM AGENT  │  │ ❌ SEM AGENT  │  │ ❌ SEM AGENT  │
│ ✅ WMI ativo  │  │ ✅ WMI ativo  │  │ ✅ SNMP ativo │
│ ✅ Firewall   │  │ ✅ Firewall   │  │ ✅ Community  │
└───────────────┘  └───────────────┘  └───────────────┘
```

## 🔄 Fluxo de Coleta

### 1. Sonda Busca Lista de Servidores

```
Sonda → API: GET /api/v1/probes/servers?probe_token=XXX

API → Sonda: [
  {
    "id": 5,
    "hostname": "SERVER-01",
    "ip_address": "192.168.0.100",
    "monitoring_protocol": "wmi",
    "wmi_enabled": true,
    "wmi_username": "Administrator",
    "wmi_password": "senha_descriptografada",
    "wmi_domain": ""
  },
  {
    "id": 6,
    "hostname": "ROUTER-01",
    "ip_address": "192.168.0.1",
    "monitoring_protocol": "snmp",
    "snmp_community": "public",
    "snmp_version": "v2c"
  }
]
```

### 2. Sonda Coleta Métricas

Para cada servidor na lista:

**WMI (Windows)**:
```
Sonda → Servidor Windows (WMI):
  - Conecta usando credenciais
  - Coleta CPU, Memória, Disco, Serviços
  - Armazena no buffer
```

**SNMP (Router/Switch)**:
```
Sonda → Dispositivo SNMP:
  - Conecta usando community string
  - Coleta via OIDs SNMP
  - Armazena no buffer
```

**PING (Todos)**:
```
Sonda → Qualquer dispositivo:
  - ICMP ping
  - Mede latência
  - Detecta se está online
```

### 3. Sonda Envia Métricas

```
Sonda → API: POST /api/v1/metrics/probe/bulk
{
  "probe_token": "XXX",
  "metrics": [
    {
      "hostname": "SERVER-01",
      "sensor_type": "cpu",
      "value": 45.2,
      "status": "ok",
      ...
    },
    {
      "hostname": "ROUTER-01",
      "sensor_type": "snmp_traffic",
      "value": 1024000,
      "status": "ok",
      ...
    }
  ]
}
```

## 📋 Protocolos Suportados

### 1. WMI (Windows Management Instrumentation)

**Usado para**: Servidores Windows

**Requisitos no servidor remoto**:
- WMI habilitado (padrão no Windows)
- Firewall liberado (portas 135, 445)
- Usuário administrador

**Métricas coletadas**:
- CPU Usage
- Memory Usage
- Disk Usage
- Network Traffic
- Services Status
- Uptime

**Configuração**:
```powershell
# No servidor remoto
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"
Enable-NetFirewallRule -DisplayGroup "File and Printer Sharing"
```

### 2. SNMP (Simple Network Management Protocol)

**Usado para**: Routers, Switches, Firewalls, Impressoras, etc

**Requisitos no dispositivo**:
- SNMP habilitado
- Community string configurada

**Métricas coletadas**:
- Uptime
- CPU Load
- Memory Usage
- Interface Traffic
- Interface Status

**Configuração**:
```
# Exemplo Cisco
snmp-server community public RO
```

### 3. ICMP PING

**Usado para**: Todos os dispositivos

**Requisitos**:
- Dispositivo responde a ping
- Firewall permite ICMP

**Métricas coletadas**:
- Online/Offline
- Latência (ms)

## 🚀 Como Usar

### Passo 1: Adicionar Servidor na Interface Web

**Para Windows (WMI)**:
1. Ir para "Servidores"
2. Clicar em "Adicionar Servidor"
3. Preencher:
   - **Hostname**: SERVER-01
   - **IP**: 192.168.0.100
   - **Probe**: Selecionar probe instalada
   - **Protocolo**: WMI
   - **Usuário WMI**: Administrator
   - **Senha WMI**: senha_do_servidor
   - **Domínio**: (vazio para workgroup)
   - **Habilitar WMI**: ✓ Sim
4. Salvar

**Para SNMP (Router/Switch)**:
1. Ir para "Servidores"
2. Clicar em "Adicionar Servidor"
3. Preencher:
   - **Hostname**: ROUTER-01
   - **IP**: 192.168.0.1
   - **Probe**: Selecionar probe instalada
   - **Protocolo**: SNMP
   - **Versão SNMP**: v2c
   - **Community**: public
   - **Porta**: 161
4. Salvar

### Passo 2: Aguardar Coleta

A sonda irá:
1. Buscar a lista de servidores da API (a cada 60 segundos)
2. Coletar métricas de cada servidor
3. Enviar para a API
4. Dados aparecem na interface em 1-2 minutos

### Passo 3: Verificar Dados

1. Ir para "Servidores"
2. Selecionar o servidor adicionado
3. Ver sensores com dados atualizados

## 🔧 Configuração do Servidor Remoto (Windows)

### Para Monitoramento WMI Remoto

**No servidor que será monitorado (192.168.0.100)**:

```powershell
# Executar como Administrador

# 1. Habilitar WMI
Set-Service -Name Winmgmt -StartupType Automatic
Start-Service -Name Winmgmt

# 2. Habilitar Remote Registry
Set-Service -Name RemoteRegistry -StartupType Automatic
Start-Service -Name RemoteRegistry

# 3. Liberar firewall
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"
Enable-NetFirewallRule -DisplayGroup "File and Printer Sharing"

# 4. Criar usuário dedicado (opcional, mais seguro)
$Password = ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force
New-LocalUser -Name "CorujaMonitor" -Password $Password -Description "Usuario para monitoramento remoto"
Add-LocalGroupMember -Group "Administrators" -Member "CorujaMonitor"

# 5. Testar localmente
Get-WmiObject -Class Win32_OperatingSystem
```

### Testar Conexão Remota

**Na máquina onde está a sonda (192.168.0.38)**:

```powershell
# Testar WMI remoto
$credential = Get-Credential  # Digitar: Administrator e senha
Get-WmiObject -Class Win32_OperatingSystem -ComputerName 192.168.0.100 -Credential $credential

# Deve retornar informações do sistema operacional
```

## 📊 Comparação: Antes vs Depois

### ❌ Antes (Modo Agent)

```
Servidor 1: Instalar sonda ❌
Servidor 2: Instalar sonda ❌
Servidor 3: Instalar sonda ❌
Servidor 4: Instalar sonda ❌
Servidor 5: Instalar sonda ❌

Total: 5 instalações
Manutenção: 5 sondas para atualizar
```

### ✅ Depois (Modo Agentless - PRTG)

```
Sonda Central: 1 instalação ✅
Servidor 1: Configurar WMI ✅ (5 min)
Servidor 2: Configurar WMI ✅ (5 min)
Servidor 3: Configurar WMI ✅ (5 min)
Servidor 4: Configurar WMI ✅ (5 min)
Servidor 5: Configurar WMI ✅ (5 min)

Total: 1 instalação + configuração WMI
Manutenção: 1 sonda para atualizar
```

## 🎯 Vantagens da Arquitetura Agentless

### ✅ Vantagens
1. **1 única instalação** - Sonda central
2. **Fácil manutenção** - Atualizar apenas 1 sonda
3. **Escalável** - 1 sonda monitora centenas de servidores
4. **Flexível** - Suporta WMI, SNMP, PING
5. **Padrão da indústria** - Mesma arquitetura do PRTG, Zabbix, Nagios

### ⚠️ Requisitos
1. **Credenciais** - Precisa usuário/senha para WMI
2. **Firewall** - Precisa liberar portas (135, 445 para WMI)
3. **Rede** - Sonda precisa ter acesso de rede aos servidores
4. **Segurança** - Senhas armazenadas criptografadas no banco

## 🔐 Segurança

### Criptografia de Senhas

As senhas WMI são:
1. **Criptografadas** antes de salvar no banco (Fernet)
2. **Descriptografadas** apenas quando a sonda precisa usar
3. **Nunca expostas** na interface web
4. **Chave de criptografia** em variável de ambiente

### Boas Práticas

1. **Usar usuário dedicado** para monitoramento (não Administrator)
2. **Senha forte** e única para cada servidor
3. **Firewall** liberado apenas para IP da sonda
4. **Auditoria** de acessos WMI habilitada
5. **Rotação de senhas** periódica

## 📝 Troubleshooting

### Problema: Servidor sem dados

**Verificar**:
1. Sonda está rodando? `verificar_status.bat`
2. Servidor foi adicionado com credenciais WMI?
3. Firewall do servidor remoto está liberado?
4. Credenciais estão corretas?

**Testar manualmente**:
```powershell
# Na máquina da sonda
$cred = Get-Credential
Get-WmiObject -Class Win32_OperatingSystem -ComputerName 192.168.0.100 -Credential $cred
```

### Problema: "Access Denied"

**Causa**: Usuário sem permissões ou UAC bloqueando

**Solução**:
```powershell
# No servidor remoto
# Desabilitar UAC para acesso remoto (workgroup)
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

### Problema: "RPC Server Unavailable"

**Causa**: Firewall bloqueando ou serviço WMI parado

**Solução**:
```powershell
# No servidor remoto
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"
Start-Service -Name Winmgmt
```

## 🚀 Próximos Passos

1. ✅ **Adicionar servidores** na interface web com credenciais WMI
2. ✅ **Configurar WMI** nos servidores remotos
3. ✅ **Aguardar 1-2 minutos** - Dados aparecem automaticamente
4. ⏭️ **Implementar SNMP collector** (próxima versão)
5. ⏭️ **Adicionar SSH** para Linux (próxima versão)

---

**Data**: 13/02/2026 18:30 UTC
**Status**: ✅ IMPLEMENTADO
**Arquitetura**: PRTG-style Agentless (1 sonda central)
