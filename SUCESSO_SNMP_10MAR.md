# Monitoramento SNMP Linux - Implementado com Sucesso

**Data:** 10 de Março de 2026  
**Status:** ✓ FUNCIONANDO

## Resumo da Implementação

Sistema de monitoramento SNMP para servidores Linux implementado com sucesso, seguindo arquitetura PRTG (1 sonda Windows, N servidores monitorados).

## Arquitetura Final

```
SRVSONDA001 (Windows)          SRVCMONITOR001 (Linux)
├─ Probe Python                ├─ API (porta 8000)
├─ Coleta métricas locais      ├─ Frontend (porta 3000)
└─ Coleta SNMP remoto ────────>├─ PostgreSQL (Docker)
   (192.168.31.161:161)        └─ SNMP (porta 161)
```

## Problemas Resolvidos

### 1. Erro UnicodeEncodeError
- **Causa:** Emojis Unicode no `config.py` incompatíveis com Windows cp1252
- **Solução:** Removidos emojis do arquivo
- **Arquivo:** `probe/config.py`

### 2. SNMP Não Retornava Métricas
- **Causa:** `snmpd.conf` no Linux não habilitava MIBs do NET-SNMP
- **Solução:** Reconfigurado `snmpd.conf` com OIDs completos
- **Arquivo:** `/etc/snmp/snmpd.conf` no SRVCMONITOR001

### 3. Probe Coletava Apenas OIDs Básicos
- **Causa:** `snmp_collector.py` só pedia 8 OIDs padrão
- **Solução:** Adicionados 16 OIDs do NET-SNMP (CPU, Memória, Disco, Load)
- **Arquivo:** `probe/collectors/snmp_collector.py`

### 4. Logs de Debug Não Apareciam
- **Causa:** Logs configurados como DEBUG não aparecem no output
- **Solução:** Mudados logs críticos para INFO
- **Arquivo:** `probe/probe_core.py`

## Métricas Coletadas

O sistema agora coleta 25 OIDs via SNMP e parseia 3 métricas principais:

1. **CPU** - Percentual de uso (calculado: 100 - idle)
2. **Memória** - Percentual de uso (calculado: (total - disponível) / total * 100)
3. **Disco** - Percentual de uso (primeiro disco montado)

### OIDs Coletados

**Básicos (MIB-II):**
- 1.3.6.1.2.1.1.1.0 - Descrição do Sistema
- 1.3.6.1.2.1.1.3.0 - Uptime
- 1.3.6.1.2.1.1.5.0 - Hostname
- 1.3.6.1.2.1.2.x.x - Interfaces de rede

**NET-SNMP (UCD-SNMP-MIB):**
- 1.3.6.1.4.1.2021.4.5.0 - Memória Total (KB)
- 1.3.6.1.4.1.2021.4.6.0 - Memória Disponível (KB)
- 1.3.6.1.4.1.2021.11.11.0 - CPU Idle (%)
- 1.3.6.1.4.1.2021.9.1.9.1 - Disco Percentual (%)
- 1.3.6.1.4.1.2021.10.1.3.1 - Load Average 1min

## Arquivos Modificados

### Desenvolvimento (DESKTOP-P9VGN04)
1. `probe/config.py` - Removidos emojis Unicode
2. `probe/collectors/snmp_collector.py` - Adicionados 16 OIDs do NET-SNMP
3. `probe/probe_core.py` - Logs mudados para INFO, parsing detalhado

### Produção (SRVSONDA001)
1. `C:\Program Files\CorujaMonitor\Probe\config.py`
2. `C:\Program Files\CorujaMonitor\Probe\collectors\snmp_collector.py`
3. `C:\Program Files\CorujaMonitor\Probe\probe_core.py`

### Servidor Linux (SRVCMONITOR001)
1. `/etc/snmp/snmpd.conf` - Configuração completa com MIBs habilitadas

## Teste de Funcionamento

### Script de Diagnóstico
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
python DIAGNOSTICAR_SNMP_PARSING.py
```

**Resultado Esperado:**
```
Total de OIDs coletados: 25
✓ ENCONTRADO | CPU Idle
✓ ENCONTRADO | Memória Total
✓ ENCONTRADO | Memória Disponível
✓ ENCONTRADO | Disco Percentual
RESULTADO FINAL: 3 métricas parseadas
```

### Probe em Produção
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
python probe_core.py
```

**Logs Esperados:**
```
INFO:__main__:Collecting SNMP metrics from 192.168.31.161 (vv2c)
INFO:__main__:SNMP result status: success
INFO:__main__:SNMP data keys: ['1.3.6.1.2.1.1.1.0', ...]
INFO:__main__:Parsing SNMP data: 25 OIDs received
INFO:__main__:Found mem_total: 7004932.0 KB
INFO:__main__:Found mem_avail: 246812.0 KB
INFO:__main__:Parsed Memory: 96.48%
INFO:__main__:Parsed CPU: 1.00% (idle: 99.0%)
INFO:__main__:Parsed Disk: 56.00%
INFO:__main__:Total metrics parsed: 3
INFO:__main__:Collected 3 SNMP metrics from 192.168.31.161
```

## Dashboard

**URL:** http://192.168.31.161:3000  
**Login:** admin@coruja.com / admin123

**Servidores > SRVCMONITOR001:**
- ✓ PING - Latência em ms
- ✓ CPU - 1% uso
- ✓ Memória - 96% uso
- ✓ Disco - 56% uso

## Próximos Passos

1. **Instalar Probe como Serviço Windows**
   - Usar `INSTALAR_SERVICO_PROBE_SIMPLES.bat`
   - Configurar início automático

2. **Adicionar Mais Servidores Linux**
   - Configurar SNMP no servidor
   - Adicionar no dashboard
   - Probe coleta automaticamente

3. **Expandir Métricas**
   - Load Average (já coletado, falta parsear)
   - Uptime (já coletado, falta parsear)
   - Interfaces de rede (já coletado, falta parsear)

4. **Enviar para Git**
   - Commit das correções
   - Push para repositório
   - Atualizar servidor Linux

## Ferramentas de Diagnóstico

1. **DIAGNOSTICAR_SNMP_PARSING.py** - Testa coleta e parsing isoladamente
2. **TESTAR_SNMP_DETALHADO.py** - Testa SNMP direto no Linux
3. **probe_core.py** - Logs INFO detalhados de cada etapa

## Configuração SNMP Linux

Arquivo `/etc/snmp/snmpd.conf` configurado com:
- Community: public (read-only)
- Porta: 161
- MIBs habilitadas: CPU, Memória, Disco, Load, Processos
- Firewall liberado para rede 192.168.31.0/24

## Lições Aprendidas

1. **Emojis Unicode** - Evitar em código Python para Windows
2. **Logs de Debug** - Usar INFO para logs críticos
3. **SNMP MIBs** - Precisam ser explicitamente habilitadas no snmpd.conf
4. **OIDs Padrão** - MIB-II (1.3.6.1.2.1.x) vs NET-SNMP (1.3.6.1.4.1.2021.x)
5. **Diagnóstico Isolado** - Scripts de teste são essenciais para debug

## Referências

- RFC 1213 - MIB-II (OIDs básicos)
- NET-SNMP Documentation - UCD-SNMP-MIB
- pysnmp 4.4.12 - API antiga compatível
- PRTG Architecture - 1 sonda, N dispositivos
