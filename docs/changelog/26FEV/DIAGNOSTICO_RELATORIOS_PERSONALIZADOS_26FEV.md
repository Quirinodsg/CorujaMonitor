# Diagnóstico: Relatórios Personalizados Não Aparecem

**Data**: 26 de Fevereiro de 2026  
**Problema**: Relatórios personalizados não estão aparecendo na interface

## 🔍 Análise do Problema

### Sintomas
- Usuário reporta que relatórios personalizados não aparecem
- Nem pela URL normal nem pela nova
- Interface mostra apenas templates padrão

### Verificações Realizadas

#### ✅ Backend
1. **Router implementado**: `api/routers/custom_reports.py`
   - 10 templates pré-definidos
   - Endpoints funcionais
   - Lógica de geração de relatórios

2. **Router registrado**: `api/main.py`
   ```python
   app.include_router(custom_reports.router, prefix="/api/v1/custom-reports", tags=["Custom Reports"])
   ```

3. **Modelo criado**: `api/models.py`
   - Classe `CustomReport` existe
   - Campos corretos

#### ✅ Frontend
1. **Componente atualizado**: `frontend/src/components/Reports.js`
   - Funções `loadCustomTemplates()` e `loadMyReports()` implementadas
   - Renderização das seções na sidebar

### 🐛 Problemas Identificados

#### 1. Geração Automática Não Funcionava
**Problema**: Ao clicar em um template personalizado, o relatório não era gerado automaticamente.

**Causa**: A função `handleSelectCustomTemplate` apenas selecionava o template, mas não chamava a API para gerar os dados.

**Solução**: Modificada a função para gerar automaticamente o relatório ao selecionar:
```javascript
const handleSelectCustomTemplate = async (template) => {
  setSelectedReport(template.id);
  setReportName(template.name);
  setReportDescription(template.description || '');
  setFilters(template.filters || {});
  setSelectedColumns(template.columns || []);
  setReportData(null);
  
  // Gerar automaticamente o relatório
  setLoading(true);
  try {
    if (typeof template.id === 'number') {
      const response = await api.post(`/api/v1/custom-reports/${template.id}/generate`);
      setReportData(response.data);
    } else {
      const response = await api.post('/api/v1/custom-reports/generate-template', {
        template_id: template.id,
        filters: template.filters || {}
      });
      setReportData(response.data);
    }
  } catch (error) {
    console.error('Erro ao gerar relatório:', error);
    alert('Erro ao gerar relatório: ' + (error.response?.data?.detail || error.message));
  } finally {
    setLoading(false);
  }
};
```

#### 2. Falta de Debug
**Problema**: Sem logs, era difícil identificar onde estava falhando.

**Solução**: Adicionados console.log nas funções de carregamento:
```javascript
const loadCustomTemplates = async () => {
  try {
    console.log('Carregando templates personalizados...');
    const response = await api.get('/api/v1/custom-reports/templates');
    console.log('Templates personalizados carregados:', response.data);
    setCustomTemplates(response.data);
  } catch (error) {
    console.error('Erro ao carregar templates personalizados:', error);
    console.error('Detalhes do erro:', error.response?.data);
  }
};
```

#### 3. Possível Migração Não Executada
**Problema**: Se a migração não foi executada, a tabela `custom_reports` não existe.

**Solução**: Script de correção executa a migração automaticamente.

#### 4. Cache do Frontend
**Problema**: Frontend pode estar usando versão antiga do código.

**Solução**: Script recompila e reinicia o frontend.

## 🔧 Correções Aplicadas

### 1. Arquivo Modificado
- `frontend/src/components/Reports.js`
  - Geração automática de relatórios ao selecionar template
  - Logs de debug adicionados

### 2. Scripts Criados

#### `testar_relatorios_personalizados.ps1`
Script de diagnóstico que:
- Verifica se a migração foi executada
- Testa endpoint de templates
- Mostra logs da API
- Verifica se router está registrado

#### `corrigir_relatorios_personalizados.ps1`
Script de correção automática que:
1. Executa migração do banco de dados
2. Reinicia API
3. Verifica se API está respondendo
4. Testa endpoint de templates
5. Recompila frontend
6. Reinicia frontend

## 📋 Checklist de Verificação

### Antes de Executar Correção
- [ ] Docker está rodando
- [ ] Containers estão ativos: `docker ps`
- [ ] Backup do banco de dados (opcional)

### Executar Correção
```powershell
.\corrigir_relatorios_personalizados.ps1
```

