# Correção: Discrepância na Contagem de Incidentes

## Problema Identificado

Havia uma inconsistência entre o dashboard e a página de incidentes:
- **Dashboard**: Mostrava 4 incidentes abertos
- **Página de Incidentes**: Mostrava apenas 2 incidentes abertos

## Causa Raiz

A discrepância ocorria porque:

1. **Dashboard** (`api/routers/dashboard.py`): Contava apenas incidentes com `status == "open"`
2. **Página de Incidentes** (`frontend/src/components/Incidents.js`): Também contava apenas `status === 'open'`

Porém, o sistema possui incidentes com status `"acknowledged"` que são considerados ativos em outras partes do código (como `worker/tasks.py`, `api/routers/noc.py`, etc.), mas não estavam sendo incluídos na contagem de "incidentes abertos".

## Solução Implementada

### 1. Backend - Dashboard API (`api/routers/dashboard.py`)

Alterado para incluir incidentes "acknowledged" na contagem:

```python
# Antes
open_incidents = db.query(func.count(Incident.id)).filter(
    Incident.status == "open"
).scalar()

# Depois  
open_incidents = db.query(func.count(Incident.id)).filter(
    Incident.status.in_(["open", "acknowledged"])
).scalar()
```

### 2. Frontend - Página de Incidentes (`frontend/src/components/Incidents.js`)

Alterado para incluir incidentes "acknowledged" no card "Abertos":

```javascript
// Antes
if (inc.status === 'open') counts.open++;

// Depois
if (inc.status === 'open' || inc.status === 'acknowledged') counts.open++;
```

## Arquivos Modificados

1. `api/routers/dashboard.py` - Linhas 30-32, 66-68, 35-38, 73-76
2. `frontend/src/components/Incidents.js` - Linha 142

## Justificativa

Esta correção alinha a contagem com o comportamento do resto do sistema, onde incidentes "acknowledged" são tratados como ativos. Um incidente "acknowledged" significa que foi reconhecido por um operador, mas ainda não foi resolvido, portanto deve ser contado como "aberto".

## Resultado Esperado

Após a correção, tanto o dashboard quanto a página de incidentes devem mostrar o mesmo número de incidentes abertos, incluindo aqueles com status "open" e "acknowledged".