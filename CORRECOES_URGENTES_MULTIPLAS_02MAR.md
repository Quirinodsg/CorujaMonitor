# 🔧 Correções Urgentes Múltiplas - 02 de Março 2026

## 📋 PROBLEMAS IDENTIFICADOS

### 1. ❌ Card de Sensores Ruim
**Problema:** Layout do card de sensor está confuso/feio
**Localização:** `frontend/src/components/Management.css` - `.sensor-card`
**Solução:** Melhorar espaçamento, cores e hierarquia visual

### 2. ❌ Config > Teste de Sensores Sai da Aba
**Problema:** Ao clicar em "Testar Sensor" na aba Config, sai da aba
**Causa:** Navegação ou reload da página
**Solução:** Manter na mesma aba após teste

### 3. ❌ Notas Permanecem Após Sensor Resolver
**Problema:** Quando sensor volta a OK, a nota "Resolvido" ainda aparece no card
**Causa:** Notas não são filtradas por status do sensor
**Solução:** Ocultar notas quando `sensor.status === 'ok'`

### 4. ❌ Erro ao Excluir Probe
**Problema:** "Not Found" ao tentar excluir probe
**Causa:** Endpoint ou ID incorreto
**Solução:** Verificar rota da API

### 5. ❌ NOC: Servidores Somem Quando Tem Alerta
**Problema:** Quando há incidente, servidores desaparecem do NOC
**Causa:** Lógica de filtragem incorreta
**Solução:** Corrigir filtro de servidores

### 6. ❌ Métricas Grafana: Ajustar CARD
**Problema:** Layout do card de métricas precisa ajuste
**Solução:** Melhorar espaçamento e alinhamento

---

## 🔧 CORREÇÃO 1: Card de Sensores

### Problema Atual:
```
🖥️ CPU
50.1%
OK
Atualizado: 02/03/2026, 15:51:47
⚠️ 80% | 🔥 95%
📝 Resolvido
```

### Melhorias Necessárias:
1. Aumentar tamanho do valor (50.1%)
2. Melhorar contraste do status
3. Separar melhor as seções
4. Timestamp mais discreto

### CSS Melhorado:
```css
.sensor-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  min-height: 180px;
}

.sensor-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px 10px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(0,0,0,0.06);
}

.sensor-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.sensor-header h3 {
  margin: 0;
  font-size: 13px;
  color: #666;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.sensor-value {
  font-size: 42px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  padding: 16px 16px 12px 16px;
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  letter-spacing: -0.02em;
  line-height: 1;
}

.sensor-status-bar {
  padding: 10px 16px;
  text-align: center;
  color: white;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sensor-status-bar.ok {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.sensor-status-bar.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.sensor-status-bar.critical {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.sensor-timestamp {
  font-size: 10px;
  color: #999;
  text-align: center;
  padding: 6px 16px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  background: rgba(0,0,0,0.02);
}

.sensor-thresholds {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 8px 16px;
  font-size: 11px;
  color: #666;
  background: rgba(0,0,0,0.02);
  border-top: 1px solid rgba(0,0,0,0.06);
}
```

---

## 🔧 CORREÇÃO 2: Config > Teste de Sensores

### Problema:
Ao clicar em "Testar Sensor", a página recarrega ou navega

### Solução:
Adicionar `preventDefault()` no botão de teste

```javascript
// Em Settings.js ou onde está o botão de teste
const handleTestSensor = async (e) => {
  e.preventDefault(); // ADICIONAR ISSO
  e.stopPropagation(); // ADICIONAR ISSO
  
  try {
    // ... código de teste
  } catch (error) {
    console.error('Erro ao testar sensor:', error);
  }
};
```

---

## 🔧 CORREÇÃO 3: Notas Permanecem Após Resolver

### Problema:
Nota "Resolvido" aparece mesmo quando sensor está OK

### Solução:
Filtrar notas por status do sensor

```javascript
// Em Servers.js, ao renderizar o card
{sensor.last_note && sensor.status !== 'ok' && (
  <div className="sensor-last-note">
    <span className="note-icon">📝</span>
    <span className="note-preview">{sensor.last_note}</span>
  </div>
)}
```

