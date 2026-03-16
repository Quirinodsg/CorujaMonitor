# DIAGNÓSTICO FINAL - SNMP 10 MAR 2026 11:00

## PROBLEMA IDENTIFICADO

### Sintomas
- ✅ Script `TESTAR_SNMP_DETALHADO.py` funciona: 25 OIDs, 5 métricas
- ✅ Script `TESTAR_SNMP_MANUALMENTE.py` funciona: 25 OIDs coletados
- ✅ Script `DIAGNOSTICAR_SNMP_PARSING.py` funciona: 3 métricas parseadas
- ❌ Probe em produção coleta 0 métricas

### Logs da Probe
```
INFO:__main__:Collecting SNMP metrics from 192.168.31.161 (vv2c)
INFO:__main__:Collected 0 SNMP metrics from 192.168.31.161
```

### Logs Esperados (FALTANDO)
```
INFO:__main__:About to call collect_snmp_v2c with host=...
INFO:__main__:Collector object: ...
INFO:__main__:Collector type: ...
INFO:__main__:collect_snmp_v2c returned successfully
INFO:__main__:Result type: ...
INFO:__main__:Result: ...
INFO:__main__:SNMP result status: ...
INFO:__main__:SNMP data keys: ...
```

## CAUSA RAIZ

**Arquivo `probe_core.py` na SRVSONDA001 está com versão ANTIGA**

Quando o usuário copiou "a pasta inteira da probe", pode ter:
1. Sobrescrito com versão antiga de backup
2. Copiado de local errado
3. Não incluído as últimas mudanças

## EVIDÊNCIAS

1. **Scripts de teste funcionam** → SNMP está OK, pysnmp está OK
2. **Logs detalhados não aparecem** → Código antigo sem os logs
3. **Última modificação do arquivo** → Precisa verificar timestamp

## SOLUÇÃO

### Passo 1: Verificar Versão
Execute na SRVSONDA001:
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
python VERIFICAR_VERSAO_PROBE_CORE.py
```

### Passo 2: Copiar Versão Correta
Do notebook (DESKTOP-P9VGN04):
```
C:\Users\andre.quirino\Coruja Monitor\probe\probe_core.py
```

Para SRVSONDA001:
```
C:\Program Files\CorujaMonitor\Probe\probe_core.py
```

### Passo 3: Testar Novamente
```powershell
cd "C:\Program Files\CorujaMonitor\Probe"
python probe_core.py
```

## MUDANÇAS NO CÓDIGO

### Versão Antiga (SEM logs detalhados)
```python
if version == '2c':
    try:
        result = collector.collect_snmp_v2c(...)
        logger.info(f"SNMP result status: {result.get('status')}")
        # ...
    except Exception as e:
        logger.error(f"Error in SNMP v2c collection: {e}", exc_info=True)
        metrics = []
```

### Versão Nova (COM logs detalhados)
```python
if version == '2c':
    logger.info(f"About to call collect_snmp_v2c with host={hostname}, community={community}, port={port}")
    logger.info(f"Collector object: {collector}")
    logger.info(f"Collector type: {type(collector)}")
    
    result = collector.collect_snmp_v2c(...)
    
    logger.info(f"collect_snmp_v2c returned successfully")
    logger.info(f"Result type: {type(result)}")
    logger.info(f"Result: {result}")
    logger.info(f"SNMP result status: {result.get('status')}")
    # ...
```

## PRÓXIMOS PASSOS

1. ✅ Verificar versão instalada
2. ✅ Copiar arquivo correto
3. ✅ Testar e coletar logs completos
4. ⏳ Analisar logs para identificar onde está falhando
5. ⏳ Corrigir problema específico

## CENÁRIOS POSSÍVEIS (após copiar versão correta)

### Cenário A: Logs param em "About to call"
→ `collect_snmp_v2c()` está lançando exceção
→ Except externo capturando silenciosamente

### Cenário B: Logs mostram "returned successfully" mas Result é None
→ Método retornando None ao invés de dict
→ Problema no `snmp_collector.py`

### Cenário C: Result com status='error'
→ SNMP falhando mas erro não mostrado
→ Verificar campo 'error' no resultado

### Cenário D: Result com status='success' mas data vazio
→ OIDs não sendo coletados
→ Problema de conectividade SNMP

## ARQUIVOS CRIADOS

1. `VERIFICAR_VERSAO_PROBE_CORE.py` - Verifica qual versão está instalada
2. `COPIAR_PROBE_CORE_ATUALIZADO.txt` - Instruções detalhadas de cópia
3. `DIAGNOSTICO_FINAL_SNMP_10MAR.md` - Este arquivo (resumo completo)

## HISTÓRICO

- **09 MAR**: Implementados 16 OIDs do NET-SNMP, método `_parse_snmp_metrics()`
- **10 MAR 10:30**: Adicionados logs detalhados para debug
- **10 MAR 11:00**: Identificado que arquivo não foi atualizado na SRVSONDA001
