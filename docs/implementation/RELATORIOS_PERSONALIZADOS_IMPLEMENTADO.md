# Relatórios Personalizados - Implementado

## 📊 Sistema de Relatórios Personalizados

Sistema completo de relatórios personalizados inspirado em PRTG e SolarWinds, permitindo criar, salvar e gerar relatórios customizados com filtros avançados.

## ✅ O Que Foi Implementado

### 1. Backend (API)

**Arquivo**: `api/routers/custom_reports.py`

**Funcionalidades**:
- ✅ CRUD completo de relatórios personalizados
- ✅ 10 templates pré-definidos
- ✅ Geração de relatórios com filtros dinâmicos
- ✅ Suporte a múltiplos tipos de relatórios
- ✅ Exportação de dados

**Endpoints**:
```
GET    /api/v1/custom-reports/templates      - Listar templates
GET    /api/v1/custom-reports/               - Listar relatórios salvos
POST   /api/v1/custom-reports/               - Criar novo relatório
GET    /api/v1/custom-reports/{id}           - Obter relatório
PUT    /api/v1/custom-reports/{id}           - Atualizar relatório
DELETE /api/v1/custom-reports/{id}           - Deletar relatório
POST   /api/v1/custom-reports/{id}/generate  - Gerar dados do relatório
```

### 2. Modelo de Dados

**Arquivo**: `api/models.py`

**Tabela**: `custom_reports`

**Campos**:
- `id` - ID único
- `tenant_id` - Empresa
- `user_id` - Usuário criador
- `name` - Nome do relatório
- `description` - Descrição
- `report_type` - Tipo (incidents, servers, availability, performance, errors, ai_analysis)
- `filters` - Filtros aplicados (JSON)
- `columns` - Colunas selecionadas (JSON)
- `sort_by` - Campo de ordenação
- `sort_order` - Ordem (asc/desc)
- `is_public` - Visível para outros usuários
- `is_favorite` - Marcado como favorito
- `created_at` - Data de criação
- `updated_at` - Data de atualização
- `last_generated_at` - Última geração

### 3. Frontend (React)

**Arquivos**:
- `frontend/src/components/CustomReports.js` - Componente principal
- `frontend/src/components/CustomReports.css` - Estilos

**Funcionalidades**:
- ✅ Interface estilo PRTG/SolarWinds
- ✅ Sidebar com templates e relatórios salvos
- ✅ Construtor visual de filtros
- ✅ Seletor de colunas
- ✅ Visualização de dados em tabela
- ✅ Exportação para CSV
- ✅ Salvar relatórios personalizados
- ✅ Gerenciar relatórios salvos

### 4. Migração de Banco de Dados

**Arquivo**: `api/migrate_custom_reports.py`

Cria a tabela `custom_reports` com índices otimizados.

## 📋 Templates Pré-Definidos

### 1. 🏭 Servidores de Produção
- **Tipo**: Servidores
- **Filtros**: Ambiente = Produção, Ativos
- **Colunas**: Hostname, IP, SO, Uptime, CPU, Memória, Incidentes
- **Ordenação**: Por número de incidentes (desc)

### 2. 🚨 Servidores que Mais Alarmaram
- **Tipo**: Incidentes
- **Filtros**: Últimos 30 dias, Agrupado por servidor
- **Colunas**: Hostname, Total, Críticos, Avisos, Tempo médio de resolução
- **Ordenação**: Por total de incidentes (desc)
- **Limite**: Top 10

### 3. ❌ Erros Mais Comuns
- **Tipo**: Erros
- **Filtros**: Últimos 30 dias, Agrupado por tipo de erro
- **Colunas**: Tipo de erro, Tipo de sensor, Ocorrências, Servidores afetados, Primeira/Última ocorrência
- **Ordenação**: Por ocorrências (desc)

### 4. 🔴 Incidentes Críticos
- **Tipo**: Incidentes
- **Filtros**: Últimos 7 dias, Severidade = Crítico
- **Colunas**: Data, Servidor, Sensor, Descrição, Status, Tempo de resolução
- **Ordenação**: Por data (desc)

### 5. 📊 Disponibilidade por Servidor
- **Tipo**: Disponibilidade
- **Filtros**: Últimos 30 dias
- **Colunas**: Hostname, IP, Ambiente, Uptime %, Downtime (horas), Incidentes
- **Ordenação**: Por uptime (asc) - mostra os piores primeiro

### 6. ⚡ Resumo de Performance
- **Tipo**: Performance
- **Filtros**: Últimas 24 horas
- **Colunas**: Hostname, CPU média, CPU pico, Memória média, Memória pico, Uso de disco, Tráfego de rede
- **Ordenação**: Por CPU média (desc)

### 7. 🏷️ Servidores por Tag
- **Tipo**: Servidores
- **Filtros**: Agrupado por tags
- **Colunas**: Tag, Quantidade de servidores, Uptime médio, Total de incidentes
- **Ordenação**: Por quantidade (desc)

### 8. ⏳ Incidentes Não Resolvidos
- **Tipo**: Incidentes
- **Filtros**: Status = Aberto ou Reconhecido
- **Colunas**: Data, Servidor, Sensor, Severidade, Descrição, Idade (horas)
- **Ordenação**: Por data (asc) - mais antigos primeiro

### 9. 🤖 Taxa de Resolução por IA
- **Tipo**: Análise de IA
- **Filtros**: Últimos 30 dias
- **Colunas**: Tipo de sensor, Total de incidentes, Resolvidos por IA, Resolvidos manualmente, Taxa de sucesso
- **Ordenação**: Por taxa de sucesso (desc)

