# Correção de Timezone nas Métricas - 26/02/2026

## Problema Identificado

Os sensores estavam sendo atualizados pela probe, mas as métricas apareciam com timestamps muito antigos (3 horas de diferença), causando:
- Métricas mostrando "Atualizado há 3 horas" quando na verdade foram atualizadas há poucos segundos
- Incidentes não sendo fechados automaticamente mesmo com sensores OK
- Confusão entre horário de Brasília e UTC

## Causa Raiz

A probe estava enviando timestamps **naive** (sem timezone):
```
2026-02-26T13:09:15.537316  (sem timezone)
```

A API salvava diretamente no PostgreSQL, que interpretava como UTC, mas na verdade era horário de Brasília (UTC-3).

Quando o sistema comparava com `datetime.now(timezone.utc)`, calculava 3 horas de diferença incorretamente.

## Solução Implementada

### 1. Correção na API (`api/routers/metrics.py`)

Adicionada lógica para interpretar timestamps naive como horário de Brasília e converter para UTC antes de salvar:

```python
# Fix timezone: if timestamp is naive, assume it's in Brazil timezone (America/Sao_Paulo)
from datetime import timezone as tz
import pytz

timestamp = metric_data.timestamp
if timestamp.tzinfo is None:
    # Timestamp is naive, assume it's in Brazil timezone
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    timestamp = brazil_tz.localize(timestamp)
    # Convert to UTC for storage
    timestamp = timestamp.astimezone(pytz.UTC)
```

### 2. Dependência Adicionada

Adicionado `pytz==2024.1` ao `api/requirements.txt` para manipulação correta de timezones.

### 3. Containers Reiniciados

- API reiniciada com pytz instalado
- Timezone `TZ=America/Sao_Paulo` já estava configurado no `docker-compose.yml`

## Validação

### Antes da Correção
```
Timestamp: 2026-02-26 13:09:15.537316+00:00
Idade: 10829 segundos (3 horas)
```

### Depois da Correção
```
Timestamp: 2026-02-26 16:12:16.558365+00:00
Idade: 65 segundos
```

## Resultado

✅ Métricas agora mostram timestamps corretos (UTC)
✅ Idade das métricas calculada corretamente (segundos, não horas)
✅ Sistema interpreta corretamente horário de Brasília → UTC
✅ Incidentes podem ser fechados automaticamente quando sensores voltam ao normal
✅ Frontend mostra "Atualizado há X segundos" corretamente

## Arquivos Modificados

1. `api/routers/metrics.py` - Lógica de conversão de timezone
2. `api/requirements.txt` - Adicionado pytz==2024.1

## Próximos Passos

O sistema agora está funcionando corretamente:
- Probe coleta métricas a cada 60 segundos
- API converte timestamps de Brasília para UTC
- Worker avalia thresholds e fecha incidentes automaticamente
- Frontend mostra timestamps corretos

## Observações Técnicas

- PostgreSQL armazena timestamps em UTC (padrão)
- Probe envia timestamps em horário local (Brasília)
- API faz a conversão automática
- Frontend pode exibir em qualquer timezone desejado

---

**Data da Correção**: 26/02/2026 13:13
**Status**: ✅ Implementado e Validado
