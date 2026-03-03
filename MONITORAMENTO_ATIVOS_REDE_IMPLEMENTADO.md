# Monitoramento de Ativos de Rede - IMPLEMENTADO ✅

## Data: 25 de Fevereiro de 2026

## Novos Sensores Adicionados

### 1. Access Point (AP) WiFi 📶
- **Tipo**: `snmp_ap`
- **Ícone**: 📶
- **Descrição**: Monitora Access Points WiFi via SNMP
- **Métricas**:
  - Uptime (tempo de atividade)
  - Status da interface (online/offline)
  - Informações do dispositivo
  - Descrição e nome do AP
- **Thresholds Padrão**:
  - Warning: 80%
  - Critical: 95%
- **Fabricantes Suportados**:
  - Ubiquiti UniFi
  - Cisco Aironet
  - TP-Link
  - Aruba
  - Qualquer AP com SNMP habilitado

### 2. Ar-Condicionado ❄️
- **Tipo**: `snmp_ac`
- **Ícone**: ❄️
- **Descrição**: Monitora ar-condicionado via SNMP
- **Métricas**:
  - Temperatura (°C)
  - Status do dispositivo
  - Uptime
  - Temperatura de insuflamento
  - Temperatura de retorno
- **Thresholds Padrão**:
  - Warning: 28°C
  - Critical: 32°C
- **Fabricantes Suportados**:
  - APC InRow
  - Liebert
  - Schneider Electric
  - Qualquer AC com SNMP habilitado

### 3. Nobreak (UPS) 🔋
- **Tipo**: `snmp_ups`
- **Ícone**: 🔋
- **Descrição**: Monitora nobreak via SNMP
- **Métricas**:
  - Nível de bateria (%)
  - Carga atual
  - Tempo restante
  - Status do dispositivo
- **Thresholds Padrão**:
  - Warning: 30%
  - Critical: 15%
- **Já estava implementado** (agora com melhor descrição)

## Arquivos Criados

### 1. `probe/collectors/snmp_ap_collector.py`
Coletor especializado para Access Points WiFi:
- Coleta via SNMP v1/v2c/v3
- Suporte a múltiplos fabricantes
- OIDs padrão IEEE 802.11
- OIDs específicos por fabricante
- Teste standalone incluído

### 2. `probe/collectors/snmp_ac_collector.py`
Coletor especializado para Ar-Condicionado:
- Coleta temperatura via SNMP
- Suporte a múltiplos fabricantes
- Fallback para OIDs genéricos
- Alertas baseados em temperatura
- Teste standalone incluído

### 3. `frontend/src/data/sensorTemplates.js` (Atualizado)
Templates de sensores atualizados com:
- Access Point na categoria SNMP
- Ar-Condicionado na categoria SNMP
- Nobreak com descrição melhorada
- Todos marcados como `recommended: true`

## Como Usar

### 1. Adicionar Dispositivo SNMP

1. Vá em **Servidores** → Selecione um servidor
2. Clique em **+ Adicionar Sensor**
3. Vá na aba **SNMP** 📡
4. Escolha o tipo de dispositivo:
   - **Access Point (AP)** 📶
   - **Ar-Condicionado** ❄️
   - **Nobreak (UPS)** 🔋

### 2. Configurar o Dispositivo

Antes de adicionar o sensor, certifique-se que:

#### Para Access Points:
- SNMP está habilitado no AP
- Community string está configurada (ex: `public`)
- Firewall permite porta 161 (SNMP)
- AP está acessível pela probe

#### Para Ar-Condicionado:
- SNMP está habilitado no controlador do AC
- Community string está configurada
- Porta 161 está acessível
- Verifique o manual do fabricante para OIDs específicos

#### Para Nobreak:
- SNMP está habilitado no UPS
- Community string está configurada
- Porta 161 está acessível
- Cabo de rede conectado ao UPS

### 3. Adicionar o Dispositivo como Servidor

Primeiro, adicione o dispositivo como servidor:

1. Vá em **Servidores** → **+ Adicionar Servidor**
2. Preencha:
   - **Probe**: Selecione a probe que irá monitorar
   - **Tipo de Dispositivo**: 
     - Para AP: Selecione "Outro" ou crie tipo específico
     - Para AC: Selecione "Outro"
     - Para UPS: Selecione "Nobreak"
   - **Nome**: Ex: "AP-Sala-01", "AC-Datacenter", "UPS-Principal"
   - **IP**: IP do dispositivo na rede
   - **Protocolo**: **SNMP**
   - **Versão SNMP**: v2c (recomendado)
   - **Community String**: `public` (ou sua community)
   - **Porta SNMP**: 161

3. Clique em **Adicionar Dispositivo**

### 4. Adicionar Sensor SNMP

Depois de adicionar o dispositivo:

1. Selecione o servidor na lista lateral
2. Clique em **+ Adicionar Sensor**
3. Vá na aba **SNMP**
4. Selecione o template apropriado
5. Configure os thresholds se necessário
6. Clique em **Adicionar Sensor**

