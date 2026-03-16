# Situação SNMP - 10 de Março de 2026

## Problema Atual

Probe coleta 0 métricas SNMP do servidor Linux, mesmo com SNMP funcionando.

## Progresso Realizado

### ✓ Problemas Resolvidos

1. **Erro UnicodeEncodeError** - RESOLVIDO
   - Causa: Emojis Unicode no `config.py` incompatíveis com Windows cp1252
   - Solução: Removidos emojis do arquivo
   - Comando: `(Get-Content config.py) -replace '🔍', '' ... | Set-Content config.py`
   - Status: Probe inicia normalmente

2. **SNMP Configurado no Linux** - CONFIRMADO
   - Pacotes instalados: snmpd, snmp, snmp-mibs-downloader
   - Arquivo `/etc/snmp/snmpd.conf` configurado
   - Community: public, Porta: 161
   - Serviço rodando e respondendo
   - Firewall liberado para rede 192.168.31.0/24

3. **pysnmp Versão Correta** - CONFIRMADO
   - pysnmp 4.4.12 instalado
   - pyasn1 0.4.8 instalado
   - Teste manual `TESTAR_SNMP_DETALHADO.py` funciona (8 OIDs coletados)

### ✗ Problema Atual

**Probe coleta 0 métricas SNMP**

```
INFO:__main__:Collecting SNMP metrics from 192.168.31.161 (vv2c)
INFO:__main__:Collected 0 SNMP metrics from 192.168.31.161
```

## Diagnóstico

### Hipóteses

1. **OIDs não batem** - Servidor retorna OIDs diferentes dos esperados
2. **Erro de conversão** - Valores não podem ser convertidos para float
3. **Problema no server_id** - Métrica não tem server_id correto
4. **Formato inesperado** - Dados em formato diferente do esperado

### Arquivos Envolvidos

- `probe/probe_core.py` - Método `_parse_snmp_metrics()` (linhas 370-470)
- `probe/collectors/snmp_collector.py` - Coleta SNMP v2c
- `probe/config.py` - Configuração (emojis removidos)

### Logs de Debug

Adicionados mas não aparecem no output:
```python
logger.debug(f"SNMP result status: {result.get('status')}")
logger.debug(f"SNMP data keys: {list(result.get('data', {}).keys())[:5]}")
logger.debug(f"Parsed {len(metrics)} metrics from SNMP data")
logger.debug(f"Parsing SNMP data: {len(data)} OIDs received")
```

## Próximos Passos

### 1. Executar Script de Diagnóstico

**Arquivo:** `DIAGNOSTICAR_SNMP_PARSING.py`

**Objetivo:** Identificar exatamente por que parsing retorna 0 métricas

**O que faz:**
- Coleta dados SNMP do servidor Linux
- Verifica quais OIDs foram recebidos
- Compara com OIDs esperados
- Tenta parsear cada métrica
- Mostra erros de conversão

**Como executar:**
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
python DIAGNOSTICAR_SNMP_PARSING.py
```

### 2. Analisar Resultado

**Cenário A:** Script gera 3-4 métricas
- Parsing funciona isoladamente
- Problema está no `probe_core.py` (integração)
- Verificar: server_id, formato de retorno, buffer

**Cenário B:** Script gera 0 métricas, OIDs não encontrados
- Servidor Linux não retorna OIDs esperados
- Ajustar `snmpd.conf` no Linux
- Adicionar MIBs necessárias

**Cenário C:** Script gera 0 métricas, erro de conversão
- Valores em formato inesperado (bytes, string, etc)
- Ajustar código de parsing
- Converter tipos corretamente

### 3. Aplicar Correção

Dependendo do resultado do diagnóstico:
- Ajustar OIDs esperados
- Corrigir conversão de tipos
- Configurar SNMP no Linux
- Ajustar integração no probe_core.py

## Arquitetura

```
SRVSONDA001 (Windows)          SRVCMONITOR001 (Linux)
├─ Probe Python                ├─ API (porta 8000)
├─ Coleta métricas locais      ├─ Frontend (porta 3000)
└─ Coleta SNMP remoto ────────>├─ PostgreSQL (Docker)
   (192.168.31.161:161)        └─ SNMP (porta 161)
```

## Configuração Atual

### SRVSONDA001
- IP: 192.168.31.x (dinâmico)
- Probe: `C:\Program Files\CorujaMonitor\Probe`
- Token: V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY
- Empresa: Techbiz, Probe: Datacenter

### SRVCMONITOR001
- IP: 192.168.31.161
- Hostname: srvcmonitor001
- SNMP Community: public
- SNMP Port: 161
- SNMP Version: 2c

## Referências

- `EXECUTAR_AGORA_SNMP.txt` - Instruções atuais
- `DIAGNOSTICAR_SNMP_PARSING.py` - Script de diagnóstico
- `EXECUTAR_DIAGNOSTICO_PARSING.txt` - Guia detalhado
- `CORRIGIR_EMOJIS_CONFIG_AGORA.txt` - Problema anterior resolvido
- `TESTAR_SNMP_DETALHADO.py` - Teste manual que funciona