**OU** limpar a nota quando sensor volta a OK:

```css
/* Ocultar nota quando sensor está OK */
.sensor-card[data-status="ok"] .sensor-last-note {
  display: none;
}
```

---

## 🔧 CORREÇÃO 4: Erro ao Excluir Probe

### Problema:
"Not Found" ao excluir probe

### Diagnóstico:
Verificar endpoint da API

```javascript
// Em Probes.js
const handleDeleteProbe = async (probeId) => {
  try {
    console.log('Excluindo probe ID:', probeId);
    await api.delete(`/api/v1/probes/${probeId}`);
    // ...
  } catch (error) {
    console.error('Erro ao excluir probe:', error.response?.data || error);
    alert(`Erro ao excluir probe: ${error.response?.data?.detail || error.message}`);
  }
};
```

### Verificar na API:
```python
# api/routers/probes.py
@router.delete("/{probe_id}")
async def delete_probe(
    probe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    probe = db.query(Probe).filter(Probe.id == probe_id).first()
    if not probe:
        raise HTTPException(status_code=404, detail="Probe não encontrado")
    
    # Verificar se há servidores usando este probe
    servers_count = db.query(Server).filter(Server.probe_id == probe_id).count()
    if servers_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Não é possível excluir. Existem {servers_count} servidores usando este probe."
        )
    
    db.delete(probe)
    db.commit()
    return {"message": "Probe excluído com sucesso"}
```

---

## 🔧 CORREÇÃO 5: NOC - Servidores Somem com Alerta

### Problema:
Quando há incidente, servidores desaparecem da lista

### Causa Provável:
Filtro incorreto no frontend ou backend

### Solução Backend:
```python
# api/routers/noc_realtime.py
# Garantir que TODOS os servidores sejam retornados
servers = db.query(Server).filter(server_filter).all()

# NÃO filtrar por status de incidente
# Retornar TODOS os servidores com seus respectivos status
```

### Solução Frontend:
```javascript
// NOCRealTime.js
const renderServers = () => (
  <div className="noc-view servers-view">
    <div className="servers-grid-modern">
      {data.servers && data.servers.length > 0 ? (
        data.servers.map(server => (
          <div key={server.id} className={`server-card-modern ${server.status}`}>
            {/* ... */}
          </div>
        ))
      ) : (
        <div className="no-servers">Nenhum servidor encontrado</div>
      )}
    </div>
  </div>
);
```

---

## 🔧 CORREÇÃO 6: Métricas Grafana - Ajustar CARD

### Problema:
Layout do card de métricas precisa ajuste

### Melhorias:
1. Aumentar padding interno
2. Melhorar alinhamento das barras
3. Ajustar tamanho dos valores

```css
/* MetricsViewer.css */
.server-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
  overflow: hidden;
  min-height: 200px;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.server-header h4 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #f3f4f6;
}

.server-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 0 8px;
}

.metric-label {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #f3f4f6;
  margin-bottom: 8px;
}
```

---

## 📝 RESUMO DAS CORREÇÕES

| # | Problema | Arquivo | Tipo |
|---|----------|---------|------|
| 1 | Card de sensores ruim | Management.css | CSS |
| 2 | Teste sai da aba | Settings.js | JS |
| 3 | Notas após resolver | Servers.js | JS/CSS |
| 4 | Erro excluir probe | probes.py | Backend |
| 5 | NOC servidores somem | noc_realtime.py | Backend |
| 6 | Card métricas | MetricsViewer.css | CSS |

---

## 🚀 PRIORIDADE DE APLICAÇÃO

1. **CRÍTICO:** NOC servidores somem (Problema 5)
2. **ALTO:** Notas após resolver (Problema 3)
3. **ALTO:** Erro excluir probe (Problema 4)
4. **MÉDIO:** Card de sensores (Problema 1)
5. **MÉDIO:** Card métricas (Problema 6)
6. **BAIXO:** Teste sai da aba (Problema 2)

---

**Data:** 02 de Março de 2026  
**Status:** 📋 Documentado - Aguardando Aplicação  
**Próximo Passo:** Aplicar correções por prioridade
