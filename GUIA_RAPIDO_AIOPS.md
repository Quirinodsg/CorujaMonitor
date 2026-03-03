# 🚀 GUIA RÁPIDO - AIOps em 5 Minutos

**Sistema 100% funcional e testado!** ✅

---

## 🎯 O QUE É O AIOPS?

Inteligência Artificial para Operações de TI que:
- 🔍 Detecta anomalias ANTES de virarem problemas
- 🔗 Correlaciona incidentes relacionados
- 🎯 Identifica causa raiz automaticamente
- 📋 Cria planos de ação prontos para executar

---

## ⚡ INÍCIO RÁPIDO

### 1. Acesse o Dashboard
```
Menu → AIOps → Overview
```

### 2. Execute Sua Primeira Análise

**Opção A: Detectar Anomalias**
1. Clique na aba "Detecção de Anomalias"
2. Selecione um sensor (ex: PING, Disco C, CPU)
3. Clique em "Detectar Anomalias"
4. Veja resultado em < 1 segundo

**Opção B: Correlacionar Eventos**
1. Clique na aba "Correlação de Eventos"
2. Clique em "Correlacionar Eventos"
3. Sistema analisa últimos 30 minutos
4. Veja grupos de incidentes relacionados

**Opção C: Analisar Causa Raiz**
1. Clique na aba "Análise de Causa Raiz"
2. Digite ID de um incidente (ex: 94)
3. Clique em "Analisar Causa Raiz"
4. Veja sintomas, timeline e causa raiz

**Opção D: Criar Plano de Ação**
1. Após análise RCA
2. Clique em "Criar Plano de Ação"
3. Veja ações imediatas, curto e longo prazo
4. Execute comandos sugeridos

---

## 📊 ENTENDENDO O DASHBOARD

### Cards Principais

**🔍 Anomalias Detectadas**
- Mostra quantas anomalias foram encontradas
- Clique para ver detalhes
- Verde = Normal | Vermelho = Anomalia

**🔗 Eventos Correlacionados**
- Mostra grupos de incidentes relacionados
- Clique para ver padrões identificados
- Ajuda a entender problemas sistêmicos

**📋 Planos de Ação**
- Mostra planos criados automaticamente
- Clique para ver ações detalhadas
- Comandos prontos para executar

**⚡ Ações Automatizadas**
- Mostra quantas ações podem ser automatizadas
- Clique para ver quais ações
- Sistema pode executar sozinho

### Atividade Recente
- Últimas análises executadas
- Clique em qualquer item para ver detalhes
- Atualiza em tempo real

---

## 🔍 DETECÇÃO DE ANOMALIAS

### O que faz?
Analisa métricas e detecta comportamentos anormais usando:
- **Z-score:** Detecta valores fora do padrão estatístico
- **Média Móvel:** Detecta mudanças de tendência
- **Taxa de Mudança:** Detecta spikes súbitos

### Como usar?
1. Selecione um sensor
2. Clique em "Detectar Anomalias"
3. Sistema analisa últimas 24 horas
4. Veja resultado:
   - ✅ Normal: Tudo OK
   - ⚠️ Anomalia: Comportamento anormal detectado

### Exemplo de Resultado
```
Sensor: PING
Anomalia detectada: SIM
Confiança: 95%
Total de anomalias: 3
Recomendação: "Investigar causa raiz da anomalia"

Detalhes:
- Valor: 150ms (normal: 20-50ms)
- Método: Z-score
- Z-score: 3.5 (muito alto)
```

---

## 🔗 CORRELAÇÃO DE EVENTOS

### O que faz?
Agrupa incidentes relacionados para identificar:
- Problemas sistêmicos
- Falhas em cascata
- Servidores afetados juntos
- Padrões temporais

### Como usar?
1. Clique em "Correlacionar Eventos"
2. Sistema analisa últimos 30 minutos
3. Veja grupos identificados
4. Entenda padrão (temporal, espacial, cascata)

### Exemplo de Resultado
```
Correlação encontrada: SIM
Total de grupos: 2

Grupo 1:
- Incidentes: 3
- Tipo: Falha em cascata
- Servidores: SRV-01, SRV-02
- Padrão: Disco cheio → SQL parou → CPU alta

Grupo 2:
- Incidentes: 2
- Tipo: Temporal
- Servidores: SRV-03, SRV-04
- Padrão: Ambos falharam ao mesmo tempo
```

---

## 🎯 ANÁLISE DE CAUSA RAIZ (RCA)

### O que faz?
Identifica a causa raiz de um incidente analisando:
- Sintomas detectados
- Timeline de eventos
- Dependências
- Padrões conhecidos (109 na base)

### Como usar?
1. Digite ID do incidente
2. Clique em "Analisar Causa Raiz"
3. Veja análise completa:
   - Causa raiz identificada
   - Confiança da análise
   - Sintomas detectados
   - Timeline de eventos
   - Fatores contribuintes

