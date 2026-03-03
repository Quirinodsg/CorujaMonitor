# Guia Completo: Monitoramento Agentless (CheckMK/PRTG Style)

## 🎯 VISÃO GERAL

O Coruja Monitor suporta monitoramento **agentless** (sem agente) de máquinas na rede usando as mesmas técnicas do CheckMK e PRTG:

- **WMI** (Windows Management Instrumentation) para Windows
- **SNMP** (Simple Network Management Protocol) para dispositivos de rede
- **SSH** para Linux (futuro)

## 📋 ARQUITETURA

```
┌─────────────────────────────────────────────────────────────┐
│                    CORUJA MONITOR API                        │
│                  (Servidor Central)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    PROBE (Sonda)                             │
│              Instalada em 1 Máquina                          │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Local    │  │    WMI     │  │   SNMP     │           │
│  │ Collector  │  │ Collector  │  │ Collector  │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────┬───────────────┬───────────────┬─────────────────────┘
       │               │               │
       │               │               │
   ┌───▼───┐      ┌────▼────┐     ┌───▼────┐
   │ Local │      │ Windows │     │Network │
   │Machine│      │ Servers │     │Devices │
   └───────┘      └─────────┘     └────────┘
                  (via WMI)       (via SNMP)
```

## 🔧 CONFIGURAÇÃO PASSO A PASSO

### 1. Preparar Máquinas Windows para WMI Remoto

#### 1.1. Configurar Firewall (Em TODAS as máquinas a monitorar)

```powershell
# Executar como Administrador
# Habilitar regras WMI no Firewall
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"

# OU criar regra manualmente
New-NetFirewallRule -DisplayName "WMI-In" -Direction Inbound -Protocol TCP -LocalPort 135 -Action Allow
New-NetFirewallRule -DisplayName "WMI-DCOM" -Direction Inbound -Protocol TCP -LocalPort 49152-65535 -Action Allow
```

#### 1.2. Configurar DCOM

```powershell
# Configurar DCOM para aceitar conexões remotas
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Ole" -Name "EnableDCOM" -Value "Y"

# Configurar autenticação
dcomcnfg
# Navegar: Component Services > Computers > My Computer
# Botão direito > Properties > COM Security
# Em "Access Permissions" e "Launch and Activation Permissions"
# Adicionar o usuário que será usado para monitoramento
```

#### 1.3. Criar Usuário de Monitoramento (Recomendado)

```powershell
# Criar usuário dedicado para monitoramento
$Password = ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force
New-LocalUser "MonitorUser" -Password $Password -FullName "Coruja Monitor" -Description "Usuário para monitoramento remoto"

# Adicionar aos grupos necessários
Add-LocalGroupMember -Group "Administrators" -Member "MonitorUser"
# OU (mais seguro)
Add-LocalGroupMember -Group "Performance Monitor Users" -Member "MonitorUser"
Add-LocalGroupMember -Group "Distributed COM Users" -Member "MonitorUser"
```

#### 1.4. Testar Conexão WMI

```powershell
# Da máquina com a Probe, testar conexão
$cred = Get-Credential  # Usar MonitorUser
Get-WmiObject -Class Win32_OperatingSystem -ComputerName "SERVER01" -Credential $cred
```

### 2. Configurar Probe para Monitoramento Remoto

#### 2.1. Criar Arquivo de Credenciais WMI

Criar arquivo: `probe/wmi_credentials.json`

```json
{
  "servers": [
    {
      "hostname": "SERVER01",
      "ip": "192.168.1.10",
      "username": "MonitorUser",
      "password": "SenhaForte123!",
      "domain": "WORKGROUP",
      "description": "Servidor de Aplicação"
    },
    {
      "hostname": "SERVER02",
      "ip": "192.168.1.11",
      "username": "DOMAIN\\MonitorUser",
      "password": "SenhaForte123!",
      "domain": "EMPRESA",
      "description": "Controlador de Domínio"
    },
    {
      "hostname": "SERVER03",
      "ip": "192.168.1.12",
      "username": "Administrator",
      "password": "AdminPass123!",
      "domain": "WORKGROUP",
      "description": "Servidor de Banco de Dados"
    }
  ]
}
```

**⚠️ SEGURANÇA**: Este arquivo contém senhas. Proteja-o:
```powershell
# Definir permissões apenas para o usuário da probe
icacls "wmi_credentials.json" /inheritance:r /grant:r "%USERNAME%:F"
```

#### 2.2. Habilitar Coletor WMI Remoto

Editar `probe/probe_config.json`:

