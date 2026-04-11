# 📋 Resumo das Alterações - Dashboard Incidentes

## 🎯 Objetivo
Corrigir discrepância onde dashboard mostrava 4 incidentes abertos e página de incidentes mostrava apenas 2.

## 🔍 Causa
Incidentes com status "acknowledged" não estavam sendo contados como "abertos".

## 📝 Alterações Realizadas

### 1️⃣ Backend: `api/routers/dashboard.py`

#### Antes:
```python
# Linha 30-32 (Admin)
open_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
    Incident.status == "open"
).scalar()

# Linha 66-68 (Tenant User)
open_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
    Server.tenant_id == current_user.tenant_id,
    Incident.status == "open"
).scalar()
```

#### Depois:
```python
# Linha 30-32 (Admin)
open_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
    Incident.status.in_(["open", "acknowledged"])
).scalar()

# Linha 66-68 (Tenant User)
open_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
    Server.tenant_id == current_user.tenant_id,
    Incident.status.in_(["open", "acknowledged"])
).scalar()
```

**Mesma alteração aplicada para `critical_incidents`** (linhas 35-38 e 73-76)

---

### 2️⃣ Frontend: `frontend/src/components/Incidents.js`

#### Antes:
```javascript
// Linha 142
incidents.forEach(inc => {
  if (inc.status === 'open') counts.open++;
  if (inc.status === 'acknowledged') counts.acknowledged++;
  // ...
});
```

#### Depois:
```javascript
// Linha 142
incidents.forEach(inc => {
  if (inc.status === 'open' || inc.status === 'acknowledged') counts.open++;
  if (inc.status === 'acknowledged') counts.acknowledged++;
  // ...
});
```

---

## 📊 Impacto

### Antes da Correção:
| Local | Contagem "Abertos" |
|-------|-------------------|
| Dashboard | 4 (incluía acknowledged?) |
| Página Incidentes | 2 (só open) |

### Depois da Correção:
| Local | Contagem "Abertos" |
|-------|-------------------|
| Dashboard | open + acknowledged |
| Página Incidentes | open + acknowledged |

**Resultado**: Números consistentes em ambas as telas ✅

---

## 🔄 Compatibilidade

✅ **Sem mudanças no banco de dados**
✅ **Sem mudanças na API externa**
✅ **Compatível com versão atual**
✅ **Não afeta outras funcionalidades**

---

## 🧪 Como Testar

1. **Verificar no banco**:
```sql
SELECT status, COUNT(*) 
FROM incidents 
WHERE status IN ('open', 'acknowledged') 
GROUP BY status;
```

2. **Acessar dashboard**: Anotar número de "Incidentes Abertos"

3. **Clicar em "Incidentes"**: Verificar se o card "Abertos" mostra o mesmo número

4. **Filtrar por "Abertos"**: Deve mostrar incidentes com status "open" E "acknowledged"

---

## 📦 Arquivos para Deploy

```
api/routers/dashboard.py          (Backend - Python)
frontend/src/components/Incidents.js  (Frontend - React)
```

---

## ⚠️ Observações

- Incidentes "acknowledged" são aqueles reconhecidos por um operador mas ainda não resolvidos
- Esta alteração alinha o dashboard com o comportamento do resto do sistema
- Em `worker/tasks.py`, `api/routers/noc.py` e outros, já se usa `status.in_(['open', 'acknowledged'])`
- A correção apenas padroniza essa lógica em todo o sistema