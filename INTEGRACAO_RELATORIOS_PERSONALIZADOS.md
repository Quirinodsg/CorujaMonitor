# Integração de Relatórios Personalizados - 26 de Fevereiro 2026

## ✅ O Que Foi Feito

Integrei os relatórios personalizados DENTRO do componente Reports.js existente, adicionando novas seções na sidebar sem criar uma URL separada.

## 📝 Modificações Realizadas

### 1. Frontend - Reports.js

**Arquivo**: `frontend/src/components/Reports.js`

**Mudanças**:
- ✅ Adicionado estado para relatórios personalizados
- ✅ Adicionadas funções para carregar templates personalizados
- ✅ Adicionadas funções para gerar relatórios personalizados
- ✅ Adicionada renderização de relatórios personalizados
- ✅ Adicionadas 2 novas seções na sidebar:
  - **📊 Relatórios Personalizados** - 10 templates estilo PRTG/SolarWinds
  - **💾 Meus Relatórios Salvos** - Relatórios customizados do usuário

**Novas Funções Adicionadas**:
```javascript
- loadCustomTemplates() - Carrega templates personalizados
- loadMyReports() - Carrega relatórios salvos do usuário
- handleSelectCustomTemplate() - Seleciona template personalizado
- handleGenerateCustomReport() - Gera relatório personalizado
- handleSaveCustomReport() - Salva relatório customizado
- handleExportCSV() - Exporta para CSV
- renderCustomReport() - Renderiza tabela de dados
- formatColumnName() - Formata nomes de colunas
- formatCellValue() - Formata valores das células
```

### 2. Backend - custom_reports.py

**Arquivo**: `api/routers/custom_reports.py`

**Novo Endpoint Adicionado**:
```python
POST /api/v1/custom-reports/generate-template
```

**Funcionalidade**: Gera relatório a partir de um template sem salvar no banco de dados.

## 📊 Templates Adicionados na Sidebar

### Seção: 📊 Relatórios Personalizados

1. **🏭 Servidores de Produção**
   - Filtra servidores em ambiente de produção
   - Mostra CPU, memória, uptime e incidentes

2. **🚨 Servidores que Mais Alarmaram**
   - Top 10 servidores com mais incidentes
   - Mostra total, críticos e avisos

3. **❌ Erros Mais Comuns**
   - Agrupa por tipo de erro
   - Mostra ocorrências e servidores afetados

4. **🔴 Incidentes Críticos**
   - Apenas incidentes críticos do período

5. **📊 Disponibilidade por Servidor**
   - Uptime % de cada servidor

6. **⚡ Resumo de Performance**
   - Métricas de CPU, memória, disco

7. **🏷️ Servidores por Tag**
   - Agrupa por tags personalizadas

8. **⏳ Incidentes Não Resolvidos**
   - Pendentes de resolução

9. **🤖 Taxa de Resolução por IA**
   - Efetividade da auto-resolução

10. **💾 Espaço em Disco Crítico**
    - Discos acima de 85%

### Seção: 💾 Meus Relatórios Salvos

- Mostra relatórios personalizados salvos pelo usuário
- Permite gerar novamente com um clique
- Mantém filtros e colunas configuradas

## 🎨 Como Aparece na Interface

```
📈 Relatórios
├── Templates Disponíveis
│   ├── 📊 Disponibilidade
│   │   ├── Disponibilidade Mensal
│   │   ├── Disponibilidade Trimestral
│   │   └── Disponibilidade Anual
│   ├── ⚠️ Problemas
│   │   ├── Máquinas com Mais Problemas (Mensal)
│   │   └── Máquinas com Mais Problemas (Trimestral)
│   ├── 🤖 Resoluções IA
│   │   ├── Resoluções por IA (Mensal)
│   │   ├── Resoluções por IA (Trimestral)
│   │   └── Resoluções por IA (Anual)
│   ├── 💻 Utilização de Recursos
│   │   ├── Utilização de CPU Mensal
│   │   └── Utilização de Memória Mensal
│   ├── 📊 Relatórios Personalizados ⭐ NOVO
│   │   ├── 🏭 Servidores de Produção
│   │   ├── 🚨 Servidores que Mais Alarmaram
│   │   ├── ❌ Erros Mais Comuns
│   │   ├── 🔴 Incidentes Críticos
│   │   ├── 📊 Disponibilidade por Servidor
│   │   ├── ⚡ Resumo de Performance
│   │   ├── 🏷️ Servidores por Tag
│   │   ├── ⏳ Incidentes Não Resolvidos
│   │   ├── 🤖 Taxa de Resolução por IA
│   │   └── 💾 Espaço em Disco Crítico
│   └── 💾 Meus Relatórios Salvos ⭐ NOVO
│       └── (Relatórios salvos pelo usuário)
```

## 🚀 Como Usar

### 1. Acessar Relatórios

```
http://localhost:3000/reports
```

(Mesma URL de sempre, não mudou!)

### 2. Usar um Template Personalizado

