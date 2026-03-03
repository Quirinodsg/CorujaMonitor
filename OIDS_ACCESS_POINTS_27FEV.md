# OIDs SNMP para Monitoramento de Access Points WiFi

## OIDs Padrão (IEEE 802.11 MIB)

### Status e Informações Básicas
```
sysDescr: 1.3.6.1.2.1.1.1.0                    # Descrição do sistema
sysUpTime: 1.3.6.1.2.1.1.3.0                   # Uptime em centésimos de segundo
sysName: 1.3.6.1.2.1.1.5.0                     # Nome do dispositivo
```

### Carga - CPU e Memória
```
hrProcessorLoad: 1.3.6.1.2.1.25.3.3.1.2        # CPU % (HOST-RESOURCES-MIB)
hrStorageUsed: 1.3.6.1.2.1.25.2.3.1.6          # Memória usada
hrStorageSize: 1.3.6.1.2.1.25.2.3.1.5          # Memória total
```

### Carga - Clientes Conectados
```
dot11CurrentChannelNumber: 1.3.6.1.2.1.10.127.1.1.1.1.4    # Canal atual
dot11StationID: 1.3.6.1.2.1.10.127.1.2.1.1.1               # MAC dos clientes
```

### Tráfego - Interfaces
```
ifInOctets: 1.3.6.1.2.1.2.2.1.10               # Bytes recebidos
ifOutOctets: 1.3.6.1.2.1.2.2.1.16              # Bytes enviados
ifInUcastPkts: 1.3.6.1.2.1.2.2.1.11            # Pacotes unicast recebidos
ifOutUcastPkts: 1.3.6.1.2.1.2.2.1.17           # Pacotes unicast enviados
ifInErrors: 1.3.6.1.2.1.2.2.1.14               # Erros de entrada
ifOutErrors: 1.3.6.1.2.1.2.2.1.20              # Erros de saída
ifInDiscards: 1.3.6.1.2.1.2.2.1.13             # Pacotes descartados (entrada)
ifOutDiscards: 1.3.6.1.2.1.2.2.1.19            # Pacotes descartados (saída)
ifSpeed: 1.3.6.1.2.1.2.2.1.5                   # Velocidade da interface
ifOperStatus: 1.3.6.1.2.1.2.2.1.8              # Status operacional (1=up, 2=down)
```

### Sinais - Qualidade WiFi
```
dot11TransmittedFragmentCount: 1.3.6.1.2.1.10.127.1.1.2.1.1    # Fragmentos transmitidos
dot11ReceivedFragmentCount: 1.3.6.1.2.1.10.127.1.1.2.1.2       # Fragmentos recebidos
dot11FailedCount: 1.3.6.1.2.1.10.127.1.1.2.1.12                # Transmissões falhadas
dot11RetryCount: 1.3.6.1.2.1.10.127.1.1.2.1.13                 # Retransmissões
```

---

## OIDs Específicos por Fabricante

### Ubiquiti UniFi
```
# Clientes conectados
unifiVapNumStations: 1.3.6.1.4.1.41112.1.6.1.2.1.8             # Número de clientes por VAP

# Estatísticas de rádio
unifiRadioTxPower: 1.3.6.1.4.1.41112.1.6.1.2.1.4               # Potência TX
unifiRadioChannel: 1.3.6.1.4.1.41112.1.6.1.2.1.5               # Canal
unifiRadioNumStations: 1.3.6.1.4.1.41112.1.6.1.2.1.7           # Clientes por rádio

# Estatísticas de clientes
unifiStaRssi: 1.3.6.1.4.1.41112.1.6.1.3.1.5                    # RSSI do cliente
unifiStaTxBytes: 1.3.6.1.4.1.41112.1.6.1.3.1.6                 # Bytes TX
unifiStaRxBytes: 1.3.6.1.4.1.41112.1.6.1.3.1.7                 # Bytes RX
```

