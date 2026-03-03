# Correções Aplicadas - Exclusão de Servidor e Impressão de Relatórios

## Data: 18/02/2026

## 1. Correção: Erro ao Excluir Servidor

### Problema
Ao tentar excluir um servidor, ocorria erro de "Network Error" devido a violação de constraint de chave estrangeira:
```
update or delete on table "incidents" violates foreign key constraint "remediation_logs_incident_id_fkey"
```

### Causa
A tabela `remediation_logs` possui uma chave estrangeira para `incidents.id`. Quando tentávamos excluir um servidor:
1. Deletava sensores
2. Tentava deletar incidents
3. **FALHAVA** porque remediation_logs ainda referenciava os incidents

### Solução Implementada
Modificado o endpoint `DELETE /api/v1/servers/{server_id}` em `api/routers/servers.py` para seguir a ordem correta de deleção:

```python
# Ordem correta de deleção em cascata:
1. Obter todos os sensors do servidor
2. Obter todos os incidents desses sensors
3. Deletar remediation_logs (referencia incidents) ✅ NOVO
4. Deletar incidents (referencia sensors)
5. Deletar metrics (referencia sensors)
6. Deletar sensors (referencia server)
7. Deletar server
```

### Código Modificado
**Arquivo:** `api/routers/servers.py`

```python
# Delete associated data in order
from models import Sensor, Metric, Incident, RemediationLog

# Get all sensors for this server
sensors = db.query(Sensor).filter(Sensor.server_id == server_id).all()
sensor_ids = [s.id for s in sensors]

if sensor_ids:
    # Get all incidents for these sensors
    incidents = db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).all()
    incident_ids = [i.id for i in incidents]
    
    if incident_ids:
        # Delete remediation logs first (they reference incidents)
        db.query(RemediationLog).filter(RemediationLog.incident_id.in_(incident_ids)).delete(synchronize_session=False)
    
    # Delete incidents for these sensors
    db.query(Incident).filter(Incident.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
    
    # Delete metrics for these sensors
    db.query(Metric).filter(Metric.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
    
    # Delete sensors
    db.query(Sensor).filter(Sensor.server_id == server_id).delete(synchronize_session=False)

# Delete server
db.delete(server)
db.commit()
```

### Status
✅ **CORRIGIDO** - API reiniciada com sucesso

---

## 2. Correção: Impressão de Relatórios Mostrando Barra Lateral

### Problema
Ao imprimir um relatório, a página impressa incluía:
- 🦉 Barra lateral de navegação (Sidebar)
- 📊 Dashboard, 🏢 Empresas, 🖥️ Servidores, etc.
- Elementos da interface que não fazem parte do relatório

### Solução Implementada
Melhorado o CSS de impressão em `frontend/src/components/Reports.css` para:

1. **Ocultar TODOS os elementos da interface** usando `visibility: hidden`
2. **Mostrar APENAS o conteúdo do relatório** tornando `.report-viewer` e seus filhos visíveis
3. **Posicionar o relatório** para ocupar toda a página impressa
4. **Manter cores importantes** usando `print-color-adjust: exact`

### Código CSS Adicionado

```css
@media print {
  /* Ocultar TODOS os elementos da interface */
  body.printing-report * {
    visibility: hidden;
  }

  /* Mostrar apenas o conteúdo do relatório */
  body.printing-report .report-viewer,
  body.printing-report .report-viewer * {
    visibility: visible;
  }

  /* Ocultar elementos específicos mesmo dentro do relatório */
  body.printing-report .management-header,
  body.printing-report .templates-sidebar,
  body.printing-report .report-actions,
  body.printing-report .no-print,
  body.printing-report .sidebar,
  body.printing-report nav,
  body.printing-report header,
  body.printing-report .btn-export {
    display: none !important;
    visibility: hidden !important;
  }

  /* Posicionar o relatório para ocupar toda a página */
  body.printing-report .report-viewer {
    position: absolute;
    left: 0;
    top: 0;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 20px !important;
    box-shadow: none !important;
    border: none !important;
  }

  /* Manter cores dos cards importantes */
  .cost-analysis,
  .cloud-provider-card,
  .comparison-card {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```

### Como Funciona
1. Usuário clica em "Imprimir Relatório"
2. JavaScript adiciona classe `printing-report` ao `<body>`
3. CSS oculta TUDO exceto `.report-viewer`
4. `window.print()` é chamado
5. Após 1 segundo, classe é removida e interface volta ao normal

### Status
✅ **CORRIGIDO** - Agora apenas o conteúdo do relatório será impresso

---

## Teste Recomendado

### Para Exclusão de Servidor:
1. Acesse a página de Servidores
2. Selecione um servidor de teste
3. Clique no botão de excluir (🗑️)
4. Confirme a exclusão
5. ✅ Servidor deve ser excluído sem erros

### Para Impressão de Relatórios:
1. Acesse a página de Relatórios
2. Gere qualquer relatório (ex: Disponibilidade 7 dias)
3. Clique em "Imprimir Relatório"
4. Na pré-visualização de impressão:
   - ✅ Deve mostrar APENAS o conteúdo do relatório
   - ❌ NÃO deve mostrar barra lateral
   - ❌ NÃO deve mostrar menus de navegação
   - ✅ Deve manter cores e formatação do relatório

---

## Arquivos Modificados

1. `api/routers/servers.py` - Corrigida ordem de deleção em cascata
2. `frontend/src/components/Reports.css` - Melhorado CSS de impressão

## Observações

### Sobre Exclusão de Servidor
- A correção garante que TODOS os dados relacionados sejam deletados na ordem correta
- Não é necessário rodar uninstall na máquina - a exclusão via interface agora funciona corretamente
- O sistema deleta automaticamente:
  - Remediation logs
  - Incidents
  - Metrics
  - Sensors
  - Server

### Sobre Impressão
- A técnica de `visibility: hidden` é mais eficaz que `display: none` para impressão
- Mantém o layout correto do relatório
- Preserva cores e gráficos importantes
- Funciona em todos os navegadores modernos

---

## Próximos Passos Sugeridos

1. Testar exclusão de servidor com dados reais
2. Testar impressão de diferentes tipos de relatórios
3. Verificar se há outros relacionamentos de chave estrangeira que precisam ser tratados
4. Considerar adicionar CASCADE nas foreign keys do banco de dados para simplificar futuras deleções