```json
{
  "api_url": "http://localhost:8000",
  "probe_token": "SEU_TOKEN_AQUI",
  "collection_interval": 60,
  "collectors": {
    "local": {
      "enabled": true,
      "types": ["system", "cpu", "memory", "disk", "network", "docker"]
    },
    "wmi_remote": {
      "enabled": true,
      "credentials_file": "wmi_credentials.json",
      "timeout": 30,
      "retry_count": 3
    },
    "snmp": {
      "enabled": true,
      "devices_file": "snmp_devices.json",
      "timeout": 10
    }
  }
}
```

### 3. Configurar Dispositivos SNMP

#### 3.1. Habilitar SNMP em Switches/Roteadores

**Cisco:**
```
configure terminal
snmp-server community public RO
snmp-server location "Datacenter Principal"
snmp-server contact "admin@empresa.com"
end
write memory
```

**HP/Aruba:**
```
snmp-server community public
snmp-server location "Datacenter Principal"
```

**Impressoras HP:**
- Acessar interface web da impressora
- Ir em: Networking > SNMP
- Habilitar SNMP v1/v2
- Definir community: `public` (leitura)

#### 3.2. Criar Arquivo de Dispositivos SNMP

Criar arquivo: `probe/snmp_devices.json`

```json
{
  "devices": [
    {
      "hostname": "SWITCH-CORE",
      "ip": "192.168.1.1",
      "type": "switch",
      "version": "v2c",
      "community": "public",
      "port": 161,
      "description": "Switch Core Datacenter"
    },
    {
      "hostname": "ROUTER-PRINCIPAL",
      "ip": "192.168.1.254",
      "type": "router",
      "version": "v2c",
      "community": "public",
      "port": 161,
      "description": "Roteador Principal"
    },
    {
      "hostname": "PRINTER-RH",
      "ip": "192.168.1.50",
      "type": "printer",
      "version": "v2c",
      "community": "public",
      "port": 161,
      "description": "Impressora HP RH"
    },
    {
      "hostname": "UPS-DATACENTER",
      "ip": "192.168.1.100",
      "type": "ups",
      "version": "v2c",
      "community": "public",
      "port": 161,
      "description": "Nobreak APC Datacenter"
    }
  ]
}
```

#### 3.3. SNMP v3 (Mais Seguro)

```json
{
  "devices": [
    {
      "hostname": "SWITCH-SEGURO",
      "ip": "192.168.1.2",
      "type": "switch",
      "version": "v3",
      "username": "snmpuser",
      "auth_protocol": "SHA",
      "auth_key": "AuthPassword123",
      "priv_protocol": "AES",
      "priv_key": "PrivPassword123",
      "port": 161,
      "description": "Switch com SNMP v3"
    }
  ]
}
```

### 4. Adicionar Servidores Remotos via Interface Web

#### 4.1. Via Interface (Recomendado)

1. Acesse **Servidores** no menu
2. Clique em **+ Adicionar Servidor**
3. Preencha:
   - **Nome**: SERVER01
   - **IP**: 192.168.1.10
   - **Tipo**: Windows (WMI) ou SNMP
   - **Credenciais**: Selecione ou adicione novas
4. Clique em **Descobrir Sensores**
5. Selecione os sensores desejados
6. Clique em **Adicionar**

#### 4.2. Via API (Automação)

```bash
# Adicionar servidor Windows via WMI
curl -X POST http://localhost:8000/api/v1/servers/remote \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "SERVER01",
    "ip_address": "192.168.1.10",
    "os_type": "Windows",
    "monitoring_type": "wmi",
    "credentials": {
      "username": "MonitorUser",
      "password": "SenhaForte123!",
      "domain": "WORKGROUP"
    }
  }'

# Adicionar dispositivo SNMP
curl -X POST http://localhost:8000/api/v1/servers/remote \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "SWITCH-CORE",
    "ip_address": "192.168.1.1",
    "device_type": "switch",
    "monitoring_type": "snmp",
    "snmp_config": {
      "version": "v2c",
      "community": "public",
      "port": 161
    }
  }'
```

## 📊 MÉTRICAS COLETADAS

### Windows via WMI
- ✅ CPU (uso, frequência, núcleos)
- ✅ Memória (total, usado, disponível)
- ✅ Disco (espaço, I/O, latência)
- ✅ Rede (tráfego, pacotes, erros)
- ✅ Serviços (status, startup type)
- ✅ Processos (CPU, memória por processo)
- ✅ Event Logs (erros, warnings)
- ✅ Uptime
- ✅ Temperatura (se disponível)

### Dispositivos SNMP

**Switches/Roteadores:**
- ✅ Interfaces (status, tráfego, erros)
- ✅ CPU e Memória
- ✅ Temperatura
- ✅ Uptime
- ✅ Tabela ARP
- ✅ Tabela de rotas

**Impressoras:**
- ✅ Níveis de toner (todas as cores)
- ✅ Contador de páginas
- ✅ Status (online/offline/erro)
- ✅ Papel atolado
- ✅ Erros de hardware
- ✅ Modelo e serial