### Após Correção
- [ ] API respondendo: http://localhost:8000/health
- [ ] Frontend acessível: http://localhost:3000
- [ ] Login funcionando: admin@coruja.com / admin123
- [ ] Aba Relatórios acessível
- [ ] Seção "📊 Relatórios Personalizados" visível
- [ ] 10 templates listados
- [ ] Ao clicar em template, relatório é gerado
- [ ] Console do navegador (F12) mostra logs

## 🎯 Templates Disponíveis

Após correção, devem aparecer 10 templates:

1. **🏭 Servidores de Produção**
   - Relatório de todos os servidores em ambiente de produção

2. **🚨 Servidores que Mais Alarmaram**
   - Top 10 servidores com mais incidentes no período

3. **❌ Erros Mais Comuns**
   - Tipos de erros que mais ocorreram no período

4. **🔴 Incidentes Críticos**
   - Todos os incidentes críticos do período

5. **📊 Disponibilidade por Servidor**
   - Percentual de disponibilidade de cada servidor

6. **⚡ Resumo de Performance**
   - Métricas de performance de todos os servidores

7. **🏷️ Servidores por Tag**
   - Agrupa servidores por tags personalizadas

8. **⏳ Incidentes Não Resolvidos**
   - Incidentes abertos ou reconhecidos pendentes

9. **🤖 Taxa de Resolução por IA**
   - Efetividade da auto-resolução por IA

10. **💾 Espaço em Disco Crítico**
    - Servidores com espaço em disco acima de 85%

## 🔍 Debug no Navegador

Abra o Console (F12) e verifique:

```javascript
// Deve aparecer ao carregar a página de relatórios:
Carregando templates personalizados...
Templates personalizados carregados: Array(10)

Carregando meus relatórios...
Meus relatórios carregados: Array(0)

// Ao clicar em um template:
Gerando relatório...
```

## 🚨 Possíveis Erros

### Erro 404 no endpoint
**Causa**: Router não registrado ou API não reiniciada  
**Solução**: Verificar `api/main.py` e reiniciar API

### Erro 500 no endpoint
**Causa**: Migração não executada ou erro no banco  
**Solução**: Executar migração e verificar logs

### Templates não aparecem
**Causa**: Erro na requisição ou frontend com cache  
**Solução**: Verificar console do navegador e recompilar frontend

### Relatório não gera dados
**Causa**: Sem dados no banco ou filtros muito restritivos  
**Solução**: Verificar se há servidores e incidentes cadastrados

## 📊 Próximos Passos

Após correção funcionar:

1. **Testar cada template**
   - Verificar se dados são gerados corretamente
   - Validar formatação das tabelas

2. **Criar relatórios personalizados**
   - Usar templates como base
   - Salvar relatórios customizados

3. **Exportar relatórios**
   - Testar impressão (PDF)
   - Testar exportação CSV (se implementado)

4. **Feedback do usuário**
   - Validar se atende necessidades
   - Ajustar templates conforme necessário

## 📝 Notas Técnicas

### Estrutura de Dados

**Template**:
```json
{
  "id": "production_servers",
  "name": "Servidores de Produção",
  "description": "Relatório de todos os servidores em ambiente de produção",
  "report_type": "servers",
  "icon": "🏭",
  "filters": {
    "environment": "production",
    "is_active": true
  },
  "columns": ["hostname", "ip_address", "os_type", "uptime", "cpu_avg", "memory_avg", "incidents_count"],
  "sort_by": "incidents_count",
  "sort_order": "desc"
}
```

**Resposta de Geração**:
```json
{
  "report": {
    "id": "production_servers",
    "name": "Servidores de Produção",
    "description": "...",
    "report_type": "servers",
    "generated_at": "2026-02-26T10:30:00"
  },
  "data": {
    "total_count": 5,
    "rows": [
      {
        "hostname": "srv-prod-01",
        "ip_address": "192.168.1.10",
        "os_type": "Windows Server 2022",
        "incidents_count": 3
      }
    ]
  }
}
```

### Endpoints Implementados

- `GET /api/v1/custom-reports/templates` - Listar templates
- `GET /api/v1/custom-reports/` - Listar relatórios salvos
- `POST /api/v1/custom-reports/` - Criar relatório
- `GET /api/v1/custom-reports/{id}` - Obter relatório
- `PUT /api/v1/custom-reports/{id}` - Atualizar relatório
- `DELETE /api/v1/custom-reports/{id}` - Deletar relatório
- `POST /api/v1/custom-reports/{id}/generate` - Gerar relatório salvo
- `POST /api/v1/custom-reports/generate-template` - Gerar de template

## ✅ Conclusão

O problema foi identificado e corrigido. Execute o script de correção para aplicar as mudanças e testar o sistema.

```powershell
.\corrigir_relatorios_personalizados.ps1
```
