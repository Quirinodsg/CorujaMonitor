# Interface AIOps Implementada - Coruja Monitor

## Data: 18/02/2026

## Resumo

Criada interface completa para o sistema AIOps com dashboard interativo mostrando todas as ações da IA, anomalias detectadas, correlações de eventos, análises de causa raiz e planos de ação.

## Arquivos Criados

### 1. Componente React
**Arquivo**: `frontend/src/components/AIOps.js`
- Componente completo com 5 abas
- 600+ linhas de código
- Integração total com API AIOps

### 2. Estilos CSS
**Arquivo**: `frontend/src/components/AIOps.css`
- 800+ linhas de CSS
- Design moderno e responsivo
- Gradientes e animações

### 3. Integração
- Adicionado ao `Sidebar.js` (ícone 🤖)
- Adicionado ao `MainLayout.js`
- Rota: `/aiops`

## Funcionalidades da Interface

### 1. Overview (Dashboard Principal)

**Cards de Estatísticas**:
- 🔍 Anomalias Detectadas (últimas 24h)
- 🔗 Eventos Correlacionados (grupos)
- 📋 Planos de Ação (criados)
- ⚡ Ações Automatizadas (executadas)

**Ações Rápidas**:
- Botão para Detectar Anomalias
- Botão para Correlacionar Eventos
- Botão para Análise de Causa Raiz

**Atividade Recente**:
- Lista de últimas análises realizadas
- Timestamp de cada ação
- Resultados resumidos

### 2. Detecção de Anomalias

**Funcionalidades**:
- Seletor de sensor (dropdown com todos os sensores)
- Botão "Detectar Anomalias"
- Lookback de 24 horas

**Resultados Exibidos**:
- Status: ANOMALIA DETECTADA ou NORMAL
- Nível de confiança (%)
- Total de anomalias encontradas
- Recomendações da IA
- Detalhes de cada anomalia:
  - Valor
  - Método de detecção
  - Z-score (quando aplicável)

**Visual**:
- Cards coloridos (vermelho para anomalia, verde para normal)
- Badges de status
- Lista de anomalias com detalhes

### 3. Correlação de Eventos

**Funcionalidades**:
- Botão "Correlacionar Eventos"
- Janela temporal: 30 minutos
- Filtro de severidade: critical e warning

**Resultados Exibidos**:
- Total de grupos correlacionados
- Padrão identificado:
  - `infrastructure_wide` - Problema sistêmico
  - `cascading_failure` - Falha em cascata
  - `isolated_incidents` - Incidentes isolados
- Total de incidentes correlacionados
- Servidores afetados

**Detalhes por Grupo**:
- Número de incidentes
- Tipo de correlação (temporal/espacial)
- Duração (segundos)
- Lista de servidores afetados
- Severidade do grupo

**Visual**:
- Cards laranja para correlações
- Badges de severidade
- Sub-cards para cada grupo

### 4. Análise de Causa Raiz (RCA)

**Funcionalidades**:
- Input para ID do incidente
- Botão "Analisar Causa Raiz"
- Análise completa multi-dimensional

**Resultados Exibidos**:

**Causa Raiz**:
- Card destacado com gradiente
- Descrição completa da causa
- Badge de confiança

**Sintomas Detectados**:
- Lista de sintomas
- Tipo (primary, trend, spike)
- Descrição
- Severidade

**Timeline de Eventos**:
- Linha do tempo visual
- Marcadores coloridos
- Eventos ordenados cronologicamente
- Mudanças em métricas
- Incidentes relacionados

**Fatores Contribuintes**:
- Lista de fatores que contribuíram
- Análise de dependências
- Contexto adicional

**Ações**:
- Botão "Criar Plano de Ação"
- Integração direta com geração de planos

**Visual**:
- Layout em grid responsivo
- Timeline estilo moderno
- Cards coloridos por tipo de sintoma
- Gradientes e sombras

### 5. Planos de Ação

**Funcionalidades**:
- Lista de todos os planos criados
- Visualização completa de cada plano
- Organização por prioridade

**Estrutura do Plano**:

**Cabeçalho**:
- ID do plano
- ID do incidente
- Severidade (badge colorido)
- Tempo estimado de resolução
- Badge de automação disponível

**Ações Imediatas** (🚨):
- Objetivo: Parar o sangramento
- Tempo: 1-5 minutos
- Prioridade alta
- Comandos prontos para execução
- Indicador de automação
- Nível de risco

**Ações de Curto Prazo** (🔧):
- Objetivo: Corrigir o problema
- Tempo: 5-30 minutos
- Comandos PowerShell/Bash
- Indicador de aprovação necessária
- Nível de risco

**Ações de Longo Prazo** (📈):
- Objetivo: Prevenir recorrência
- Tempo: Horas/dias
- Ações estratégicas
- Melhorias de processo

**Visual**:
- Cards grandes e detalhados
- Cores por tipo de ação:
  - Vermelho: Imediatas
  - Laranja: Curto prazo
  - Azul: Longo prazo
- Comandos em terminal (fundo preto, texto verde)
- Badges de prioridade, risco e automação
- Layout responsivo

## Design e UX

### Paleta de Cores

**Gradientes Principais**:
- Roxo: `#667eea` → `#764ba2`
- Rosa: `#f093fb` → `#f5576c`
- Azul: `#4facfe` → `#00f2fe`

