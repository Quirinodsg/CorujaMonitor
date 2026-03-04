# Notificação por E-mail - Implementada

## Resumo
Implementada notificação básica por e-mail via SMTP no Coruja Monitor.

## O Que Foi Implementado

### 1. Frontend (Settings.js)

#### Seção de E-mail (primeira integração):
- **Servidor SMTP**: Endereço do servidor (ex: smtp.gmail.com)
- **Porta SMTP**: Porta de conexão (587 para TLS, 465 para SSL)
- **Usuário SMTP**: Login para autenticação
- **Senha SMTP**: Senha do usuário
- **E-mail de Origem**: Remetente dos alertas
- **E-mails de Destino**: Lista de destinatários (separados por vírgula)
- **Usar TLS**: Checkbox para habilitar TLS/STARTTLS
- **Botão de Teste**: Envia e-mail de teste

### 2. Backend (notifications.py)

#### Função `send_email_notification()`:
- Envia e-mails via SMTP
- Suporta TLS (porta 587) e SSL (porta 465)
- Cria e-mails em formato HTML e texto plano
- Template HTML profissional com:
  - Header com logo do Coruja Monitor
  - Box de alerta colorido (vermelho para crítico, laranja para aviso)
  - Seção de detalhes
  - Botão para acessar dashboard
  - Footer com informações

#### Endpoint `POST /api/v1/notifications/test/email`:
- Testa configuração de e-mail
- Envia e-mail de teste formatado
- Retorna lista de destinatários
- Valida autenticação SMTP

### 3. Template de E-mail

#### Estrutura HTML:
```html
- Header azul escuro com logo
- Box de alerta (vermelho/laranja)
- Seção de detalhes em cinza claro
- Botão azul para dashboard
- Footer com copyright
```

#### Informações Incluídas:
- Assunto do alerta
- Descrição do problema
- Detalhes técnicos (servidor, sensor, valor, threshold)
- Link para dashboard
- Data/hora do envio

## Como Configurar

### Passo 1: Acessar Configurações
1. Vá em **Configurações > Integrações e Notificações**
2. Localize a seção **E-mail (SMTP)** (primeira da lista)
3. Ative o toggle

### Passo 2: Configurar SMTP

#### Gmail:
```
Servidor SMTP: smtp.gmail.com
Porta: 587
Usuário: seu-email@gmail.com
Senha: senha de app (não a senha normal)
Usar TLS: ✓ Marcado
```

**Importante**: Para Gmail, você precisa:
1. Ativar verificação em 2 etapas
2. Gerar uma "Senha de app" em https://myaccount.google.com/apppasswords
3. Usar a senha de app no campo "Senha SMTP"

#### Outlook/Office 365:
```
Servidor SMTP: smtp.office365.com
Porta: 587
Usuário: seu-email@empresa.com
Senha: sua senha
Usar TLS: ✓ Marcado
```

#### Servidor SMTP Próprio:
```
Servidor SMTP: mail.empresa.com
Porta: 587 (TLS) ou 465 (SSL)
Usuário: monitor@empresa.com
Senha: senha do usuário
Usar TLS: ✓ Marcado (587) ou ✗ Desmarcado (465)
```

### Passo 3: Configurar Destinatários
```
E-mail de Origem: coruja-monitor@empresa.com
E-mails de Destino: ti@empresa.com, suporte@empresa.com, admin@empresa.com
```

### Passo 4: Testar
1. Clique em **Testar E-mail**
2. Aguarde confirmação
3. Verifique caixa de entrada dos destinatários
4. Se não chegou, verifique spam/lixo eletrônico

### Passo 5: Salvar
Clique em **Salvar Configurações**

## Exemplo de E-mail de Teste

```
De: coruja-monitor@empresa.com
Para: ti@empresa.com, suporte@empresa.com
Assunto: ✅ Teste de Integração - Coruja Monitor

[HTML formatado com:]
- Header azul com logo
- Mensagem de teste
- Informações da configuração
- Data/hora do teste
- Próximos passos
```

## Exemplo de E-mail de Alerta

```
De: coruja-monitor@empresa.com
Para: ti@empresa.com
Assunto: 🔥 CRÍTICO: CPU alta - SERVIDOR-WEB-01

[HTML formatado com:]
- Header azul
- Box vermelho de alerta crítico
- Detalhes:
  * Servidor: SERVIDOR-WEB-01 (192.168.1.100)
  * Sensor: cpu_usage
  * Valor atual: 98.5%
  * Threshold crítico: 95%
  * Duração: 15 minutos
- Botão "Ver no Dashboard"
- Footer
```

