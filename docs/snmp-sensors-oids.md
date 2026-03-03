# Sensores SNMP Padrão - OIDs Baseados em PRTG e Zabbix

## 📋 Sensores Criados Automaticamente para Dispositivos SNMP

Quando você adiciona um dispositivo com protocolo SNMP (router, switch, firewall, etc), os seguintes sensores são criados automaticamente:

### 1. PING (ICMP)
- **Tipo**: ping
- **Protocolo**: ICMP (não usa SNMP)
- **Descrição**: Verifica se o dispositivo está online
- **Thresholds**: 
  - Warning: 100ms
  - Critical: 200ms

### 2. SNMP Uptime
- **Tipo**: snmp_uptime
- **OID**: `1.3.6.1.2.1.1.3.0` (sysUpTime)
- **Descrição**: Tempo desde o último boot
- **Unidade**: Timeticks (centésimos de segundo)
- **MIB**: SNMPv2-MIB::sysUpTime.0

### 3. SNMP CPU Load
- **Tipo**: snmp_cpu
- **OID**: `1.3.6.1.4.1.2021.10.1.3.1` (laLoad.1)
- **Descrição**: Carga média de CPU (1 minuto)
- **Unidade**: Porcentagem
- **Thresholds**:
  - Warning: 80%
  - Critical: 95%
- **MIB**: UCD-SNMP-MIB::laLoad.1

**OIDs Alternativos**:
- Cisco: `1.3.6.1.4.1.9.2.1.56.0` (avgBusy5)
- HP: `1.3.6.1.4.1.11.2.14.11.5.1.9.6.1.0`
- Juniper: `1.3.6.1.4.1.2636.3.1.13.1.8`

### 4. SNMP Memory Usage
- **Tipo**: snmp_memory
- **OID**: `1.3.6.1.4.1.2021.4.6.0` (memTotalFree)
- **Descrição**: Memória livre total
- **Unidade**: KB
- **Thresholds**:
  - Warning: 80% usado
  - Critical: 95% usado
- **MIB**: UCD-SNMP-MIB::memTotalFree.0

**OIDs Relacionados**:
- Total RAM: `1.3.6.1.4.1.2021.4.5.0` (memTotalReal)
- RAM Usada: `1.3.6.1.4.1.2021.4.14.0` (memAvailReal)
- Buffer: `1.3.6.1.4.1.2021.4.15.0` (memBuffer)
- Cache: `1.3.6.1.4.1.2021.4.15.0` (memCached)

### 5. SNMP Traffic In
- **Tipo**: snmp_traffic
- **OID**: `1.3.6.1.2.1.2.2.1.10.1` (ifInOctets)
- **Descrição**: Bytes recebidos na interface 1
- **Unidade**: Bytes (contador)
- **Thresholds**:
  - Warning: 80 MB/s
  - Critical: 95 MB/s
- **MIB**: IF-MIB::ifInOctets.1

**Nota**: O `.1` no final é o índice da interface. Para outras interfaces, use `.2`, `.3`, etc.

### 6. SNMP Traffic Out
- **Tipo**: snmp_traffic
- **OID**: `1.3.6.1.2.1.2.2.1.16.1` (ifOutOctets)
- **Descrição**: Bytes enviados na interface 1
- **Unidade**: Bytes (contador)
- **Thresholds**:
  - Warning: 80 MB/s
  - Critical: 95 MB/s
- **MIB**: IF-MIB::ifOutOctets.1

### 7. SNMP Interface Status
- **Tipo**: snmp_interface
- **OID**: `1.3.6.1.2.1.2.2.1.8.1` (ifOperStatus)
- **Descrição**: Status operacional da interface 1
- **Valores**:
  - 1 = up (online)
  - 2 = down (offline)
  - 3 = testing
  - 4 = unknown
  - 5 = dormant
  - 6 = notPresent
  - 7 = lowerLayerDown
- **MIB**: IF-MIB::ifOperStatus.1

---

## 📊 OIDs SNMP Comuns por Fabricante

### Cisco
```
# System Info
sysDescr:       1.3.6.1.2.1.1.1.0
sysName:        1.3.6.1.2.1.1.5.0
sysLocation:    1.3.6.1.2.1.1.6.0

# CPU
avgBusy1:       1.3.6.1.4.1.9.2.1.57.0  (1 min)
avgBusy5:       1.3.6.1.4.1.9.2.1.56.0  (5 min)

# Memory
ciscoMemoryPoolUsed:  1.3.6.1.4.1.9.9.48.1.1.1.5.1
ciscoMemoryPoolFree:  1.3.6.1.4.1.9.9.48.1.1.1.6.1

# Temperature
ciscoEnvMonTemperatureStatusValue: 1.3.6.1.4.1.9.9.13.1.3.1.3
```

### HP/Aruba
```
# CPU
hpSwitchCpuStat: 1.3.6.1.4.1.11.2.14.11.5.1.9.6.1.0

# Memory
hpLocalMemTotalBytes: 1.3.6.1.4.1.11.2.14.11.5.1.1.2.1.1.1.5
hpLocalMemFreeBytes:  1.3.6.1.4.1.11.2.14.11.5.1.1.2.1.1.1.6
```

### Juniper
```
# CPU
jnxOperatingCPU: 1.3.6.1.4.1.2636.3.1.13.1.8

# Memory
jnxOperatingBuffer: 1.3.6.1.4.1.2636.3.1.13.1.11
```