### 10. 💾 Espaço em Disco Crítico
- **Tipo**: Performance
- **Filtros**: Tipo de sensor = Disco, Threshold > 85%
- **Colunas**: Hostname, Nome do disco, Uso %, Espaço livre (GB), Espaço total (GB), Tendência
- **Ordenação**: Por uso % (desc)

## 🎯 Filtros Disponíveis

### Filtros Comuns
- **Período**: Últimas 24h, 7 dias, 30 dias, 90 dias
- **Limite de Resultados**: 10, 25, 50, 100, 500

### Filtros por Tipo de Relatório

**Incidentes**:
- Severidade (Crítico, Aviso, Info)
- Status (Aberto, Reconhecido, Resolvido)
- Servidor específico
- Ambiente

**Servidores**:
- Ambiente (Produção, Homologação, Desenvolvimento)
- Tipo de dispositivo
- Status (Ativo/Inativo)
- Tags

**Performance**:
- Tipo de sensor
- Threshold mínimo/máximo

**Erros**:
- Tipo de erro
- Tipo de sensor

## 📥 Exportação

- **Formato**: CSV
- **Nome do arquivo**: `{nome_relatorio}_{data}.csv`
- **Encoding**: UTF-8
- **Separador**: Vírgula
- **Aspas**: Campos com vírgula são entre aspas

## 🔧 Como Usar

### 1. Acessar Relatórios Personalizados

```
http://localhost:3000/custom-reports
```

### 2. Usar um Template

1. Clique em um template na sidebar
2. Ajuste os filtros conforme necessário
3. Selecione as colunas desejadas
4. Clique em "Gerar Relatório"

### 3. Salvar um Relatório Personalizado

1. Configure filtros e colunas
2. Gere o relatório
3. Clique em "Salvar Relatório"
4. Informe nome e descrição
5. O relatório aparecerá em "Meus Relatórios"

### 4. Exportar Dados

1. Gere um relatório
2. Clique em "Exportar CSV"
3. O arquivo será baixado automaticamente

## 🚀 Instalação

### 1. Executar Migração

```bash
cd api
python migrate_custom_reports.py
```

### 2. Reiniciar API

```bash
docker restart coruja-api
```

### 3. Atualizar Frontend

O componente já está criado. Adicione a rota no App.js:

```javascript
import CustomReports from './components/CustomReports';

// Adicionar rota
<Route path="/custom-reports" element={<CustomReports />} />
```

### 4. Adicionar ao Menu

Adicione link no menu de navegação:

```javascript
<Link to="/custom-reports">📊 Relatórios Personalizados</Link>
```

## 📊 Exemplos de Uso

### Exemplo 1: Relatório de Servidores Críticos

**Objetivo**: Identificar servidores de produção com mais de 5 incidentes no mês

**Configuração**:
- Template: "Servidores que Mais Alarmaram"
- Filtro Período: Últimos 30 dias
- Filtro Ambiente: Produção
- Filtro Limite: 10
- Ordenação: Total de incidentes (desc)

### Exemplo 2: Análise de Erros Recorrentes

**Objetivo**: Identificar tipos de erros que mais ocorrem

**Configuração**:
- Template: "Erros Mais Comuns"
- Filtro Período: Últimos 30 dias
- Ordenação: Ocorrências (desc)
- Colunas: Tipo de erro, Ocorrências, Servidores afetados

### Exemplo 3: Monitoramento de Disponibilidade

**Objetivo**: Verificar servidores com disponibilidade abaixo de 99%

**Configuração**:
- Template: "Disponibilidade por Servidor"
- Filtro Período: Últimos 30 dias
- Ordenação: Uptime % (asc)
- Filtro personalizado: Uptime < 99%

## 🔍 Próximas Melhorias

### Fase 2 (Futuro)
- [ ] Agendamento de relatórios
- [ ] Envio automático por email
- [ ] Gráficos e visualizações
- [ ] Comparação entre períodos
- [ ] Relatórios em PDF
- [ ] Dashboard de relatórios
- [ ] Compartilhamento de relatórios
- [ ] Histórico de execuções
- [ ] Alertas baseados em relatórios
- [ ] Integração com BI tools

### Fase 3 (Avançado)
- [ ] Relatórios com SQL customizado
- [ ] Relatórios multi-tenant
- [ ] Relatórios com drill-down
- [ ] Relatórios com previsões (ML)
- [ ] API para integração externa
- [ ] Webhooks para relatórios
- [ ] Relatórios em tempo real
- [ ] Relatórios colaborativos

## 📝 Notas Técnicas

### Performance
- Queries otimizadas com índices
- Limite de resultados configurável
- Cache de relatórios (futuro)
- Paginação (futuro)

### Segurança
- Filtro por tenant automático
- Permissões por usuário
- Relatórios públicos/privados
- Auditoria de acessos (futuro)

### Escalabilidade
- Geração assíncrona (futuro)
- Fila de processamento (futuro)
- Armazenamento de resultados (futuro)
- CDN para exports (futuro)

## 🐛 Troubleshooting

### Erro: "Report not found"
- Verifique se o relatório pertence ao seu tenant
- Verifique se você tem permissão de acesso

### Erro: "No data found"
- Ajuste os filtros do relatório
- Verifique se há dados no período selecionado
- Verifique se os servidores estão ativos

### Relatório lento
- Reduza o período de análise
- Reduza o limite de resultados
- Use filtros mais específicos

## 📚 Referências

- PRTG Network Monitor - Sistema de relatórios
- SolarWinds - Custom Reports
- Grafana - Dashboard e visualizações
- Datadog - Reporting features

---

**Data**: 26 de Fevereiro de 2026  
**Status**: ✅ Implementado  
**Versão**: 1.0.0