## Configurações Comuns de SMTP

### Provedores Populares:

| Provedor | Servidor | Porta TLS | Porta SSL |
|----------|----------|-----------|-----------|
| Gmail | smtp.gmail.com | 587 | 465 |
| Outlook | smtp.office365.com | 587 | 465 |
| Yahoo | smtp.mail.yahoo.com | 587 | 465 |
| SendGrid | smtp.sendgrid.net | 587 | 465 |
| Mailgun | smtp.mailgun.org | 587 | 465 |
| Amazon SES | email-smtp.us-east-1.amazonaws.com | 587 | 465 |

### Portas SMTP:
- **587**: STARTTLS (recomendado) - Marque "Usar TLS"
- **465**: SSL/TLS - Desmarque "Usar TLS"
- **25**: Sem criptografia (não recomendado)

## Troubleshooting

### Erro: "Falha na autenticação SMTP"
**Causa**: Usuário ou senha incorretos
**Solução**:
- Verifique usuário e senha
- Para Gmail, use senha de app
- Para Office 365, verifique se autenticação moderna está habilitada

### Erro: "Connection refused"
**Causa**: Servidor ou porta incorretos
**Solução**:
- Verifique endereço do servidor
- Confirme porta (587 ou 465)
- Verifique firewall

### Erro: "TLS/SSL error"
**Causa**: Configuração TLS incorreta
**Solução**:
- Porta 587: Marque "Usar TLS"
- Porta 465: Desmarque "Usar TLS"

### E-mail vai para spam
**Causa**: Falta de autenticação SPF/DKIM
**Solução**:
- Configure SPF no DNS: `v=spf1 ip4:SEU_IP ~all`
- Configure DKIM se possível
- Adicione remetente aos contatos confiáveis
- Use domínio próprio ao invés de Gmail/Outlook

### E-mail não chega
**Causa**: Bloqueio ou filtro
**Solução**:
- Verifique pasta de spam
- Verifique logs do servidor SMTP
- Teste com outro destinatário
- Verifique se servidor SMTP está acessível

## Boas Práticas

### Segurança:
1. Use TLS/SSL sempre que possível
2. Não use senha pessoal, crie senha de app
3. Use conta dedicada para monitoramento
4. Rotacione senhas periodicamente

### Confiabilidade:
1. Use servidor SMTP confiável (SendGrid, Mailgun, etc)
2. Configure SPF e DKIM no DNS
3. Monitore taxa de entrega
4. Mantenha lista de destinatários atualizada

### Performance:
1. Limite número de destinatários (máx 10-20)
2. Use grupos de e-mail ao invés de múltiplos destinatários
3. Configure retry em caso de falha
4. Não envie e-mails para cada métrica, apenas incidentes

### Conteúdo:
1. Assunto claro e objetivo
2. Inclua severidade no assunto (🔥 CRÍTICO, ⚠️ AVISO)
3. Detalhes técnicos no corpo
4. Link para dashboard
5. Ação recomendada

## Integração com Incidentes

Quando um incidente crítico ocorre:
1. Sistema verifica se e-mail está habilitado
2. Monta e-mail com detalhes do incidente
3. Envia para todos os destinatários configurados
4. Registra envio no log
5. Em caso de falha, tenta novamente (retry)

## Próximos Passos

### Melhorias Futuras:
1. **Templates personalizáveis**: Permitir customizar HTML
2. **Agrupamento**: Agrupar múltiplos alertas em um e-mail
3. **Throttling**: Limitar frequência de envio
4. **Digest**: E-mail resumo diário/semanal
5. **Anexos**: Incluir gráficos e relatórios
6. **Priorização**: Enviar apenas alertas críticos por e-mail

### Integrações:
- E-mail já funciona em conjunto com:
  - Twilio (ligações)
  - Teams (mensagens)
  - WhatsApp (mensagens)
  - Telegram (mensagens)
  - TOPdesk (chamados)
  - GLPI (tickets)

## Arquivos Modificados

- `frontend/src/components/Settings.js` - Interface de configuração
- `api/routers/notifications.py` - Backend e envio de e-mail

## Teste Rápido

```bash
# 1. Configure e-mail na interface
# 2. Clique em "Testar E-mail"
# 3. Verifique caixa de entrada
# 4. Se funcionou, salve as configurações
```

## Suporte

Para problemas com e-mail:
1. Verifique logs da API: `docker logs coruja-api`
2. Teste conexão SMTP manualmente
3. Valide credenciais no provedor
4. Consulte documentação do provedor SMTP