**Status**:
- Sucesso: `#4caf50` (verde)
- Aviso: `#ff9800` (laranja)
- Crítico: `#f44336` (vermelho)
- Info: `#2196f3` (azul)

### Componentes Visuais

**Cards**:
- Bordas arredondadas (12px)
- Sombras suaves
- Hover effects (elevação)
- Transições suaves (0.3s)

**Badges**:
- Pequenos e coloridos
- Texto uppercase
- Padding consistente
- Cores semânticas

**Botões**:
- Gradientes vibrantes
- Hover com elevação
- Estados disabled
- Ícones emoji

**Timeline**:
- Linha vertical
- Marcadores circulares
- Cards conectados
- Animações suaves

### Responsividade

**Desktop** (> 768px):
- Grid de 2-4 colunas
- Sidebar fixa
- Cards lado a lado

**Mobile** (< 768px):
- Grid de 1 coluna
- Tabs em coluna
- Cards empilhados
- Botões full-width

## Integração com API

### Endpoints Utilizados

```javascript
// Detecção de Anomalias
POST /api/v1/aiops/anomaly-detection
Body: { sensor_id, lookback_hours }

// Correlação de Eventos
POST /api/v1/aiops/event-correlation
Body: { time_window_minutes, severity_filter }

// Análise de Causa Raiz
POST /api/v1/aiops/root-cause-analysis
Body: { incident_id }

// Criar Plano de Ação
POST /api/v1/aiops/action-plan/{incident_id}
Query: include_correlation=true

// Listar Sensores
GET /api/v1/sensors/
```

### Estado da Aplicação

**Estados Gerenciados**:
- `activeTab`: Aba atual
- `loading`: Estado de carregamento
- `anomalies`: Lista de anomalias detectadas
- `correlations`: Lista de correlações
- `actionPlans`: Lista de planos de ação
- `sensors`: Lista de sensores disponíveis
- `selectedSensor`: Sensor selecionado
- `selectedIncident`: Incidente selecionado
- `rcaResult`: Resultado da RCA
- `stats`: Estatísticas do dashboard

### Tratamento de Erros

- Try/catch em todas as chamadas API
- Alerts informativos para o usuário
- Mensagens de erro detalhadas
- Estados de loading

## Fluxo de Uso

### Cenário 1: Detectar Anomalia

1. Usuário clica em "AIOps" no sidebar
2. Vai para aba "Detecção de Anomalias"
3. Seleciona um sensor no dropdown
4. Clica em "Detectar Anomalias"
5. Sistema analisa últimas 24 horas
6. Exibe resultado com confiança e recomendações
7. Resultado fica salvo na lista de atividades

### Cenário 2: Investigar Incidente

1. Usuário identifica incidente crítico
2. Vai para aba "Análise de Causa Raiz"
3. Digita ID do incidente
4. Clica em "Analisar Causa Raiz"
5. Sistema exibe:
   - Causa raiz identificada
   - Sintomas detectados
   - Timeline de eventos
   - Fatores contribuintes
6. Usuário clica em "Criar Plano de Ação"
7. Sistema gera plano estruturado
8. Usuário vai para aba "Planos de Ação"
9. Visualiza plano completo com comandos

### Cenário 3: Monitoramento Proativo

1. Usuário acessa Overview diariamente
2. Visualiza estatísticas:
   - Anomalias detectadas
   - Eventos correlacionados
   - Ações automatizadas
3. Revisa atividade recente
4. Identifica padrões
5. Toma ações preventivas

## Melhorias Futuras

### Fase 1 (Próxima Sprint)
- [ ] Gráficos de anomalias (Recharts)
- [ ] Exportar planos de ação (PDF)
- [ ] Filtros avançados
- [ ] Busca em resultados

### Fase 2 (Q2 2026)
- [ ] Execução automática de ações
- [ ] Aprovação de ações críticas
- [ ] Histórico completo
- [ ] Métricas de performance

### Fase 3 (Q3 2026)
- [ ] Dashboard em tempo real (WebSocket)
- [ ] Notificações push
- [ ] Integração com ChatOps
- [ ] Mobile app

## Testes

### Teste Manual

1. **Acessar AIOps**:
   - Login no sistema
   - Clicar em "🤖 AIOps" no sidebar
   - Verificar carregamento do dashboard

2. **Testar Detecção de Anomalias**:
   - Selecionar sensor
   - Clicar em "Detectar Anomalias"
   - Verificar resultado

3. **Testar Correlação**:
   - Clicar em "Correlacionar Eventos"
   - Verificar grupos formados

4. **Testar RCA**:
   - Digitar ID de incidente
   - Clicar em "Analisar Causa Raiz"
   - Verificar timeline e sintomas

5. **Testar Plano de Ação**:
   - Criar plano a partir de RCA
   - Verificar ações geradas
   - Verificar comandos

## Comandos

```bash
# Reiniciar frontend
docker-compose restart frontend

# Ver logs
docker logs coruja-frontend --tail 50

# Verificar compilação
docker exec coruja-frontend npm run build
```

## Conclusão

Interface AIOps completa implementada com sucesso! O sistema agora possui uma interface visual moderna e intuitiva para todas as capacidades de IA, permitindo que os usuários:

- Monitorem atividades da IA em tempo real
- Detectem anomalias proativamente
- Investiguem incidentes com RCA
- Criem e executem planos de ação estruturados
- Visualizem correlações de eventos

**Status**: ✅ IMPLEMENTADO E FUNCIONAL
**Versão**: 1.0.0
**Data**: 18/02/2026
