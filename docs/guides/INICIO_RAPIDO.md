# 🚀 Início Rápido - Coruja Monitor

## Acesso ao Sistema

```
URL: http://localhost:3000
Login: admin@coruja.com
Senha: admin123
```

---

## 📋 Menu Principal

### 🏠 Dashboard
- Visão geral do sistema
- 5 cards de status: Servidores, Sensores, Incidentes, Críticos, Verificado pela TI
- Incidentes recentes
- Clique nos cards para navegar

### 🏢 Empresas
- Gerenciar empresas/tenants
- Adicionar probes por empresa
- Tokens de autenticação

### 🖥️ Servidores
- Lista de servidores monitorados
- Visualização em árvore ou lista
- Sensores por servidor
- **NOVO:** Badge "✓ Verificado pela TI" em sensores reconhecidos

### 📡 Sensores
- Todos os sensores do sistema
- 6 filtros: Total, OK, Aviso, Crítico, **Verificado pela TI**, Desconhecido
- Clique no sensor para ir ao servidor

### 🚨 Incidentes (NOVO)
- Todos os incidentes do sistema
- Filtros: Abertos, Críticos, Avisos, Resolvidos
- Tabela completa com detalhes
- Modal com análise da IA

### 📊 Relatórios
- Relatórios executivos de CPU e Memória
- Gráficos de evolução
- Análise de sizing
- Recomendações estratégicas

### 👥 Usuários
- Gerenciar usuários do sistema
- 3 roles: Admin, Técnico, Visualizador
- Permissões por role

### ⚙️ Configurações
- Integrações de notificação
- Ferramentas administrativas
- Configurações avançadas

---

## 🔥 Fluxo: Sensor Crítico → Reconhecimento

### 1. Identificar Sensor Crítico

**Onde:** Dashboard ou Servidores

1. Vá para "Servidores" no menu
2. Selecione um servidor
3. Localize sensor com barra VERMELHA (crítico)

**Indicadores:**
- 🔥 Barra vermelha "CRITICAL"
- Valor acima do threshold crítico
- Sem badge "Verificado pela TI"

### 2. Reconhecer o Sensor

**Ação:** Marcar como "Em Análise"

1. Clique no ícone 🔍 no sensor crítico
2. Modal "Detalhes do Sensor" abre
3. Role até "Notas do Técnico"
4. Preencha:
   - **Status:** 🔍 Em Análise
   - **Nota:** "Verificando causa do problema. Servidor sob análise."
5. Clique "Adicionar Nota"

**Resultado:**
- ✅ Badge verde "✓ Verificado pela TI" aparece
- 🔵 Barra muda para azul "EM ANÁLISE"
- 📝 Preview da nota no rodapé
- Sensor SAI de "Crítico"
- Sensor VAI para "Verificado pela TI"
- Alertas e ligações SUPRIMIDOS

### 3. Trabalhar no Problema

**Ação:** Adicionar notas de progresso

1. Continue adicionando notas conforme trabalha
2. Mantenha status "Em Análise" ou "Verificado"
3. Equipe vê suas atualizações em tempo real

### 4. Resolver o Problema

**Ação:** Marcar como "Resolvido"

1. Clique em 🔍 novamente
2. Adicione nota final:
   - **Status:** 🎉 Resolvido
   - **Nota:** "Problema resolvido. Serviço reiniciado com sucesso."
3. Clique "Adicionar Nota"

**Resultado:**
- Badge "Verificado pela TI" DESAPARECE
- Barra volta para cor normal
- Sensor volta para contagem normal
- Alertas e ligações REATIVADOS

---

## 🚨 Fluxo: Gerenciar Incidentes

### 1. Ver Incidentes

**Onde:** Menu "Incidentes"

1. Clique em "Incidentes" no menu
2. Veja tabela de todos os incidentes
3. Cards de resumo no topo

**Informações:**
- Severidade (🔥 Crítico, ⚠️ Aviso)
- Status (🚨 Aberto, ✓ Reconhecido, ✅ Resolvido)
- Servidor e Sensor
- Descrição inteligente
- Duração
- Data de criação

### 2. Filtrar Incidentes

**Filtros Disponíveis:**
- Todos
- Abertos
- Reconhecidos
- Críticos
- Avisos

**Como usar:**
1. Clique nos cards de resumo OU
2. Clique nos botões de filtro
3. Combine filtros (ex: Críticos + Abertos)

### 3. Ver Detalhes

**Ação:** Clicar em 🔍

1. Clique no botão 🔍 em qualquer incidente
2. Modal abre com:
   - Informações básicas
   - Descrição completa
   - 🤖 Análise da IA (causa raiz)
   - 🔧 Logs de remediação
3. Veja tentativas de auto-healing

### 4. Reconhecer Incidente

**Ação:** Clicar em ✓

1. No modal de detalhes, clique "Reconhecer Incidente"
2. Sistema navega para o servidor
3. Adicione nota no sensor
4. Incidente é marcado como reconhecido

---

## 📊 Filtro "Verificado pela TI"

### Dashboard

**Onde:** Seção "Status de Saúde"

1. Veja 5 cards de status
2. Card azul "Verificado pela TI" mostra contagem
3. Clique no card para filtrar sensores

### Página "Todos os Sensores"

**Onde:** Menu "Sensores"

1. Veja 6 cards de filtro
2. Card "Verificado pela TI" (azul com ícone ✓)
3. Clique para ver apenas sensores reconhecidos

