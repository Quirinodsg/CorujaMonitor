# Relatórios Personalizados - Funcionalidade Completa

**Data**: 26 de Fevereiro de 2026  
**Status**: ✅ Implementado e Funcional

## 🎯 Funcionalidades Implementadas

### 1. Visualizar Templates Pré-Definidos
- 10 templates prontos inspirados em PRTG e SolarWinds
- Geração instantânea ao clicar
- Ícones visuais para identificação rápida

### 2. Criar Relatórios Personalizados
- Botão "➕ Criar Relatório Personalizado" no topo
- Modal visual com formulário completo
- Opções de personalização:
  - Nome e descrição
  - Tipo de relatório (Incidentes, Servidores, Erros, etc.)
  - Seleção de colunas
  - Filtros específicos por tipo
  - Ordenação customizada

### 3. Salvar Templates como Relatórios
- Botão 💾 ao lado de cada template
- Cria cópia editável do template
- Permite ajustar antes de salvar

### 4. Editar Relatórios Salvos
- Botão ✏️ ao lado de cada relatório salvo
- Abre modal com dados preenchidos
- Atualiza relatório existente

### 5. Excluir Relatórios
- Botão 🗑️ ao lado de cada relatório salvo
- Confirmação antes de excluir
- Remove do banco de dados

## 📊 Templates Disponíveis

### Incidentes
1. **🏭 Servidores de Produção**
   - Servidores em ambiente de produção
   - Ordenado por quantidade de incidentes

2. **🚨 Servidores que Mais Alarmaram**
   - Top 10 com mais incidentes
   - Últimos 30 dias

3. **🔴 Incidentes Críticos**
   - Apenas severidade crítica
   - Últimos 7 dias

4. **⏳ Incidentes Não Resolvidos**
   - Status: aberto ou reconhecido
   - Ordenado por data (mais antigos primeiro)

### Erros
5. **❌ Erros Mais Comuns**
   - Agrupado por tipo de erro
   - Contagem de ocorrências
   - Servidores afetados

### Disponibilidade
6. **📊 Disponibilidade por Servidor**
   - Percentual de uptime
   - Horas de downtime
   - Últimos 30 dias

### Performance
7. **⚡ Resumo de Performance**
   - CPU, memória, disco
   - Médias e picos
   - Últimas 24 horas

8. **💾 Espaço em Disco Crítico**
   - Servidores acima de 85%
   - Espaço livre e total
   - Tendência

### Agrupamentos
9. **🏷️ Servidores por Tag**
   - Agrupado por tags
   - Contagem por grupo
   - Estatísticas agregadas

### IA
10. **🤖 Taxa de Resolução por IA**
    - Incidentes resolvidos automaticamente
    - Taxa de sucesso
    - Últimos 30 dias

## 🎨 Interface do Modal

### Campos do Formulário

#### Informações Básicas
- **Nome do Relatório** (obrigatório)
  - Texto livre
  - Ex: "Servidores Críticos de Produção"

- **Descrição** (opcional)
  - Textarea
  - Explica o objetivo do relatório

#### Configuração
- **Tipo de Relatório** (obrigatório)
  - 📋 Incidentes
  - 🖥️ Servidores
  - ❌ Erros
  - 📊 Disponibilidade
  - ⚡ Performance

- **Colunas a Exibir**
  - Checkboxes múltiplos
  - Colunas disponíveis variam por tipo
  - Seleção padrão inteligente

#### Filtros (variam por tipo)

**Para Incidentes:**
- Período (últimas 24h, 7d, 30d, 90d)
- Severidade (crítico, aviso, info)
- Status (aberto, reconhecido, resolvido)

**Para Servidores:**
- Ambiente (produção, homologação, desenvolvimento)
- Status (ativos, inativos)

#### Ordenação
- **Ordenar por**: Qualquer coluna selecionada
- **Ordem**: Crescente ou Decrescente

## 🔧 Como Usar

### Criar Novo Relatório do Zero

1. Clique em "➕ Criar Relatório Personalizado"
2. Preencha o nome (obrigatório)
3. Adicione descrição (opcional)
4. Selecione o tipo de relatório
5. Escolha as colunas desejadas
6. Configure filtros (opcional)
7. Defina ordenação (opcional)
8. Clique em "Criar Relatório"