## Testando os Coletores

### Teste do Access Point:
```bash
cd probe/collectors
python snmp_ap_collector.py 192.168.1.100 public 161
```

### Teste do Ar-Condicionado:
```bash
cd probe/collectors
python snmp_ac_collector.py 192.168.1.200 public 161
```

### Saída Esperada:
```
🔍 Testando coleta SNMP do Access Point 192.168.1.100...
   Community: public
   Porta: 161

✅ Métricas coletadas com sucesso!

📊 Resultados:
   description: Ubiquiti UniFi AP-AC-PRO
   uptime: 15.5
   name: AP-Sala-01
   status: online
   timestamp: 2026-02-25T10:30:00
   target_ip: 192.168.1.100

📦 Métricas formatadas:
   Status: ok
   Valor: 15.5 days
   Metadata: {...}
```

## OIDs SNMP Utilizados

### Access Points:
```
System Info (RFC 1213):
- sysDescr: 1.3.6.1.2.1.1.1.0
- sysUpTime: 1.3.6.1.2.1.1.3.0
- sysName: 1.3.6.1.2.1.1.5.0

Interface Stats:
- ifOperStatus: 1.3.6.1.2.1.2.2.1.8

Ubiquiti UniFi:
- unifiApSystemModel: 1.3.6.1.4.1.41112.1.6.3.3.0
- unifiApSystemVersion: 1.3.6.1.4.1.41112.1.6.3.6.0

Cisco Aironet:
- cDot11ActiveDevices: 1.3.6.1.4.1.9.9.273.1.1.2.1.1
```

### Ar-Condicionado:
```
System Info (RFC 1213):
- sysDescr: 1.3.6.1.2.1.1.1.0
- sysUpTime: 1.3.6.1.2.1.1.3.0

APC InRow:
- apcInRowSupplyAirTemp: 1.3.6.1.4.1.318.1.1.13.3.2.2.2.3.0
- apcInRowReturnAirTemp: 1.3.6.1.4.1.318.1.1.13.3.2.2.2.4.0
- apcInRowStatus: 1.3.6.1.4.1.318.1.1.13.3.2.2.2.9.0

Liebert:
- liebertSupplyAirTemp: 1.3.6.1.4.1.476.1.42.3.4.1.2.3.1.4.0
- liebertReturnAirTemp: 1.3.6.1.4.1.476.1.42.3.4.1.2.3.1.5.0

Genérico:
- ambientTemp: 1.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1
```

## Troubleshooting

### Problema: "SNMP Error: Timeout"
**Solução**:
- Verifique se o IP está correto
- Verifique se o dispositivo está ligado e acessível
- Verifique firewall (porta 161 UDP)
- Teste com `snmpwalk` ou `snmpget` no terminal

### Problema: "No Such Instance"
**Solução**:
- O OID não existe neste dispositivo
- Verifique o manual do fabricante para OIDs corretos
- Use `snmpwalk` para descobrir OIDs disponíveis:
  ```bash
  snmpwalk -v2c -c public 192.168.1.100
  ```

### Problema: "Authentication failure"
**Solução**:
- Community string incorreta
- Verifique a configuração SNMP no dispositivo
- Tente com community padrão: `public` ou `private`

### Problema: "Temperatura sempre 22°C"
**Solução**:
- O AC não suporta os OIDs padrão
- Consulte o manual do fabricante
- Use OID customizado se disponível

## Próximos Passos

### Melhorias Futuras:
1. **SNMP v3** - Suporte completo com autenticação e criptografia
2. **Auto-discovery** - Descoberta automática de dispositivos SNMP na rede
3. **Gráficos** - Visualização de histórico de temperatura e uptime
4. **Alertas Avançados** - Notificações por email/SMS quando temperatura crítica
5. **Dashboard NOC** - Visualização de todos os ativos de rede em tempo real
6. **Relatórios** - Relatórios de disponibilidade e temperatura

### Dispositivos Adicionais:
- Câmeras IP
- Sensores de umidade
- Sensores de porta (abertura de rack)
- PDUs (Power Distribution Units)
- Geradores

## Comandos Úteis

### Descobrir OIDs disponíveis:
```bash
snmpwalk -v2c -c public 192.168.1.100
```

### Testar OID específico:
```bash
snmpget -v2c -c public 192.168.1.100 1.3.6.1.2.1.1.1.0
```

### Verificar temperatura do AC:
```bash
snmpget -v2c -c public 192.168.1.200 1.3.6.1.4.1.318.1.1.13.3.2.2.2.3.0
```

## Status: ✅ COMPLETO

Os sensores para monitoramento de ativos de rede (Access Points, Ar-Condicionado e Nobreak) foram implementados com sucesso e estão disponíveis na biblioteca de sensores SNMP.

Frontend reiniciado: `docker restart coruja-frontend`