**O que você vê:**
- Apenas sensores com badge verde
- Todos com barra azul "EM ANÁLISE"
- Preview da última nota
- Tooltip ao passar mouse

---

## 🎯 Dicas Rápidas

### Para Técnicos

✅ **Sempre reconheça sensores críticos ao começar a trabalhar**
- Evita ligações repetidas
- Comunica status para equipe
- Documenta suas ações

✅ **Adicione notas detalhadas**
- Descreva o que está fazendo
- Atualize conforme progride
- Facilita handover

✅ **Marque como "Resolvido" quando terminar**
- Reativa monitoramento
- Fecha o ciclo
- Gera métricas

### Para Gestores

✅ **Monitore "Verificado pela TI" no Dashboard**
- Veja quantos sensores estão sendo trabalhados
- Identifique gargalos
- Distribua carga de trabalho

✅ **Use página de Incidentes**
- Visão completa de problemas
- Filtre por severidade
- Acompanhe tempo de resolução

✅ **Revise Relatórios Executivos**
- Análise de CPU e Memória
- Recomendações de sizing
- Análise de custos

---

## 🔧 Atalhos Úteis

### Navegação Rápida

- **Dashboard → Sensor Crítico:** Clique no card "Críticos"
- **Dashboard → Verificado TI:** Clique no card "Verificado pela TI"
- **Sensor → Servidor:** Clique no sensor em "Todos os Sensores"
- **Incidente → Servidor:** Clique em ✓ (Reconhecer)

### Ações Rápidas

- **Reconhecer Sensor:** 🔍 → Nota → "Em Análise"
- **Resolver Sensor:** 🔍 → Nota → "Resolvido"
- **Ver Detalhes:** 🔍 em qualquer sensor/incidente
- **Editar Sensor:** ✏️ no sensor

---

## 📱 Indicadores Visuais

### Cores de Status

| Cor | Significado | Onde |
|-----|-------------|------|
| 🟢 Verde | OK / Saudável | Sensores, Dashboard |
| 🟡 Amarelo | Aviso / Warning | Sensores, Incidentes |
| 🔴 Vermelho | Crítico | Sensores, Incidentes |
| 🔵 Azul | Verificado pela TI | Sensores reconhecidos |
| ⚪ Cinza | Desconhecido | Sensores sem dados |

### Ícones Importantes

| Ícone | Significado | Ação |
|-------|-------------|------|
| 🔍 | Ver detalhes | Abre modal |
| ✏️ | Editar | Edita sensor/servidor |
| × | Remover | Remove sensor |
| ✓ | Reconhecer | Marca como verificado |
| 📝 | Nota | Indica presença de nota |
| 🤖 | IA | Análise da IA disponível |
| 🔧 | Remediação | Tentativa de auto-healing |

### Badges

| Badge | Significado |
|-------|-------------|
| ✓ Verificado pela TI | Sensor reconhecido por técnico |
| 🚨 Aberto | Incidente aberto |
| ✓ Reconhecido | Incidente reconhecido |
| ✅ Resolvido | Incidente/sensor resolvido |
| 🔥 CRÍTICO | Severidade crítica |
| ⚠️ AVISO | Severidade aviso |

---

## ❓ Perguntas Frequentes

### Como sei se um sensor está sendo trabalhado?

Procure por:
- Badge verde "✓ Verificado pela TI"
- Barra azul "EM ANÁLISE"
- Preview de nota no rodapé
- Tooltip ao passar mouse

### Sensores reconhecidos geram alertas?

❌ NÃO! Quando um sensor é reconhecido:
- Alertas são SUPRIMIDOS
- Ligações são BLOQUEADAS
- Sistema entende que técnico está trabalhando

### Como voltar ao monitoramento normal?

Adicione nota com status "Resolvido":
- Badge desaparece
- Barra volta para cor normal
- Alertas e ligações REATIVADOS

### Onde vejo todos os sensores reconhecidos?

3 lugares:
1. Dashboard → Card "Verificado pela TI"
2. Sensores → Card "Verificado pela TI"
3. Servidores → Sensores com badge verde

### Como funcionam os incidentes?

Automático:
1. Sensor ultrapassa threshold
2. Worker cria incidente
3. Descrição inteligente gerada
4. Tenta auto-healing
5. Solicita análise da IA
6. Aparece em "Incidentes"

### Posso reconhecer múltiplos sensores?

✅ SIM! Adicione nota em cada sensor:
- Cada um terá seu badge
- Cada um terá sua nota
- Todos aparecem em "Verificado pela TI"

---

## 🆘 Suporte

### Problemas Comuns

**Badge não aparece:**
- Limpe cache: Ctrl+Shift+R
- Aguarde 10 segundos (auto-refresh)
- Verifique se nota foi salva

**Contagem não atualiza:**
- Aguarde 10 segundos
- Recarregue página (F5)
- Verifique logs da API

**Incidentes não aparecem:**
- Verifique se worker está rodando
- Veja logs: `docker logs coruja-worker`
- Aguarde 1 minuto (avaliação de thresholds)

### Comandos Úteis

```bash
# Ver status dos serviços
docker ps

# Ver logs
docker logs coruja-frontend --tail 50
docker logs coruja-api --tail 50
docker logs coruja-worker --tail 50

# Reiniciar serviços
docker compose restart frontend api worker

# Limpar cache do navegador
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

---

## 🎉 Pronto para Usar!

Sistema completo e funcionando. Acesse agora:

**http://localhost:3000**

Login: admin@coruja.com  
Senha: admin123

Boa monitoração! 🦉