### Exemplo de Resultado
```
Incidente: Memória em 95%
Causa raiz: "Memory leak detectado"
Confiança: 85%

Sintomas:
- Crescimento gradual nas últimas 2 horas
- Memória não sendo liberada
- Processo específico consumindo

Timeline:
10:00 - Memória em 60% (normal)
10:30 - Memória em 75% (subindo)
11:00 - Memória em 90% (crítico)
11:15 - Memória em 95% (incidente criado)

Fatores Contribuintes:
- Aplicação com memory leak
- Sem restart automático
- Monitoramento não alertou antes
```

---

## 📋 PLANOS DE AÇÃO

### O que faz?
Cria plano estruturado para resolver incidente com:
- **Ações Imediatas:** Parar o sangramento (1-5 min)
- **Ações Curto Prazo:** Corrigir o problema (5-30 min)
- **Ações Longo Prazo:** Prevenir recorrência (horas/dias)

### Como usar?
1. Após análise RCA
2. Clique em "Criar Plano de Ação"
3. Veja plano completo
4. Execute ações na ordem de prioridade

### Exemplo de Resultado
```
Plano: AP-94-20260226183837
Severidade: critical
Tempo estimado: 15 minutos

AÇÕES IMEDIATAS (1-5 min):
1. Verificar status do docker
   Comando: docker ps
   Risco: Baixo
   Tempo: 1 min

2. Identificar processo com alto CPU
   Comando: Get-Process | Sort CPU -Desc
   Risco: Baixo
   Tempo: 1 min

AÇÕES CURTO PRAZO (5-30 min):
1. Reiniciar container problemático
   Comando: docker restart <container>
   Risco: Médio
   Tempo: 5 min
   ⚠️ Requer aprovação

AÇÕES LONGO PRAZO (horas/dias):
1. Ajustar thresholds
   Tempo: 30 min

2. Implementar monitoramento proativo
   Tempo: 2 horas
```

---

## 💡 DICAS E TRUQUES

### Para Melhores Resultados

**1. Deixe dados acumularem**
- Mínimo: 10 métricas por sensor
- Ideal: 2-24 horas de histórico
- Quanto mais dados, melhor a análise

**2. Execute análises regularmente**
- Detecção de anomalias: Diariamente
- Correlação: Quando houver múltiplos incidentes
- RCA: Para cada incidente importante

**3. Use a base de conhecimento**
- 109 problemas catalogados
- 29 com auto-resolução
- Taxa de sucesso: 84.88%

**4. Siga os planos de ação**
- Ações estão priorizadas
- Comandos prontos para executar
- Níveis de risco indicados

### Atalhos Úteis

**Dashboard Overview:**
- Clique nos cards para ir direto para a aba
- Clique na atividade recente para ver detalhes
- Use "Ações Rápidas" para acesso rápido

**Análises:**
- Resultados aparecem imediatamente
- Histórico mantido por 24 horas
- Pode executar múltiplas análises

---

## 🔧 TROUBLESHOOTING

### Dashboard zerado?
✅ **Normal!** Dashboard mostra últimas 24 horas.
- Execute uma análise
- Dashboard atualiza automaticamente

### "Insufficient data"?
✅ **Normal!** Sensor precisa de mais métricas.
- Aguarde probe coletar mais dados
- Mínimo: 10 métricas
- Ou use outro sensor

### "No incidents found"?
✅ **Normal!** Não há incidentes para analisar.
- Sistema está saudável
- Ou use Ferramentas de Teste para simular

### Análise demorada?
✅ **Verifique:**
- Detecção de anomalias: < 1 segundo
- Correlação: < 2 segundos
- RCA: < 3 segundos
- Se demorar mais, verifique logs

---

## 📚 DOCUMENTAÇÃO COMPLETA

Para mais detalhes, consulte:

- `AIOPS_AUTOMATICO_EXPLICADO.md` - Como funciona automaticamente
- `AIOPS_IA_HIBRIDA_EXPLICADA.md` - Arquitetura de IA
- `AIOPS_TESTADO_FUNCIONANDO_26FEV.md` - Testes e validação
- `BASE_CONHECIMENTO_80_ITENS_COMPLETA.md` - Base de conhecimento

---

## 🎯 CHECKLIST DE PRIMEIRO USO

- [ ] Acessei o dashboard AIOps
- [ ] Executei detecção de anomalias em um sensor
- [ ] Executei correlação de eventos
- [ ] Analisei causa raiz de um incidente
- [ ] Criei um plano de ação
- [ ] Vi os resultados no dashboard
- [ ] Entendi como funciona

---

## 🦉 SUPORTE

**Sistema 100% funcional e testado!**

Se tiver dúvidas:
1. Consulte a documentação
2. Execute `testar_aiops_completo.ps1`
3. Verifique logs: `docker logs coruja-api`

**Bom uso do AIOps!** 🚀
