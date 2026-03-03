# Guia: Como Configurar Microsoft Teams - Passo a Passo

## Data: 25 de Fevereiro de 2026

## ⚠️ IMPORTANTE: Ordem Correta

Você DEVE seguir esta ordem:
1. ✅ Cole a Webhook URL
2. ✅ Marque "Ativado"
3. ✅ **CLIQUE EM "SALVAR CONFIGURAÇÕES"** (botão no final da página)
4. ✅ Depois clique em "Testar Mensagem"

**Se você testar ANTES de salvar, vai dar erro: "Notification config not found"**

---

## Passo 1: Criar Webhook no Teams

### 1.1 Abrir o Canal
1. Abra o Microsoft Teams
2. Vá até o canal onde quer receber alertas
3. Clique nos **3 pontos** ao lado do nome do canal
4. Selecione **"Conectores"** ou **"Connectors"**

### 1.2 Adicionar Incoming Webhook
1. Na lista de conectores, procure por **"Incoming Webhook"**
2. Clique em **"Configurar"** ou **"Configure"**
3. Dê um nome ao webhook (ex: "Coruja Monitor")
4. Opcionalmente, adicione uma imagem
5. Clique em **"Criar"** ou **"Create"**

### 1.3 Copiar a URL
1. O Teams vai gerar uma URL longa
2. **COPIE TODA A URL** (ela é bem grande!)
3. Exemplo de URL:
```
https://techbizfd.webhook.office.com/webhookb2/1fce8d39-1753-47cd-8927-c2b01053abfe@6731fa33-e076-4815-8003-ad91af58421f/IncomingWebhook/562933e89fc24e7dbcc4a78d340aec42/beb27b50-822b-4170-81d2-7d3f2d7c52ca/V2IImzFRxh4Jc4_ZGWpY_RdjSxpMNZUGArb2HqYmvLfVg1
```

---

## Passo 2: Configurar no Coruja Monitor

### 2.1 Acessar Configurações
1. Faça login no Coruja Monitor
2. Vá em **Configurações** (menu lateral)
3. Clique na aba **"Notificações"**

### 2.2 Configurar Microsoft Teams
1. Role até a seção **"Microsoft Teams"**
2. Cole a Webhook URL no campo
3. Marque o checkbox **"Ativado"**

### 2.3 SALVAR (PASSO CRÍTICO!)
1. Role até o **FINAL DA PÁGINA**
2. Clique no botão **"Salvar Configurações"**
3. Aguarde a mensagem: "Configurações de notificação salvas com sucesso!"

### 2.4 Testar
1. Agora sim, clique em **"Testar Mensagem"**
2. Vá até o canal do Teams
3. Você deve ver uma mensagem como:

```
🦉 Teste de Integração - Coruja Monitor
Teste de Notificação

Este é um teste de integração com Microsoft Teams. 
Se você está vendo esta mensagem, a integração está funcionando corretamente!

Tenant: Default
Usuário: admin@coruja.com
Data/Hora: 25/02/2026 14:30:00
Status: ✅ Integração Ativa

[Abrir Dashboard]
```

---

## Troubleshooting

### Erro: "Notification config not found"
**Causa:** Você tentou testar ANTES de salvar
**Solução:** 
1. Clique em "Salvar Configurações" no final da página
2. Aguarde confirmação
3. Depois clique em "Testar Mensagem"

### Erro: "Teams API error: 400"
**Causa:** Webhook URL inválida ou expirada
**Solução:**
1. Verifique se copiou a URL completa
2. Verifique se não tem espaços no início/fim
3. Se necessário, gere nova webhook no Teams

### Erro: "Teams not configured or disabled"
**Causa:** Checkbox "Ativado" não está marcado
**Solução:**
1. Marque o checkbox "Ativado"
2. Salve as configurações
3. Teste novamente

### Mensagem não aparece no Teams
**Causa:** Webhook pode estar desativado ou removido
**Solução:**
1. Vá no Teams → Canal → Conectores
2. Verifique se o webhook ainda existe
3. Se não existir, crie um novo

---

## Formato da Mensagem

As mensagens enviadas para o Teams incluem:

### Cabeçalho
- Emoji 🦉
- Título do alerta
- Cor baseada na severidade:
  - 🔴 Vermelho: Crítico
  - 🟡 Laranja: Aviso
  - 🔵 Azul: Informação
  - 🟢 Verde: Sucesso

### Corpo
- Subtítulo
- Data e hora
- Fatos importantes (tenant, usuário, servidor, sensor, etc.)
- Descrição detalhada

### Ações
- Botão "Abrir Dashboard" (link direto)

---

## Exemplo de Alerta Real

Quando um sensor ficar crítico, você receberá:

```
🦉 ALERTA CRÍTICO - CPU Alta
Servidor: DESKTOP-P9VGN04

Servidor: DESKTOP-P9VGN04
Sensor: CPU
Valor Atual: 98.5%
Limite Crítico: 95%
Status: 🔴 CRÍTICO
Data/Hora: 25/02/2026 14:35:22

O uso de CPU ultrapassou o limite crítico configurado.
Ação recomendada: Verificar processos em execução.

[Abrir Dashboard] [Ver Servidor] [Ver Incidente]
```

---

## Configurações Avançadas

### Múltiplos Canais
Você pode configurar webhooks diferentes para:
- Canal de Alertas Críticos
- Canal de Avisos
- Canal de Informações

Basta criar múltiplos webhooks e alternar entre eles.

### Filtrar por Severidade
No futuro, será possível configurar:
- Crítico → Canal #alertas-criticos
- Aviso → Canal #avisos
- Info → Canal #informacoes

### Horário de Notificações
Configure em "Ambientes" se quer receber:
- 24x7 (Produção)
- Horário comercial (Homologação/Dev)
- Personalizado

---

## Sua Webhook URL

Você configurou:
```
https://techbizfd.webhook.office.com/webhookb2/1fce8d39-1753-47cd-8927-c2b01053abfe@6731fa33-e076-4815-8003-ad91af58421f/IncomingWebhook/562933e89fc24e7dbcc4a78d340aec42/beb27b50-822b-4170-81d2-7d3f2d7c52ca/V2IImzFRxh4Jc4_ZGWpY_RdjSxpMNZUGArb2HqYmvLfVg1
```

**Lembre-se:**
1. Cole a URL
2. Marque "Ativado"
3. **SALVE AS CONFIGURAÇÕES**
4. Teste

---

## Checklist Final

- [ ] Webhook criado no Teams
- [ ] URL copiada completamente
- [ ] URL colada no Coruja Monitor
- [ ] Checkbox "Ativado" marcado
- [ ] **Botão "Salvar Configurações" clicado**
- [ ] Mensagem de sucesso recebida
- [ ] Botão "Testar Mensagem" clicado
- [ ] Mensagem apareceu no Teams

Se todos os itens estiverem marcados, sua integração está funcionando! ✅