**Nobreaks (UPS):**
- ✅ Carga da bateria (%)
- ✅ Tempo restante
- ✅ Voltagem entrada/saída
- ✅ Frequência
- ✅ Status (online/bateria/bypass)
- ✅ Temperatura

## 🔐 MELHORES PRÁTICAS DE SEGURANÇA

### 1. Usuário Dedicado
```powershell
# Criar usuário com privilégios mínimos
New-LocalUser "MonitorUser" -Password $SecurePassword
Add-LocalGroupMember -Group "Performance Monitor Users" -Member "MonitorUser"
Add-LocalGroupMember -Group "Event Log Readers" -Member "MonitorUser"
```

### 2. Firewall Restrito
```powershell
# Permitir WMI apenas da máquina com Probe
New-NetFirewallRule -DisplayName "WMI-Probe" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 135,49152-65535 `
  -RemoteAddress 192.168.1.5 `
  -Action Allow
```

### 3. Criptografia de Credenciais
```python
# Na probe, usar criptografia para senhas
from cryptography.fernet import Fernet

# Gerar chave (uma vez)
key = Fernet.generate_key()
cipher = Fernet(key)

# Criptografar senha
encrypted_password = cipher.encrypt(b"SenhaForte123!")

# Descriptografar ao usar
password = cipher.decrypt(encrypted_password).decode()
```

### 4. SNMP v3 (Sempre que Possível)
- Usar autenticação SHA/MD5
- Usar criptografia AES/DES
- Trocar senhas regularmente

### 5. Auditoria
- Logar todas as conexões remotas
- Monitorar tentativas de acesso
- Revisar logs regularmente

## 🚀 DESCOBERTA AUTOMÁTICA

### Scan de Rede (Futuro)

```python
# probe/network_discovery.py
import nmap

def discover_network(network_range="192.168.1.0/24"):
    """Descobre dispositivos na rede"""
    nm = nmap.PortScanner()
    nm.scan(hosts=network_range, arguments='-sn')  # Ping scan
    
    devices = []
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            devices.append({
                'ip': host,
                'hostname': nm[host].hostname(),
                'mac': nm[host]['addresses'].get('mac', ''),
                'vendor': nm[host]['vendor'].get(nm[host]['addresses'].get('mac', ''), '')
            })
    
    return devices

def detect_os_and_services(ip):
    """Detecta SO e serviços"""
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-O -sV')  # OS detection + Service version
    
    return {
        'os': nm[ip].get('osmatch', [{}])[0].get('name', 'Unknown'),
        'services': [
            {
                'port': port,
                'name': nm[ip]['tcp'][port]['name'],
                'version': nm[ip]['tcp'][port].get('version', '')
            }
            for port in nm[ip].get('tcp', {})
        ]
    }
```

## 📝 TROUBLESHOOTING

### Problema: WMI não conecta

**Solução 1: Verificar Firewall**
```powershell
Test-NetConnection -ComputerName SERVER01 -Port 135
```

**Solução 2: Verificar Credenciais**
```powershell
$cred = Get-Credential
Get-WmiObject -Class Win32_OperatingSystem -ComputerName SERVER01 -Credential $cred
```

**Solução 3: Verificar DCOM**
```powershell
Get-Service -Name RpcSs  # Deve estar Running
Get-Service -Name Winmgmt  # Deve estar Running
```

### Problema: SNMP não responde

**Solução 1: Testar SNMP**
```bash
snmpwalk -v2c -c public 192.168.1.1 system
```

**Solução 2: Verificar Community**
- Conferir se community está correta
- Verificar se IP da probe está autorizado

**Solução 3: Verificar Firewall**
```bash
nmap -sU -p 161 192.168.1.1
```

## 📚 REFERÊNCIAS

### Documentação Oficial
- [Microsoft WMI](https://docs.microsoft.com/en-us/windows/win32/wmisdk/)
- [SNMP RFCs](https://www.ietf.org/rfc/rfc1157.txt)
- [CheckMK Agentless](https://docs.checkmk.com/latest/en/wmi.html)
- [PRTG SNMP](https://www.paessler.com/manuals/prtg/snmp_monitoring)

### OIDs Úteis
- **System**: 1.3.6.1.2.1.1
- **Interfaces**: 1.3.6.1.2.1.2
- **IP**: 1.3.6.1.2.1.4
- **ICMP**: 1.3.6.1.2.1.5
- **TCP**: 1.3.6.1.2.1.6
- **UDP**: 1.3.6.1.2.1.7

---

**Data**: 20/02/2026  
**Versão**: 1.0  
**Status**: ✅ Implementado  
**Baseado em**: CheckMK, PRTG, Zabbix