### Mikrotik
```
# CPU
mtxrHlCoreVoltage: 1.3.6.1.4.1.14988.1.1.3.14.0
mtxrHlProcessorTemperature: 1.3.6.1.4.1.14988.1.1.3.11.0

# Memory
hrStorageUsed: 1.3.6.1.2.1.25.2.3.1.6.65536
hrStorageSize: 1.3.6.1.2.1.25.2.3.1.5.65536
```

### Ubiquiti (UniFi)
```
# System
unifiApSystemModel: 1.3.6.1.4.1.41112.1.6.3.3.0
unifiApSystemVersion: 1.3.6.1.4.1.41112.1.6.3.6.0

# Wireless
unifiVapNumStations: 1.3.6.1.4.1.41112.1.6.1.2.1.8
```

---

## 🔧 OIDs Genéricos (RFC Standard)

### System Group (RFC 1213)
```
sysDescr:       1.3.6.1.2.1.1.1.0    # Descrição do sistema
sysObjectID:    1.3.6.1.2.1.1.2.0    # OID do fabricante
sysUpTime:      1.3.6.1.2.1.1.3.0    # Uptime em timeticks
sysContact:     1.3.6.1.2.1.1.4.0    # Contato
sysName:        1.3.6.1.2.1.1.5.0    # Nome do host
sysLocation:    1.3.6.1.2.1.1.6.0    # Localização
sysServices:    1.3.6.1.2.1.1.7.0    # Serviços
```

### Interface Group (RFC 1213)
```
ifNumber:       1.3.6.1.2.1.2.1.0    # Número de interfaces
ifDescr:        1.3.6.1.2.1.2.2.1.2  # Descrição da interface
ifType:         1.3.6.1.2.1.2.2.1.3  # Tipo da interface
ifMtu:          1.3.6.1.2.1.2.2.1.4  # MTU
ifSpeed:        1.3.6.1.2.1.2.2.1.5  # Velocidade (bps)
ifPhysAddress:  1.3.6.1.2.1.2.2.1.6  # MAC address
ifAdminStatus:  1.3.6.1.2.1.2.2.1.7  # Status admin (1=up, 2=down)
ifOperStatus:   1.3.6.1.2.1.2.2.1.8  # Status operacional
ifInOctets:     1.3.6.1.2.1.2.2.1.10 # Bytes recebidos
ifInErrors:     1.3.6.1.2.1.2.2.1.14 # Erros de entrada
ifOutOctets:    1.3.6.1.2.1.2.2.1.16 # Bytes enviados
ifOutErrors:    1.3.6.1.2.1.2.2.1.20 # Erros de saída
```

### IP Group (RFC 1213)
```
ipForwarding:   1.3.6.1.2.1.4.1.0    # IP forwarding habilitado
ipInReceives:   1.3.6.1.2.1.4.3.0    # Pacotes IP recebidos
ipInDelivers:   1.3.6.1.2.1.4.9.0    # Pacotes IP entregues
ipOutRequests:  1.3.6.1.2.1.4.10.0   # Pacotes IP enviados
```

### ICMP Group (RFC 1213)
```
icmpInMsgs:     1.3.6.1.2.1.5.1.0    # ICMP mensagens recebidas
icmpInErrors:   1.3.6.1.2.1.5.2.0    # ICMP erros recebidos
icmpOutMsgs:    1.3.6.1.2.1.5.14.0   # ICMP mensagens enviadas
```

### TCP Group (RFC 1213)
```
tcpActiveOpens: 1.3.6.1.2.1.6.5.0    # Conexões TCP ativas abertas
tcpPassiveOpens:1.3.6.1.2.1.6.6.0    # Conexões TCP passivas abertas
tcpCurrEstab:   1.3.6.1.2.1.6.9.0    # Conexões TCP estabelecidas
tcpInSegs:      1.3.6.1.2.1.6.10.0   # Segmentos TCP recebidos
tcpOutSegs:     1.3.6.1.2.1.6.11.0   # Segmentos TCP enviados
```

### UDP Group (RFC 1213)
```
udpInDatagrams: 1.3.6.1.2.1.7.1.0    # Datagramas UDP recebidos
udpOutDatagrams:1.3.6.1.2.1.7.4.0    # Datagramas UDP enviados
```

---

## 🧪 Como Testar OIDs SNMP

### Windows (snmpwalk)
```cmd
# Instalar SNMP tools
# Download: https://www.ezfive.com/snmpsoft-tools/

snmpwalk -v2c -c public 192.168.0.1 1.3.6.1.2.1.1.1.0
```

### Linux
```bash
# Instalar
sudo apt-get install snmp snmp-mibs-downloader

# Testar
snmpwalk -v2c -c public 192.168.0.1 1.3.6.1.2.1.1.1.0

# Buscar OID específico
snmpget -v2c -c public 192.168.0.1 1.3.6.1.2.1.1.3.0
```

### PowerShell
```powershell
# Testar conectividade SNMP
Test-NetConnection -ComputerName 192.168.0.1 -Port 161

# Usar módulo SNMP (instalar primeiro)
Install-Module -Name SNMP
Get-SnmpData -IP 192.168.0.1 -OID "1.3.6.1.2.1.1.1.0" -Community "public"
```

---

## 📝 Referências

- **PRTG Sensor List**: https://www.paessler.com/manuals/prtg/available_sensor_types
- **Zabbix Templates**: https://www.zabbix.com/integrations
- **SNMP OID Reference**: http://www.oid-info.com/
- **Cisco SNMP OIDs**: https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/
- **RFC 1213 (MIB-II)**: https://datatracker.ietf.org/doc/html/rfc1213

---

**Nota**: Os OIDs podem variar dependendo do fabricante e modelo do dispositivo. Sempre consulte a documentação do fabricante para OIDs específicos.