### Criar Baseado em Template

1. Localize o template desejado
2. Clique no botão 💾 ao lado
3. Modal abre com dados do template
4. Ajuste nome e configurações
5. Clique em "Criar Relatório"

### Editar Relatório Existente

1. Vá para "💾 Meus Relatórios Salvos"
2. Clique no botão ✏️ ao lado do relatório
3. Modal abre com dados atuais
4. Faça as alterações desejadas
5. Clique em "Atualizar Relatório"

### Excluir Relatório

1. Vá para "💾 Meus Relatórios Salvos"
2. Clique no botão 🗑️ ao lado do relatório
3. Confirme a exclusão
4. Relatório é removido

### Gerar Relatório

1. Clique em qualquer template ou relatório salvo
2. Aguarde geração (loading)
3. Visualize os dados na área principal
4. Use "🖨️ Imprimir / Exportar PDF" se necessário

## 💾 Estrutura de Dados

### Relatório Salvo
```json
{
  "id": 1,
  "name": "Servidores Críticos Produção",
  "description": "Servidores de produção com mais de 5 incidentes",
  "report_type": "servers",
  "filters": {
    "environment": "production",
    "is_active": true
  },
  "columns": [
    "hostname",
    "ip_address",
    "os_type",
    "incidents_count"
  ],
  "sort_by": "incidents_count",
  "sort_order": "desc",
  "is_public": false,
  "is_favorite": false,
  "created_at": "2026-02-26T10:00:00",
  "updated_at": "2026-02-26T11:30:00",
  "last_generated_at": "2026-02-26T14:45:00",
  "user_id": 1,
  "tenant_id": 1
}
```

## 🎯 Colunas Disponíveis por Tipo

### Incidentes
- Data/Hora (created_at)
- Servidor (hostname)
- IP (ip_address)
- Sensor (sensor_name)
- Tipo de Sensor (sensor_type)
- Severidade (severity)
- Status (status)
- Descrição (description)
- Tempo de Resolução (resolution_time)
- Idade (age_hours)

### Servidores
- Servidor (hostname)
- IP (ip_address)
- Sistema Operacional (os_type)
- Ambiente (environment)
- Tipo (device_type)
- Ativo (is_active)
- Incidentes (incidents_count)

### Erros
- Tipo de Erro (error_type)
- Tipo de Sensor (sensor_type)
- Ocorrências (occurrence_count)
- Servidores Afetados (affected_servers)
- Primeira Ocorrência (first_seen)
- Última Ocorrência (last_seen)

## 🎨 Estilos Visuais

