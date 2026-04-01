# Preparar Servidor para Monitoramento — Coruja Monitor

## Máquina Windows (via WMI)

Execute os comandos abaixo no servidor Windows como **Administrador** (PowerShell).

### 1. Habilitar WMI no Firewall

```powershell
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
```

### 2. Garantir que o serviço WMI está rodando

```powershell
Set-Service winmgmt -StartupType Automatic
Start-Service winmgmt
```

### 3. Verificar se está funcionando

```powershell
Get-Service winmgmt
# Status deve ser: Running
```

### Portas utilizadas pelo WMI

| Porta | Protocolo | Uso |
|-------|-----------|-----|
| 135   | TCP       | RPC Endpoint Mapper (obrigatória) |
| 49152–65535 | TCP | RPC dinâmico (WMI usa portas aleatórias nesse range) |

> Se houver firewall de rede entre a sonda e o servidor, libere a porta 135/TCP e o range dinâmico 49152-65535/TCP de entrada no servidor monitorado.

### Credencial necessária

O usuário precisa ser membro do grupo **Administrators** local ou do domínio, ou ter permissão explícita no WMI (DCOM).

No ambiente EmpresaXPTO, a credencial `DOMAIN\monitor.user` já está configurada no portal — nenhuma ação adicional é necessária no servidor além de habilitar o WMI.

### Verificação rápida (testar WMI remotamente da sonda)

```powershell
# Executar na SRVSONDA001, substituindo IP e credenciais
$cred = Get-Credential "DOMAIN\monitor.user"
Get-WmiObject -Class Win32_OperatingSystem -ComputerName "192.168.31.111" -Credential $cred
```

Se retornar dados do SO, o WMI está funcionando corretamente.

---

## Máquina Linux (via SNMP)

Execute os comandos abaixo no servidor Linux como **root** ou com **sudo**.

### 1. Instalar o agente SNMP

```bash
# Debian/Ubuntu
apt-get install -y snmpd snmp

# RHEL/CentOS/Rocky
yum install -y net-snmp net-snmp-utils
```

### 2. Configurar o SNMP (community string)

Edite o arquivo de configuração:

```bash
nano /etc/snmp/snmpd.conf
```

Substitua o conteúdo por (ou adicione as linhas):

```
# Permitir leitura com community "public" de qualquer IP
rocommunity public default

# Ou restringir apenas ao IP da sonda (recomendado)
rocommunity public 192.168.31.161

# Expor informações do sistema
syslocation "Datacenter"
syscontact "TI <ti@empresa.com>"

# Habilitar OIDs de CPU, memória e disco
extend-sh .1.3.6.1.4.1.2021.10 /bin/sh -c "cat /proc/loadavg"
```

### 3. Iniciar e habilitar o serviço

```bash
systemctl enable snmpd
systemctl start snmpd
systemctl status snmpd
```

### 4. Liberar no firewall

```bash
# UFW (Ubuntu)
ufw allow 161/udp
ufw reload

# firewalld (RHEL/CentOS)
firewall-cmd --permanent --add-port=161/udp
firewall-cmd --reload

# iptables direto
iptables -A INPUT -p udp --dport 161 -j ACCEPT
```

### Porta utilizada pelo SNMP

| Porta | Protocolo | Uso |
|-------|-----------|-----|
| 161   | UDP       | Consultas SNMP (obrigatória) |
| 162   | UDP       | SNMP Traps (opcional, não usado pelo Coruja) |

### 5. Verificar se está funcionando

```bash
# Testar localmente
snmpwalk -v2c -c public localhost 1.3.6.1.2.1.1

# Testar remotamente (da sonda ou do servidor Linux)
snmpwalk -v2c -c public 192.168.31.XXX 1.3.6.1.2.1.1
```

Se retornar dados do sistema (sysDescr, sysUpTime, etc.), o SNMP está funcionando.

---

## Resumo — O que cada protocolo coleta

| Métrica       | Windows (WMI) | Linux (SNMP) |
|---------------|:-------------:|:------------:|
| CPU           | ✅            | ✅           |
| Memória       | ✅            | ✅           |
| Disco         | ✅            | ✅           |
| Uptime        | ✅            | ✅           |
| Network IN/OUT| ✅            | ❌ (parcial) |
| Ping          | ✅ (worker)   | ✅ (worker)  |

---

## Após configurar

1. Acesse o portal Coruja Monitor
2. Vá em **Servidores → Adicionar Servidor**
3. Preencha hostname e IP
4. Selecione o protocolo: **WMI** (Windows) ou **SNMP** (Linux)
5. A credencial WMI é herdada automaticamente do tenant (EmpresaXPTO)
6. Para SNMP, informe a community string configurada (ex: `public`)
7. Aguarde o próximo ciclo da sonda (~60 segundos) — os sensores começarão a mostrar dados
