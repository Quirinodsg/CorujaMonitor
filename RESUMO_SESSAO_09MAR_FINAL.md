# RESUMO DA SESSÃO - 09 MARÇO 2026

## ✅ TAREFAS CONCLUÍDAS

### 1. Filtro CD-ROM Implementado e Funcionando
- **Arquivo**: `probe/collectors/disk_collector.py`
- **Correção**: Adicionados filtros para ignorar CD-ROM, DVD e unidades vazias
- **Status**: ✅ FUNCIONANDO (última atualização Disco D: 09:53:22, outros sensores: 15:41:50)
- **Commit**: Enviado para Git

### 2. Exclusão de Sensor Disco D
- **Problema**: Sensor Disco D ainda aparecia no dashboard
- **Causa**: Foreign key constraint em `remediation_logs`
- **Solução**: Deletar `remediation_logs` primeiro, depois sensor
- **Status**: ✅ RESOLVIDO
- **Comandos executados**:
  ```sql
  DELETE FROM remediation_logs WHERE incident_id IN (SELECT id FROM incidents WHERE sensor_id = 19);
  DELETE FROM metrics WHERE sensor_id = 19;
  DELETE FROM incidents WHERE sensor_id = 19;
  DELETE FROM sensor_notes WHERE sensor_id = 19;
  DELETE FROM sensors WHERE id = 19;
  ```

### 3. SNMP Configurado no Servidor Linux
- **Servidor**: SRVCMONITOR001 (192.168.31.161)
- **Pacotes instalados**: snmpd, snmp, snmp-mibs-downloader
- **Configuração**: `/etc/snmp/snmpd.conf`
- **Community**: public
- **Porta**: 161
- **Teste**: ✅ FUNCIONANDO
  ```
  SNMPv2-MIB::sysDescr.0 = STRING: Linux srvcmonitor001 5.15.0-171-generic
  ```

### 4. Servidor Linux Adicionado no Dashboard
- **Nome**: SRVCMONITOR001
- **IP**: 192.168.31.161
- **Protocolo**: SNMP v2c
- **Status**: Adicionado com sucesso

## ❌ PROBLEMA ATUAL

### SNMP Collector Não Coleta Métricas

**Sintoma**:
```
INFO:__main__:Collecting SNMP metrics from 192.168.31.161 (vv2c)
INFO:__main__:Collected 0 SNMP metrics from 192.168.31.161
```

**Causa Provável**:
1. Biblioteca pysnmp pode não estar instalada corretamente
2. `SNMPCollector.collect_snmp_v2c()` pode estar retornando dados vazios
3. Firewall pode estar bloqueando porta 161

**Código Implementado**:
- Método `_parse_snmp_metrics()` adicionado em `probe_core.py`
- Converte dados SNMP brutos em métricas formatadas
- Extrai CPU, Memória, Disco, Uptime

## 🔍 PRÓXIMOS PASSOS

### 1. Testar SNMP Collector Manualmente

Execute na máquina SRVSONDA001:

```cmd
cd "C:\Program Files\CorujaMonitor\Probe"
python TESTAR_SNMP_MANUALMENTE.py
```

Arquivo criado: `TESTAR_SNMP_MANUALMENTE.py`

### 2. Verificar Biblioteca pysnmp

```cmd
cd "C:\Program Files\CorujaMonitor\Probe"
python -c "from pysnmp.hlapi import *; print('pysnmp OK')"
```

Se der erro, instalar:
```cmd
pip install pysnmp
```

### 3. Verificar Firewall Windows

```cmd
netsh advfirewall firewall show rule name=all | findstr 161
```

Se não houver regra, adicionar:
```cmd
netsh advfirewall firewall add rule name="SNMP Out" dir=out action=allow protocol=UDP localport=161
```

### 4. Testar SNMP da Máquina Windows para Linux

```cmd
snmpwalk -v2c -c public 192.168.31.161 system
```

Se não funcionar, instalar Net-SNMP para Windows

## 📊 ARQUITETURA ATUAL

```
┌─────────────────────────────────────────┐
│ DESKTOP-P9VGN04 (Notebook)              │
│ - Desenvolvimento                       │
│ - Git                                   │
│ - Kiro                                  │
└─────────────────────────────────────────┘
                │
                │ Git Push/Pull
                ▼
┌─────────────────────────────────────────┐
│ SRVSONDA001 (Windows)                   │
│ - Probe Python                          │
│ - Coleta local (CPU, RAM, Disco)       │
│ - Coleta remota via SNMP/WMI           │
│ - Token: V-PTetiHvb...                 │
└─────────────────────────────────────────┘
                │
                │ SNMP (porta 161)
                │ HTTP API (porta 8000)
                ▼
┌─────────────────────────────────────────┐
│ SRVCMONITOR001 (Linux 192.168.31.161)  │
│ - SNMP habilitado                       │
│ - API:8000 (Docker)                     │
│ - Frontend:3000 (Docker)                │
│ - PostgreSQL (Docker)                   │
└─────────────────────────────────────────┘
```

## 📁 ARQUIVOS CRIADOS NESTA SESSÃO

1. `DELETAR_DISCO_D_COM_REMEDIATION.txt` - Comandos para deletar sensor
2. `ADICIONAR_LINUX_VIA_SNMP_SIMPLES.txt` - Guia SNMP
3. `CORRIGIR_SNMP_MIBS.txt` - Instalar MIBs
4. `ADICIONAR_SERVIDOR_DASHBOARD_AGORA.txt` - Adicionar servidor
5. `TESTAR_SNMP_AGORA.txt` - Testar SNMP
6. `CORRIGIR_SNMP_COLLECTOR_AGORA.txt` - Corrigir collector
7. `ENVIAR_CORRECAO_SNMP_GIT.txt` - Enviar para Git
8. `TESTAR_SNMP_MANUALMENTE.py` - Script de teste
9. `RESUMO_SESSAO_09MAR_FINAL.md` - Este arquivo

## 🎯 OBJETIVO FINAL

Ter 2 servidores monitorados:
1. **SRVSONDA001** (Windows) - Monitorado localmente
2. **SRVCMONITOR001** (Linux) - Monitorado via SNMP

Com sensores:
- CPU
- Memória
- Discos
- Rede
- Uptime
- Ping

## 📝 NOTAS IMPORTANTES

- Filtro CD-ROM está funcionando perfeitamente
- SNMP no Linux está respondendo corretamente
- Problema está na coleta/conversão de dados SNMP na probe
- Código de conversão foi implementado mas precisa debug
- Pode ser necessário instalar pysnmp na máquina Windows

## 🔐 CREDENCIAIS

- Dashboard: admin@coruja.com / admin123
- SNMP Community: public
- Token Probe: V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY
- Banco: coruja_monitor