### Cores
- **Header do Modal**: Gradiente roxo (#667eea → #764ba2)
- **Botão Salvar**: Verde (#4caf50)
- **Botão Editar**: Azul (#2196f3)
- **Botão Excluir**: Vermelho (#f44336)
- **Botão Primário**: Gradiente roxo
- **Botão Secundário**: Branco com borda

### Animações
- **Modal**: Fade in + Slide up
- **Botões**: Hover com scale e shadow
- **Botão Fechar**: Rotação 90° no hover

### Responsividade
- Desktop: 3 colunas de checkboxes
- Tablet: 2 colunas
- Mobile: 1 coluna
- Modal: 90% largura em mobile

## 🔍 Validações

### Obrigatórios
- Nome do relatório
- Tipo de relatório

### Opcionais
- Descrição
- Colunas (usa padrão se vazio)
- Filtros
- Ordenação

### Mensagens de Erro
- "Por favor, informe um nome para o relatório"
- "Erro ao salvar relatório: [detalhes]"
- "Tem certeza que deseja excluir este relatório?"

## 📱 Fluxo de Uso Completo

```
1. Usuário acessa Relatórios
   ↓
2. Vê templates pré-definidos
   ↓
3. Opções:
   a) Gerar template diretamente
   b) Salvar template como relatório
   c) Criar relatório do zero
   ↓
4. Se criar/editar:
   - Preenche formulário
   - Seleciona colunas
   - Configura filtros
   - Define ordenação
   ↓
5. Salva relatório
   ↓
6. Aparece em "Meus Relatórios Salvos"
   ↓
7. Pode:
   - Gerar relatório
   - Editar configurações
   - Excluir relatório
```

## 🚀 Próximas Melhorias Sugeridas

### Funcionalidades Adicionais
1. **Favoritar relatórios**
   - Marcar como favorito
   - Seção separada de favoritos

2. **Compartilhar relatórios**
   - Tornar público para outros usuários
   - Permissões de visualização

3. **Agendar geração**
   - Gerar automaticamente
   - Enviar por email

4. **Exportar formatos**
   - CSV (já implementado)
   - Excel
   - JSON

5. **Gráficos personalizados**
   - Adicionar visualizações
   - Tipos de gráfico configuráveis

6. **Filtros avançados**
   - Múltiplos valores
   - Operadores (AND, OR)
   - Ranges de data customizados

7. **Templates de usuário**
   - Criar templates próprios
   - Compartilhar com equipe

## ✅ Checklist de Teste

### Criar Relatório
- [ ] Abrir modal de criação
- [ ] Preencher nome
- [ ] Selecionar tipo
- [ ] Escolher colunas
- [ ] Configurar filtros
- [ ] Definir ordenação
- [ ] Salvar com sucesso
- [ ] Aparecer em "Meus Relatórios"

### Editar Relatório
- [ ] Abrir modal de edição
- [ ] Dados preenchidos corretamente
- [ ] Alterar configurações
- [ ] Salvar alterações
- [ ] Mudanças refletidas

### Excluir Relatório
- [ ] Clicar em excluir
- [ ] Confirmar exclusão
- [ ] Relatório removido
- [ ] Não aparece mais na lista

### Gerar Relatório
- [ ] Clicar em template
- [ ] Loading aparece
- [ ] Dados carregados
- [ ] Tabela renderizada
- [ ] Colunas corretas
- [ ] Filtros aplicados
- [ ] Ordenação correta

### Salvar Template
- [ ] Clicar em 💾 no template
- [ ] Modal abre com dados
- [ ] Nome ajustado automaticamente
- [ ] Salvar como novo relatório
- [ ] Aparecer em "Meus Relatórios"

## 📝 Notas Técnicas

### Endpoints Utilizados
- `GET /api/v1/custom-reports/templates` - Listar templates
- `GET /api/v1/custom-reports/` - Listar relatórios do usuário
- `POST /api/v1/custom-reports/` - Criar relatório
- `PUT /api/v1/custom-reports/{id}` - Atualizar relatório
- `DELETE /api/v1/custom-reports/{id}` - Excluir relatório
- `POST /api/v1/custom-reports/{id}/generate` - Gerar relatório salvo
- `POST /api/v1/custom-reports/generate-template` - Gerar template

### Estado do Componente
```javascript
// Templates e dados
const [templates, setTemplates] = useState([]);
const [customTemplates, setCustomTemplates] = useState([]);
const [myReports, setMyReports] = useState([]);
const [reportData, setReportData] = useState(null);

// Modal e edição
const [showCreateModal, setShowCreateModal] = useState(false);
const [showEditModal, setShowEditModal] = useState(false);
const [editingReport, setEditingReport] = useState(null);

// Formulário
const [reportName, setReportName] = useState('');
const [reportDescription, setReportDescription] = useState('');
const [reportType, setReportType] = useState('incidents');
const [filters, setFilters] = useState({});
const [selectedColumns, setSelectedColumns] = useState([]);
const [sortBy, setSortBy] = useState('');
const [sortOrder, setSortOrder] = useState('desc');
```

## 🎉 Conclusão

Sistema completo de relatórios personalizados implementado com:
- ✅ Visualização de templates
- ✅ Criação de relatórios
- ✅ Edição de relatórios
- ✅ Exclusão de relatórios
- ✅ Geração de dados
- ✅ Interface visual moderna
- ✅ Validações e feedback
- ✅ Responsividade

O sistema está pronto para uso e permite aos usuários criar relatórios totalmente personalizados baseados em suas necessidades específicas!
