# Correção de Sensores Duplicados e Implementação NOC Mode + SNMP

## ✅ PROBLEMA CORRIGIDO: Sensores Duplicados

### Diagnóstico
- **Problema**: Dashboard mostrava 49 sensores quando deveria mostrar 28
- **Causa**: 21 sensores Docker estavam duplicados com `sensor_type='unknown'`
- **Sensores corretos**: 7 sistema + 21 docker = 28 total

### Solução Aplicada

1. **Script de Diagnóstico**: `api/check_and_fix_duplicates.py`
   - Verifica sensores duplicados por servidor, tipo e nome
   - Mostra contagem por tipo de sensor
   - Modo dry-run para verificação segura

2. **Script de Correção**: `api/fix_unknown_sensors_auto.py`
   - Remove automaticamente sensores com tipo 'unknown'
   - Remove métricas associadas (1.947 métricas removidas)
   - Mantém apenas os sensores corretos

### Resultado
```
✅ Sensores removidos: 21
✅ Métricas removidas: 1.947
✅ Total de sensores restantes: 28

Contagem por tipo:
  - system: 1
  - cpu: 1
  - memory: 1
  - disk: 1
  - ping: 1
  - network: 2
  - docker: 21
```

---

## 🚀 IMPLEMENTAÇÃO: Modo NOC (Network Operations Center)

### Funcionalidades Implementadas

#### 1. Backend NOC (`api/routers/noc.py`)
Endpoints criados:
- `GET /api/v1/noc/global-status` - Status global multi-empresa
- `GET /api/v1/noc/heatmap` - Mapa de calor de disponibilidade
- `GET /api/v1/noc/active-incidents` - Ticker de incidentes ativos
- `GET /api/v1/noc/kpis` - KPIs consolidados (MTTR, MTBF, SLA)

#### 2. Frontend NOC (`frontend/src/components/NOCMode.js`)
Características:
- **Tela Full Screen** - Modo dedicado para NOC
- **4 Dashboards Rotativos**:
  1. Status Global - Visão multi-empresa
  2. Heatmap - Mapa de calor de disponibilidade
  3. Incidentes Ativos - Ticker em tempo real
  4. KPIs - Indicadores consolidados
- **Atualização Automática** - A cada 5 segundos
- **Rotação Automática** - A cada 15 segundos (pode pausar)
- **Design Profissional** - Inspirado em centros de operação corporativos

#### 3. Integração no Sistema
- Botão "Modo NOC" adicionado ao Dashboard
- Atalho visual com gradiente roxo
- Transição suave entre modo normal e NOC
- Botão de saída para retornar ao dashboard

### Como Usar
1. Acesse o Dashboard principal
2. Clique no botão "📺 Modo NOC" no canto superior direito
3. O sistema entra em modo full screen com rotação automática
4. Use os indicadores na parte inferior para navegar manualmente
5. Clique em "❌ Sair" para retornar ao dashboard normal

---

## 📡 IMPLEMENTAÇÃO: SNMP Avançado

### Coletor SNMP (`probe/collectors/snmp_collector.py`)

#### Suporte a Múltiplas Versões
- **SNMP v1** - Compatibilidade legada
- **SNMP v2c** - Versão mais comum (community string)
- **SNMP v3** - Com autenticação e criptografia (SHA/MD5 + AES/DES)

#### Funcionalidades

1. **Coleta Básica**
   - `collect_snmp_v2c()` - Coleta via v2c
   - `collect_snmp_v3()` - Coleta via v3 com segurança
   - Suporte a OIDs customizados

2. **Monitoramento de Impressoras**
   - `collect_printer_metrics()` - Métricas específicas
   - Níveis de toner por cor
   - Contador de páginas
   - Status do dispositivo
   - Erros de hardware

3. **Descoberta Automática**
   - `discover_device()` - Identifica tipo de dispositivo
   - Detecta: impressoras, switches, roteadores
   - Extrai informações: nome, descrição, uptime, vendor

4. **Bulk Operations**
   - `bulk_walk()` - SNMP Walk otimizado
   - Coleta múltiplos valores de uma vez
   - Suporte a GetBulk para performance

5. **OIDs Customizados**
   - `add_custom_oid()` - Adiciona OIDs manualmente
   - `load_custom_oids_from_file()` - Carrega de arquivo YAML
   - Biblioteca extensível de MIBs

#### OIDs Suportados

**Padrão (MIB-II - RFC 1213)**:
- sysDescr, sysUpTime, sysName
- ifNumber, ifDescr, ifSpeed
- ifInOctets, ifOutOctets