1. Role a sidebar até "📊 Relatórios Personalizados"
2. Clique em um dos 10 templates disponíveis
3. O relatório será gerado automaticamente
4. Visualize os dados em formato de tabela

### 3. Exportar para CSV

1. Após gerar um relatório personalizado
2. Clique no botão "📥 Exportar CSV" (se disponível)
3. O arquivo será baixado automaticamente

### 4. Salvar um Relatório Personalizado

1. Gere um relatório personalizado
2. Clique em "💾 Salvar Relatório" (se disponível)
3. Informe nome e descrição
4. O relatório aparecerá em "Meus Relatórios Salvos"

## 🔧 Instalação

### 1. Executar Migração (se ainda não executou)

```bash
cd api
python migrate_custom_reports.py
```

### 2. Reiniciar API

```bash
docker restart coruja-api
```

### 3. Atualizar Frontend

O código já foi modificado no Reports.js. Basta recarregar a página:

```
http://localhost:3000/reports
```

## ✅ Checklist de Verificação

- [ ] Migração do banco executada
- [ ] API reiniciada
- [ ] Acessou /reports
- [ ] Viu seção "📊 Relatórios Personalizados"
- [ ] Clicou em um template personalizado
- [ ] Relatório foi gerado com sucesso
- [ ] Dados aparecem em formato de tabela

## 📊 Exemplo de Uso

### Cenário: Ver servidores de produção com problemas

1. Acesse: http://localhost:3000/reports
2. Role a sidebar até "📊 Relatórios Personalizados"
3. Clique em "🏭 Servidores de Produção"
4. Aguarde a geração (alguns segundos)
5. Veja a tabela com:
   - Hostname
   - IP
   - Sistema Operacional
   - Ambiente
   - Total de Incidentes

### Cenário: Identificar erros recorrentes

1. Acesse: http://localhost:3000/reports
2. Role a sidebar até "📊 Relatórios Personalizados"
3. Clique em "❌ Erros Mais Comuns"
4. Aguarde a geração
5. Veja a tabela com:
   - Tipo de Erro
   - Tipo de Sensor
   - Ocorrências
   - Servidores Afetados
   - Primeira/Última Ocorrência

## 🎯 Diferenças da Implementação Anterior

| Aspecto | Antes (CustomReports.js) | Agora (Integrado) |
|---------|--------------------------|-------------------|
| URL | /custom-reports | /reports |
| Componente | Separado | Integrado |
| Sidebar | Nova sidebar | Mesma sidebar |
| Templates | Separados | Junto com existentes |
| Navegação | Nova rota | Mesma rota |
| Experiência | 2 páginas diferentes | 1 página unificada |

## 🔍 Vantagens da Integração

✅ **Experiência Unificada**: Todos os relatórios em um só lugar  
✅ **Sem Confusão**: Não precisa navegar entre páginas  
✅ **Consistência**: Mesma interface para todos os relatórios  
✅ **Facilidade**: Usuário já conhece a página de relatórios  
✅ **Manutenção**: Menos código duplicado  

## 📝 Notas Técnicas

### Estado Compartilhado

O componente Reports.js agora gerencia:
- Templates padrão (disponibilidade, problemas, IA, recursos)
- Templates personalizados (10 novos templates)
- Relatórios salvos pelo usuário
- Dados de relatórios gerados

### Renderização Condicional

```javascript
const renderReport = () => {
  // Se tem estrutura de relatório personalizado
  if (reportData.data && reportData.data.rows) {
    return renderCustomReport(reportData);
  }
  
  // Senão, renderiza relatório padrão
  if (selectedReport.startsWith('availability_')) {
    return renderAvailabilityReport(reportData);
  }
  // ... outros tipos
};
```

### Formatação de Dados

- Datas formatadas para pt-BR
- Status com badges coloridos
- Booleanos com ✓/✗
- Valores nulos como "-"

## 🐛 Troubleshooting

### Não vejo a seção "Relatórios Personalizados"

1. Verifique se a migração foi executada
2. Verifique se a API foi reiniciada
3. Limpe o cache do navegador (Ctrl+Shift+R)
4. Verifique o console do navegador por erros

### Erro ao gerar relatório

1. Verifique se há dados no período selecionado
2. Verifique se os servidores estão ativos
3. Verifique os logs da API: `docker logs coruja-api`

### Relatório vazio

- Normal se não houver dados no período
- Tente ajustar filtros (futuro)
- Verifique se há incidentes/servidores cadastrados

## 🚀 Próximos Passos

### Melhorias Futuras

- [ ] Adicionar filtros editáveis na interface
- [ ] Adicionar seletor de colunas
- [ ] Adicionar botão "Salvar Relatório"
- [ ] Adicionar botão "Exportar CSV"
- [ ] Adicionar gráficos
- [ ] Adicionar comparação entre períodos

---

**Data**: 26 de Fevereiro de 2026  
**Status**: ✅ Integrado com Sucesso  
**Localização**: Dentro de /reports (mesma URL)
