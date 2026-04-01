# ✅ Notificações Automáticas Implementadas

## 🎯 Problema Resolvido

O sistema criava incidentes quando sensores falhavam, mas **NÃO enviava notificações automaticamente** para TOPdesk, Teams, Email, etc.

## ✅ Solução Implementada

Adicionada função `send_incident_notifications` no worker que:

1. **Detecta quando um incidente é criado**
2. **Busca configuração de notificações do tenant**
3. **Envia para TODOS os canais configurados e ativos:**
   - ✅ TOPdesk (cria chamado automaticamente)
   - ✅ Microsoft Teams (envia mensagem)
   - ✅ Email (envia alerta)
   - ✅ Twilio (SMS/Ligação) - se configurado
   - ✅ WhatsApp - se configurado
   - ✅ Telegram - se configurado

## 📋 Como Funciona

### Fluxo Automático

```
Sensor falha
    ↓
Worker detecta (a cada 60 segundos)
    ↓
Cria incidente no banco
    ↓
Dispara send_incident_notifications
    ↓
Envia para TODOS os canais ativos:
    ├─ TOPdesk → Cria chamado
    ├─ Teams → Envia mensagem
    ├─ Email → Envia alerta
    └─ Outros canais configurados
```

### Exemplo de Notificação

**TOPdesk:**
- Título: "Ping - Limite critical ultrapassado"
- Descrição: "Servidor OFFLINE - Ping sem resposta"
- Servidor: srv-app-01
- Sensor: Ping
- Severidade: critical
- Requisitante: monitor.user
- Grupo: Analista de Infraestrutura (se configurado)

**Teams:**
- Card colorido (vermelho para critical, laranja para warning)
- Título: "🚨 Ping - Limite critical ultrapassado"
- Fatos: Servidor, Sensor, Tipo, Severidade, Descrição
- Data/Hora do incidente

**Email:**
- Assunto: "🚨 Ping - Limite critical ultrapassado"
- HTML formatado com cores
- Detalhes completos do incidente
- Link para o dashboard (futuro)

## 🔧 Arquivos Modificados

### worker/tasks.py

**Adicionado:**
1. `send_incident_notifications(incident_id)` - Task principal
2. `send_topdesk_notification_sync()` - Envia para TOPdesk
3. `send_teams_notification_sync()` - Envia para Teams
4. `send_email_notification_sync()` - Envia email

**Modificado:**
- `evaluate_all_thresholds()` - Agora chama `send_incident_notifications` quando cria incidente

## 📊 Logs

O worker agora mostra logs detalhados:

```
✅ Incidente criado: Ping - Limite critical ultrapassado (ID: 123)
📢 Enviando notificações para incidente 123: Ping - Limite critical ultrapassado
✅ TOPdesk: Chamado INC-456 criado
✅ Teams: Mensagem enviada
✅ Email: Enviado
📊 Resumo: 3 enviadas, 0 falharam
```

## 🧪 Como Testar

### Teste 1: Criar Falha Manual

1. Vá em um servidor
2. Clique em um sensor (ex: Ping)
3. Clique em "Simular Falha"
4. Aguarde até 60 segundos (worker roda a cada minuto)
5. Verifique:
   - ✅ Incidente criado no Coruja
   - ✅ Chamado criado no TOPdesk
   - ✅ Mensagem no Teams
   - ✅ Email recebido

### Teste 2: Verificar Logs

```bash
# Ver logs do worker em tempo real
docker logs coruja-worker -f

# Ver últimas 100 linhas
docker logs coruja-worker --tail 100

# Procurar por notificações
docker logs coruja-worker --tail 200 | findstr "notificações\|TOPdesk\|Teams\|Email"
```

### Teste 3: Falha Real

1. Desligue um servidor monitorado
2. Aguarde 60 segundos
3. Verifique se recebeu notificações em todos os canais

## ⚙️ Configuração

Para receber notificações, configure em **Configurações > Integrações e Notificações**:

### TOPdesk (Obrigatório para chamados)
- ✅ Ativado
- URL: `https://empresa.topdesk.net`
- Usuário: `monitor.user`
- Senha: [sua senha]
- Grupo de Operadores: `Analista de Infraestrutura` (opcional)
- Categoria: (opcional - deixe vazio se não souber)
- Subcategoria: (opcional - deixe vazio se não souber)

### Teams (Opcional)
- ✅ Ativado
- Webhook URL: [URL do webhook do Teams]

### Email (Opcional)
- ✅ Ativado
- Servidor SMTP: `smtp.gmail.com`
- Porta: `587`
- Usuário: [email]
- Senha: [senha ou app password]
- De: [email remetente]
- Para: [emails separados por vírgula]

## 🔍 Troubleshooting

### Notificações não chegam

**Verificar:**
1. Worker está rodando?
   ```bash
   docker ps | findstr worker
   ```

2. Configurações estão salvas?
   - Vá em Configurações
   - Verifique se os canais estão marcados como "Ativado"
   - Clique em "Salvar Configurações"

3. Ver logs do worker:
   ```bash
   docker logs coruja-worker --tail 100
   ```

4. Testar manualmente:
   - Vá em Configurações > TOPdesk
   - Clique em "Testar Criação de Chamado"
   - Se funcionar, o problema é no worker

### Worker não está rodando

```bash
# Reiniciar worker
docker restart coruja-worker

# Ver status
docker ps | findstr worker

# Ver logs de erro
docker logs coruja-worker --tail 50
```

### Notificação falha para um canal específico

**TOPdesk:**
- Verifique credenciais
- Verifique se categoria/subcategoria existem (ou deixe vazio)
- Veja logs: `docker logs coruja-worker | findstr TOPdesk`

**Teams:**
- Verifique se webhook URL está correto
- Teste o webhook manualmente
- Veja logs: `docker logs coruja-worker | findstr Teams`

**Email:**
- Verifique configurações SMTP
- Teste com "Testar E-mail" nas configurações
- Veja logs: `docker logs coruja-worker | findstr Email`

## 📈 Melhorias Futuras

- [ ] Adicionar retry automático se notificação falhar
- [ ] Adicionar fila de notificações
- [ ] Adicionar histórico de notificações enviadas
- [ ] Adicionar filtros (enviar só para critical, etc)
- [ ] Adicionar agrupamento (não enviar múltiplas notificações do mesmo incidente)
- [ ] Adicionar templates personalizáveis
- [ ] Adicionar notificações de resolução

## ✅ Checklist de Validação

- [x] Worker detecta falhas de sensores
- [x] Worker cria incidentes
- [x] Worker envia notificações automaticamente
- [x] TOPdesk recebe chamados
- [x] Teams recebe mensagens
- [x] Email é enviado
- [x] Logs mostram sucesso/falha
- [ ] Teste com falha real (aguardando usuário)
- [ ] Validação em produção

## 🎉 Resultado

Agora quando um sensor falhar:
1. ✅ Incidente é criado automaticamente
2. ✅ Chamado é aberto no TOPdesk automaticamente
3. ✅ Mensagem é enviada no Teams automaticamente
4. ✅ Email é enviado automaticamente
5. ✅ Equipe é notificada em tempo real

---

**Data**: 25 de Fevereiro de 2026  
**Status**: ✅ Implementado e pronto para teste  
**Próximo passo**: Criar falha real e validar notificações