**Impressoras (Printer MIB - RFC 3805)**:
- prtMarkerSuppliesLevel (nível de toner)
- prtMarkerSuppliesMaxCapacity (capacidade)
- prtMarkerLifeCount (contador de páginas)
- prtConsoleDisplayBufferText (status display)
- prtGeneralSerialNumber (serial)

**Rede (Bridge/IP MIB)**:
- dot1dTpFdbAddress (MAC addresses)
- ipRouteNextHop (rotas)

### Templates de Sensores SNMP

Adicionados à biblioteca (`frontend/src/data/sensorTemplates.js`):

1. **Dispositivo SNMP** - Genérico para qualquer dispositivo
2. **Impressora SNMP** - Monitoramento completo de impressoras
3. **Switch SNMP** - Switches de rede
4. **Roteador SNMP** - Roteadores
5. **Nobreak (UPS) SNMP** - Monitoramento de UPS
6. **OID Customizado** - Para OIDs específicos

### Dependências Instaladas
```
pysnmp==4.4.12
pyyaml==6.0.1
```

---

## 📋 PRÓXIMOS PASSOS

### Para Testar o Modo NOC
1. Acesse http://localhost:3000
2. Faça login (admin@coruja.com / admin123)
3. Clique no botão "Modo NOC" no Dashboard
4. Observe a rotação automática dos dashboards

### Para Adicionar Dispositivos SNMP
1. Vá em "Servidores" → Selecione um servidor
2. Clique em "Adicionar Sensor"
3. Selecione a categoria "SNMP"
4. Escolha o tipo de dispositivo:
   - Dispositivo SNMP (genérico)
   - Impressora SNMP
   - Switch SNMP
   - Roteador SNMP
   - Nobreak (UPS)
   - OID Customizado

### Configuração SNMP v2c
```json
{
  "host": "192.168.1.100",
  "community": "public",
  "port": 161,
  "version": "v2c"
}
```

### Configuração SNMP v3
```json
{
  "host": "192.168.1.100",
  "username": "snmpuser",
  "auth_key": "authpassword",
  "priv_key": "privpassword",
  "auth_protocol": "SHA",
  "priv_protocol": "AES",
  "port": 161,
  "version": "v3"
}
```

---

## 🔧 COMANDOS ÚTEIS

### Verificar Sensores
```bash
docker exec coruja-api python check_and_fix_duplicates.py
```

### Remover Duplicados (se necessário)
```bash
docker exec coruja-api python fix_unknown_sensors_auto.py
```

### Reiniciar Serviços
```bash
docker-compose restart frontend
docker-compose restart api
```

### Verificar Logs
```bash
docker logs coruja-frontend -f
docker logs coruja-api -f
```

---

## ✅ STATUS FINAL

### Correções Aplicadas
- ✅ Removidos 21 sensores duplicados
- ✅ Removidas 1.947 métricas órfãs
- ✅ Dashboard agora mostra contagem correta (28 sensores)

### Implementações Concluídas
- ✅ Modo NOC com 4 dashboards rotativos
- ✅ Backend NOC com 4 endpoints
- ✅ Coletor SNMP v1/v2c/v3
- ✅ Monitoramento de impressoras via SNMP
- ✅ Descoberta automática de dispositivos
- ✅ 6 templates de sensores SNMP
- ✅ Suporte a OIDs customizados
- ✅ Bulk operations (SNMP Walk)

### Sistema Pronto Para
- ✅ Monitoramento de impressoras
- ✅ Monitoramento de switches/roteadores
- ✅ Monitoramento de nobreaks (UPS)
- ✅ Visualização em modo NOC
- ✅ Operação 24/7 em centros de operação

---

## 📊 MÉTRICAS DO SISTEMA

**Antes da Correção**:
- Total de sensores: 49 (incorreto)
- Sensores duplicados: 21
- Métricas órfãs: 1.947

**Depois da Correção**:
- Total de sensores: 28 (correto)
- Sensores duplicados: 0
- Distribuição:
  - Sistema: 7 sensores
  - Docker: 21 sensores

**Capacidades Adicionadas**:
- Endpoints NOC: 4
- Templates SNMP: 6
- Versões SNMP: 3 (v1, v2c, v3)
- Dashboards NOC: 4
- Atualização: 5 segundos
- Rotação: 15 segundos

---

Data: 19/02/2026
Status: ✅ Implementado e Testado
