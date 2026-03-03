# Requisitos para Monitoramento de Dispositivos
## Baseado em PRTG, SolarWinds, CheckMK e Zabbix

### 📡 SNMP Genérico (Switches, Roteadores, Firewalls)
**Requisitos:**
- SNMP habilitado no dispositivo (v1, v2c ou v3)
- Community String (padrão: "public" para leitura)
- Porta SNMP (padrão: 161/UDP)
- Acesso de rede entre probe e dispositivo

**OIDs Comuns:**
- sysDescr: 1.3.6.1.2.1.1.1.0
- sysUpTime: 1.3.6.1.2.1.1.3.0
- ifInOctets: 1.3.6.1.2.1.2.2.1.10
- ifOutOctets: 1.3.6.1.2.1.2.2.1.16

**Configuração no Dispositivo:**
```
# Cisco/HP
snmp-server community public RO
snmp-server enable traps

# Linux
apt-get install snmpd
echo "rocommunity public" >> /etc/snmp/snmpd.conf
```

---

### 📶 Access Point WiFi
**Requisitos:**
- SNMP habilitado (v2c recomendado)
- Community String configurado
- MIB específico do fabricante (opcional)

**OIDs Específicos:**
- Clientes conectados: 1.3.6.1.4.1.14988.1.1.1.3.1.6 (MikroTik)
- Sinal WiFi: 1.3.6.1.4.1.14988.1.1.1.1.1.4
- Tráfego: 1.3.6.1.2.1.2.2.1.10/16

**Fabricantes Suportados:**
- Ubiquiti UniFi
- MikroTik
- Cisco Aironet
- TP-Link EAP
- Aruba

---

### 🌡️ Temperatura (Sensores SNMP)
**Requisitos:**
- Sensor de temperatura com SNMP
- Community String
- OID específico do sensor

**OIDs Comuns:**
- Cisco: 1.3.6.1.4.1.9.9.13.1.3.1.3
- APC: 1.3.6.1.4.1.318.1.1.10.2.3.2.1.4
- Genérico: 1.3.6.1.2.1.99.1.1.1.4

**Dispositivos Suportados:**
- Sensores APC NetBotz
- Cisco Environmental Monitors
- Sensores genéricos SNMP
- Switches com sensores internos

---

### 🌐 HTTP/HTTPS (Websites, APIs)
**Requisitos:**
- URL acessível
- Método HTTP (GET, POST, HEAD)
- Timeout configurável
- Certificado SSL válido (HTTPS)

**Verificações:**
- Status Code (200, 301, 404, 500)
- Tempo de resposta
- Conteúdo da página (keywords)
- Validade do certificado SSL
- Redirecionamentos

**Autenticação Suportada:**
- Basic Auth
- Bearer Token
- API Key

---

### 💾 Storage/NAS (QNAP, Synology, NetApp)
**Requisitos:**
- SNMP habilitado
- Community String
- Acesso de rede

**OIDs Específicos:**
- QNAP: 1.3.6.1.4.1.24681
- Synology: 1.3.6.1.4.1.6574
- NetApp: 1.3.6.1.4.1.789

**Métricas:**
- Espaço em disco (usado/livre)
- RAID status
- Temperatura
- Ventiladores
- Volumes/LUNs

---

### 🗄️ Banco de Dados (MySQL, PostgreSQL, SQL Server)
**Requisitos:**
- Usuário com permissões de leitura
- Porta do banco acessível
- Credenciais de conexão

**Portas Padrão:**
- MySQL: 3306
- PostgreSQL: 5432
- SQL Server: 1433
- Oracle: 1521
- MongoDB: 27017

**Permissões Necessárias:**
```sql
-- MySQL
GRANT SELECT ON performance_schema.* TO 'monitor'@'%';
GRANT PROCESS ON *.* TO 'monitor'@'%';

-- PostgreSQL
GRANT pg_monitor TO monitor_user;

-- SQL Server
GRANT VIEW SERVER STATE TO monitor_user;
```

---

### 🖨️ Impressora (HP, Canon, Epson, Brother)
**Requisitos:**
- SNMP habilitado
- Community String (padrão: public)
- Porta 161/UDP

**OIDs Printer MIB (RFC 3805):**
- Status: 1.3.6.1.2.1.25.3.5.1.1
- Toner Preto: 1.3.6.1.2.1.43.11.1.1.9.1.1
- Toner Ciano: 1.3.6.1.2.1.43.11.1.1.9.1.2
- Toner Magenta: 1.3.6.1.2.1.43.11.1.1.9.1.3
- Toner Amarelo: 1.3.6.1.2.1.43.11.1.1.9.1.4
- Papel: 1.3.6.1.2.1.43.8.2.1.10.1.1
- Total de páginas: 1.3.6.1.2.1.43.10.2.1.4.1.1

**Configuração:**
```
# HP
Menu > Network > SNMP > Enable
Community Name: public

# Canon
Setup > Network > SNMP Settings > Enable
```

---

### 🔋 UPS/Nobreak (APC, SMS, Eaton)
**Requisitos:**
- SNMP habilitado (v1 ou v2c)
- Community String
- Network Management Card (para APC)

**OIDs UPS MIB (RFC 1628):**
- Status: 1.3.6.1.2.1.33.1.4.1.0
- Bateria %: 1.3.6.1.2.1.33.1.2.4.0
- Tempo restante: 1.3.6.1.2.1.33.1.2.3.0
- Temperatura: 1.3.6.1.2.1.33.1.2.7.0
- Carga %: 1.3.6.1.2.1.33.1.4.4.1.5.1
- Tensão entrada: 1.3.6.1.2.1.33.1.3.3.1.3.1
- Tensão saída: 1.3.6.1.2.1.33.1.4.4.1.2.1

**Status Values:**
- 1 = Unknown
- 2 = Online (normal)
- 3 = On Battery
- 4 = On Boost
- 5 = Sleeping
- 6 = On Bypass
- 7 = Off
- 8 = Rebooting

**Configuração APC:**
```
# Via Web Interface
Network > SNMP > Access Control
Community Name: public
Access Type: Read
```

---

## Melhores Práticas

### Segurança SNMP:
1. Use SNMPv3 quando possível (autenticação + criptografia)
2. Altere community strings padrão
3. Configure ACLs para limitar acesso
4. Use community strings diferentes para leitura/escrita
5. Desabilite SNMP write se não necessário

### Performance:
1. Use polling intervals adequados (5-10 minutos para métricas lentas)
2. Agrupe OIDs em uma única requisição quando possível
3. Configure timeouts apropriados (5-10 segundos)
4. Use SNMP bulk operations para múltiplos valores

### Troubleshooting:
```bash
# Testar SNMP
snmpwalk -v2c -c public 192.168.1.1

# Testar OID específico
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0

# Verificar portas
nmap -sU -p 161 192.168.1.1
```