### MikroTik
```
# Clientes conectados
mtxrWlApClientCount: 1.3.6.1.4.1.14988.1.1.1.3.1.6             # Número de clientes

# Estatísticas de interface wireless
mtxrWlApTxRate: 1.3.6.1.4.1.14988.1.1.1.3.1.2                  # Taxa TX
mtxrWlApRxRate: 1.3.6.1.4.1.14988.1.1.1.3.1.3                  # Taxa RX
mtxrWlApSsid: 1.3.6.1.4.1.14988.1.1.1.3.1.4                    # SSID
mtxrWlApFreq: 1.3.6.1.4.1.14988.1.1.1.3.1.7                    # Frequência

# Estatísticas de clientes
mtxrWlRtabStrength: 1.3.6.1.4.1.14988.1.1.1.2.1.3              # Força do sinal
mtxrWlRtabTxBytes: 1.3.6.1.4.1.14988.1.1.1.2.1.4               # Bytes TX
mtxrWlRtabRxBytes: 1.3.6.1.4.1.14988.1.1.1.2.1.5               # Bytes RX
```

### Cisco Aironet
```
# Clientes conectados
cDot11ActiveDevicesCount: 1.3.6.1.4.1.9.9.273.1.1.2.1.1        # Dispositivos ativos

# Estatísticas de rádio
cDot11ChannelNumber: 1.3.6.1.4.1.9.9.272.1.1.1.1.4             # Canal
cDot11TxPowerLevel: 1.3.6.1.4.1.9.9.272.1.1.1.1.3              # Potência TX

# Qualidade do sinal
cDot11ClientSignalStrength: 1.3.6.1.4.1.9.9.273.1.3.1.1.2      # RSSI
cDot11ClientSNR: 1.3.6.1.4.1.9.9.273.1.3.1.1.3                 # SNR
```

### TP-Link EAP
```
# Sistema
tpLinkApSysUptime: 1.3.6.1.4.1.11863.6.1.1.1.0                 # Uptime
tpLinkApSysCpuUsage: 1.3.6.1.4.1.11863.6.1.1.2.0               # CPU %
tpLinkApSysMemUsage: 1.3.6.1.4.1.11863.6.1.1.3.0               # Memória %

# Wireless
tpLinkApWirelessClientNum: 1.3.6.1.4.1.11863.6.2.1.1.2         # Número de clientes
```

### Aruba
```
# Clientes conectados
wlsxWlanAPNumClients: 1.3.6.1.4.1.14823.2.2.1.5.2.1.5.1.2      # Clientes por AP

# Estatísticas de rádio
wlsxWlanRadioChannel: 1.3.6.1.4.1.14823.2.2.1.5.3.1.1.1.3      # Canal
wlsxWlanRadioTxPower: 1.3.6.1.4.1.14823.2.2.1.5.3.1.1.1.4      # Potência TX
```

---

## Cálculos e Fórmulas

### Taxa de Utilização (%)
```
Utilização = ((ifInOctets + ifOutOctets) / ifSpeed) * 100
```

### Taxa de Erro (%)
```
Taxa de Erro = ((ifInErrors + ifOutErrors) / (ifInUcastPkts + ifOutUcastPkts)) * 100
```

### Throughput (Mbps)
```
Throughput = ((ifInOctets_atual - ifInOctets_anterior) * 8) / (tempo_decorrido * 1000000)
```

### Qualidade do Sinal
```
Excelente: RSSI > -50 dBm
Bom: -50 a -60 dBm
Regular: -60 a -70 dBm
Fraco: -70 a -80 dBm
Muito Fraco: < -80 dBm
```

### SNR (Signal-to-Noise Ratio)
```
Excelente: SNR > 40 dB
Bom: 25-40 dB
Regular: 15-25 dB
Fraco: 10-15 dB
Muito Fraco: < 10 dB
```

---

## Comandos de Teste

### Testar SNMP Walk
```bash
# Informações básicas
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.1

# Interfaces
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.2.2

# Wireless (802.11)
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.10.127

# CPU e Memória
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.25.3.3
```

### Testar OID Específico
```bash
# Número de clientes (UniFi)
snmpget -v2c -c public 192.168.1.1 1.3.6.1.4.1.41112.1.6.1.2.1.8.1

# CPU %
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.25.3.3.1.2.1

# Uptime
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.3.0
```

---

## Thresholds Recomendados

### CPU
- Warning: 70%
- Critical: 85%

### Memória
- Warning: 80%
- Critical: 90%

### Clientes Conectados
- Warning: 80% da capacidade máxima
- Critical: 95% da capacidade máxima

### RSSI
- Warning: < -70 dBm
- Critical: < -80 dBm

### Taxa de Erro
- Warning: > 1%
- Critical: > 5%

### Retransmissões
- Warning: > 10%
- Critical: > 20%
