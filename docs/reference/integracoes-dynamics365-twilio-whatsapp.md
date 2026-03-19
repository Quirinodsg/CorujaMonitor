# 🔌 Integrações: Dynamics 365, Twilio e WhatsApp

## 📋 Índice

- [Microsoft Dynamics 365](#microsoft-dynamics-365)
- [Twilio (SMS)](#twilio-sms)
- [WhatsApp via Twilio](#whatsapp-via-twilio)
- [Configuração no Coruja Monitor](#configuração-no-coruja-monitor)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)

---

## 🏢 Microsoft Dynamics 365

### Visão Geral

Integração completa com Microsoft Dynamics 365 para criação automática de incidentes/casos quando alertas são detectados pelo Coruja Monitor.

### Pré-requisitos

1. **Dynamics 365 Online** (versão 9.0 ou superior)
2. **Azure Active Directory** com aplicativo registrado
3. **Permissões necessárias**:
   - Dynamics CRM API access
   - Create incidents/cases
   - Read/Write permissions

### Configuração no Azure AD

#### Passo 1: Registrar Aplicativo

1. Acesse o [Azure Portal](https://portal.azure.com)
2. Navegue para **Azure Active Directory** → **App registrations**
3. Clique em **New registration**
4. Preencha:
   - **Name**: Coruja Monitor Integration
   - **Supported account types**: Single tenant
   - **Redirect URI**: (deixe em branco)
5. Clique em **Register**

#### Passo 2: Obter Credenciais

1. Na página do aplicativo, copie:
   - **Application (client) ID**
   - **Directory (tenant) ID**
2. Vá para **Certificates & secrets**
3. Clique em **New client secret**
4. Descrição: "Coruja Monitor Secret"
5. Expiration: 24 months (recomendado)
6. Copie o **Value** (client secret) - só aparece uma vez!

#### Passo 3: Configurar Permissões

1. Vá para **API permissions**
2. Clique em **Add a permission**
3. Selecione **Dynamics CRM**
4. Marque **user_impersonation**
5. Clique em **Add permissions**
6. Clique em **Grant admin consent** (requer admin)

#### Passo 4: Configurar no Dynamics 365

1. Acesse seu Dynamics 365
2. Vá para **Settings** → **Security** → **Application Users**
3. Clique em **New**
4. Preencha:
   - **Application ID**: Cole o Client ID do Azure
   - **Full Name**: Coruja Monitor
   - **Primary Email**: seu-email@empresa.com
5. Atribua as **Security Roles** necessárias:
   - System Administrator (ou)
   - Service Manager (mínimo)
6. Salve

### Configuração no Coruja Monitor

```json
{
  "dynamics365": {
    "enabled": true,
    "url": "https://suaempresa.crm2.dynamics.com",
    "tenant_id": "seu-tenant-id-azure",
    "client_id": "seu-client-id",
    "client_secret": "seu-client-secret",
    "resource": "https://suaempresa.crm2.dynamics.com",
    "api_version": "9.2",
    "incident_type": "incident",
    "priority": 2,
    "owner_id": "guid-do-usuario-owner"
  }
}
```

### Parâmetros

| Parâmetro | Descrição | Obrigatório | Exemplo |
|-----------|-----------|-------------|---------|
| `enabled` | Habilitar integração | Sim | `true` |
| `url` | URL do Dynamics 365 | Sim | `https://empresa.crm2.dynamics.com` |
| `tenant_id` | Azure AD Tenant ID | Sim | `12345678-1234-...` |
| `client_id` | Azure AD Client ID | Sim | `87654321-4321-...` |
| `client_secret` | Azure AD Client Secret | Sim | `abc123...` |
| `resource` | Resource URL (geralmente igual ao url) | Sim | `https://empresa.crm2.dynamics.com` |
| `api_version` | Versão da API Web | Não | `9.2` (padrão) |
| `incident_type` | Tipo de entidade | Não | `incident` (padrão) |
| `priority` | Prioridade padrão (1-3) | Não | `2` (Normal) |
| `owner_id` | GUID do proprietário | Não | `guid-do-usuario` |

### Tipos de Entidade Suportados

- `incident` - Casos/Incidentes (padrão)
- `msdyn_workorder` - Ordens de Serviço (Field Service)
- Outras entidades customizadas

### Mapeamento de Severidade

| Coruja Monitor | Dynamics 365 Priority |
|----------------|----------------------|
| `critical` | 1 (High) |
| `warning` | 2 (Normal) |
| `info` | 3 (Low) |

---

## 📱 Twilio (SMS)

### Visão Geral

Envio de alertas via SMS usando a API do Twilio.

### Pré-requisitos

1. Conta no [Twilio](https://www.twilio.com)
2. Número de telefone Twilio ativo
3. Créditos na conta

### Configuração no Twilio

#### Passo 1: Criar Conta

1. Acesse [Twilio](https://www.twilio.com/try-twilio)
2. Crie uma conta gratuita (trial) ou paga
3. Verifique seu email e telefone

#### Passo 2: Obter Credenciais

1. No [Console do Twilio](https://console.twilio.com)
2. Copie:
   - **Account SID**
   - **Auth Token**

#### Passo 3: Comprar Número

1. Vá para **Phone Numbers** → **Buy a number**
2. Selecione país: Brasil (+55)
3. Filtre por: SMS capable
4. Compre um número
5. Copie o número no formato: `+5511999999999`

### Configuração no Coruja Monitor

```json
{
  "twilio": {
    "enabled": true,
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "seu-auth-token",
    "from_number": "+5511999999999",
    "to_numbers": [
      "+5511988888888",
      "+5511977777777"
    ]
  }
}
```

### Parâmetros

| Parâmetro | Descrição | Obrigatório | Exemplo |
|-----------|-----------|-------------|---------|
| `enabled` | Habilitar integração | Sim | `true` |
| `account_sid` | Twilio Account SID | Sim | `ACxxxx...` |
| `auth_token` | Twilio Auth Token | Sim | `abc123...` |
| `from_number` | Número Twilio (remetente) | Sim | `+5511999999999` |
| `to_numbers` | Lista de destinatários | Sim | `["+5511988888888"]` |

### Custos

- **Trial**: 15 USD de crédito grátis
- **SMS Brasil**: ~0.10 USD por mensagem
- **Números**: ~1 USD/mês

---

## 💬 WhatsApp via Twilio

### Visão Geral

Envio de alertas via WhatsApp usando Twilio WhatsApp Business API.

### Pré-requisitos

1. Conta Twilio (mesma do SMS)
2. WhatsApp Business API habilitado
3. Número WhatsApp aprovado

### Configuração no Twilio

#### Passo 1: Habilitar WhatsApp

1. No [Console do Twilio](https://console.twilio.com)
2. Vá para **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Siga o wizard de configuração
4. Para produção: Solicite aprovação do número

#### Passo 2: Sandbox (Teste)

Para testes, use o Twilio Sandbox:

1. Vá para **Messaging** → **Settings** → **WhatsApp sandbox settings**
2. Copie o número do sandbox: `whatsapp:+14155238886`
3. No seu WhatsApp, envie a mensagem de ativação para o número
4. Exemplo: `join <seu-codigo>`

#### Passo 3: Produção

Para produção (requer aprovação):

1. Solicite um número WhatsApp Business
2. Aguarde aprovação do Facebook (1-2 semanas)
3. Configure templates de mensagem
4. Use o número aprovado

### Configuração no Coruja Monitor

#### Opção 1: Via Twilio (Recomendado)

```json
{
  "whatsapp": {
    "enabled": true,
    "provider": "twilio",
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "auth_token": "seu-auth-token",
    "from_number": "whatsapp:+14155238886",
    "to_numbers": [
      "whatsapp:+5511988888888",
      "whatsapp:+5511977777777"
    ]
  }
}
```

#### Opção 2: API Customizada

```json
{
  "whatsapp": {
    "enabled": true,
    "provider": "custom",
    "api_url": "https://api.seuservidor.com/whatsapp/send",
    "api_key": "sua-api-key",
    "phone_numbers": [
      "+5511988888888",
      "+5511977777777"
    ]
  }
}
```

### Parâmetros

| Parâmetro | Descrição | Obrigatório | Exemplo |
|-----------|-----------|-------------|---------|
| `enabled` | Habilitar integração | Sim | `true` |
| `provider` | Provedor (twilio/custom) | Sim | `twilio` |
| `account_sid` | Twilio Account SID | Sim (Twilio) | `ACxxxx...` |
| `auth_token` | Twilio Auth Token | Sim (Twilio) | `abc123...` |
| `from_number` | Número remetente | Sim | `whatsapp:+14155238886` |
| `to_numbers` | Lista de destinatários | Sim | `["whatsapp:+5511988888888"]` |
| `api_url` | URL da API customizada | Sim (Custom) | `https://api...` |
| `api_key` | Chave da API customizada | Sim (Custom) | `abc123...` |

### Formato dos Números

- **Twilio**: Sempre use prefixo `whatsapp:`
- **Exemplo**: `whatsapp:+5511988888888`
- **Formato**: `whatsapp:+[código país][DDD][número]`

### Custos

- **Sandbox**: Grátis (apenas teste)
- **Produção**: ~0.005 USD por mensagem (Brasil)
- **Número Business**: Varia por país

---

## ⚙️ Configuração no Coruja Monitor

### Via Interface Web

1. Acesse o Coruja Monitor
2. Vá para **Configurações** → **Notificações**
3. Selecione a integração desejada
4. Preencha os campos
5. Clique em **Testar Integração**
6. Se OK, clique em **Salvar**

### Via API

```bash
# Obter configuração atual
curl -X GET http://localhost:8000/api/notifications/config \
  -H "Authorization: Bearer seu-token"

# Atualizar configuração
curl -X PUT http://localhost:8000/api/notifications/config \
  -H "Authorization: Bearer seu-token" \
  -H "Content-Type: application/json" \
  -d '{
    "dynamics365": {
      "enabled": true,
      "url": "https://empresa.crm2.dynamics.com",
      "tenant_id": "...",
      "client_id": "...",
      "client_secret": "..."
    },
    "twilio": {
      "enabled": true,
      "account_sid": "...",
      "auth_token": "...",
      "from_number": "+5511999999999",
      "to_numbers": ["+5511988888888"]
    },
    "whatsapp": {
      "enabled": true,
      "provider": "twilio",
      "account_sid": "...",
      "auth_token": "...",
      "from_number": "whatsapp:+14155238886",
      "to_numbers": ["whatsapp:+5511988888888"]
    }
  }'
```

---

## 🧪 Testes

### Testar Dynamics 365

```bash
curl -X POST http://localhost:8000/api/notifications/test/dynamics365 \
  -H "Authorization: Bearer seu-token"
```

Resposta esperada:
```json
{
  "message": "Incidente de teste criado com sucesso no Dynamics 365!",
  "incident_id": "CAS-12345-X1Y2Z3",
  "incident_url": "https://empresa.crm2.dynamics.com/main.aspx?..."
}
```

### Testar Twilio (SMS)

```bash
curl -X POST http://localhost:8000/api/notifications/test/twilio \
  -H "Authorization: Bearer seu-token"
```

Resposta esperada:
```json
{
  "message": "SMS enviado para 2 número(s)",
  "channel": "twilio",
  "errors": null
}
```

### Testar WhatsApp

```bash
curl -X POST http://localhost:8000/api/notifications/test/whatsapp \
  -H "Authorization: Bearer seu-token"
```

Resposta esperada:
```json
{
  "message": "WhatsApp enviado para 2 número(s) via Twilio",
  "channel": "whatsapp",
  "provider": "twilio",
  "errors": null
}
```

---

## 🔧 Troubleshooting

### Dynamics 365

#### Erro 401: Autenticação Falhou

**Causa**: Credenciais inválidas ou token expirado

**Solução**:
1. Verifique `tenant_id`, `client_id` e `client_secret`
2. Confirme que o aplicativo está registrado no Azure AD
3. Verifique se o client secret não expirou
4. Regenere o secret se necessário

#### Erro 403: Sem Permissão

**Causa**: Aplicativo sem permissões no Dynamics 365

**Solução**:
1. Verifique se o Application User foi criado no Dynamics 365
2. Confirme que as Security Roles estão atribuídas
3. Verifique permissões de API no Azure AD
4. Faça "Grant admin consent" no Azure AD

#### Erro 400: Dados Inválidos

**Causa**: Campos obrigatórios faltando ou formato incorreto

**Solução**:
1. Verifique o `incident_type` (incident, msdyn_workorder, etc)
2. Confirme que o `owner_id` é um GUID válido
3. Verifique se a entidade existe no seu Dynamics 365
4. Teste com campos mínimos primeiro

### Twilio

#### Erro: Biblioteca não instalada

**Solução**:
```bash
pip install twilio
```

#### Erro: Número inválido

**Causa**: Formato do número incorreto

**Solução**:
- Use formato internacional: `+5511999999999`
- Inclua código do país (+55 para Brasil)
- Não use espaços, parênteses ou hífens

#### Erro: Insufficient funds

**Causa**: Sem créditos na conta Twilio

**Solução**:
1. Acesse o Console do Twilio
2. Vá para **Billing**
3. Adicione créditos

### WhatsApp

#### Erro: Número não registrado no sandbox

**Causa**: Número não ativou o sandbox

**Solução**:
1. Envie a mensagem de ativação para o número do sandbox
2. Aguarde confirmação
3. Tente novamente

#### Erro: Template não aprovado

**Causa**: Mensagem fora do template aprovado (produção)

**Solução**:
1. Use apenas templates aprovados pelo Facebook
2. Para sandbox, qualquer mensagem funciona
3. Solicite aprovação de novos templates

---

## 📊 Monitoramento

### Logs

Todos os envios são registrados nos logs:

```bash
# Ver logs do worker
docker-compose logs -f worker

# Filtrar por integração
docker-compose logs -f worker | grep "Dynamics 365"
docker-compose logs -f worker | grep "Twilio"
docker-compose logs -f worker | grep "WhatsApp"
```

### Métricas

O Coruja Monitor registra:
- Total de notificações enviadas
- Taxa de sucesso por canal
- Tempo de resposta das APIs
- Erros e falhas

Acesse: **Dashboard** → **Métricas** → **Notificações**

---

## 🔐 Segurança

### Boas Práticas

1. **Nunca commite credenciais** no Git
2. Use **variáveis de ambiente** para secrets
3. **Rotacione secrets** periodicamente (a cada 6 meses)
4. Use **HTTPS** sempre
5. **Limite permissões** ao mínimo necessário
6. **Monitore logs** de acesso
7. **Revogue** credenciais não utilizadas

### Armazenamento Seguro

As credenciais são armazenadas:
- Criptografadas no banco de dados
- Apenas acessíveis por admins
- Nunca expostas em logs
- Protegidas por JWT

---

## 📚 Referências

### Dynamics 365
- [Dynamics 365 Web API](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/about)
- [Azure AD App Registration](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Dynamics 365 Security](https://docs.microsoft.com/en-us/dynamics365/customer-engagement/admin/security-roles-privileges)

### Twilio
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Twilio Pricing](https://www.twilio.com/pricing)

### WhatsApp
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Message Templates](https://developers.facebook.com/docs/whatsapp/message-templates)

---

## 🆘 Suporte

### Problemas com Integrações

1. Verifique os logs: `docker-compose logs -f worker`
2. Teste a integração: **Configurações** → **Notificações** → **Testar**
3. Consulte a documentação oficial do provedor
4. Abra um issue no GitHub

### Contato

- 📧 Email: suporte@corujamonitor.com
- 💬 Discord: [Coruja Monitor Community](https://discord.gg/corujamonitor)
- 🐛 Issues: [GitHub Issues](https://github.com/Quirinodsg/CorujaMonitor/issues)

---

**Data:** 04 de Março de 2026  
**Versão:** 1.0.0  
**Status:** ✅ Integração Completa
