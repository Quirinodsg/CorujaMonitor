# Integrações TOPdesk e GLPI - Implementado

## Resumo
Implementadas integrações com sistemas de Service Desk TOPdesk e GLPI no Coruja Monitor.

## O Que Foi Implementado

### 1. Frontend (Settings.js)

#### Adicionado estado para TOPdesk e GLPI:
```javascript
topdesk: { 
  enabled: false, 
  url: '', 
  username: '', 
  password: '', 
  operator_group: '', 
  category: '', 
  subcategory: '' 
}

glpi: { 
  enabled: false, 
  url: '', 
  app_token: '', 
  user_token: '', 
  entity_id: '', 
  category_id: '', 
  urgency: 4, 
  impact: 3 
}
```

#### Interface de Configuração:

**TOPdesk:**
- URL da instância
- Usuário e senha (Basic Auth)
- Grupo de operadores
- Categoria e subcategoria
- Botão de teste

**GLPI:**
- URL da instância
- App Token e User Token
- ID da entidade
- ID da categoria
- Seletores de urgência e impacto (1-5)
- Botão de teste

### 2. Backend (notifications.py)

#### Funções Implementadas:

**`create_topdesk_incident()`**
- Cria chamado no TOPdesk via API REST
- Usa Basic Authentication
- Endpoint: `/tas/api/incidents`
- Mapeia severidade para prioridade/impacto/urgência
- Retorna número do chamado e URL

**`create_glpi_ticket()`**
- Cria ticket no GLPI via API REST
- Usa App Token + User Token
- Fluxo: initSession → createTicket → killSession
- Endpoint: `/apirest.php/Ticket`
- Mapeia severidade para urgência/impacto/prioridade
- Retorna ID do ticket e URL

#### Endpoints de Teste:

**`POST /api/v1/notifications/test/topdesk`**
- Testa integração com TOPdesk
- Cria chamado de teste
- Retorna ID e URL do chamado

**`POST /api/v1/notifications/test/glpi`**
- Testa integração com GLPI
- Cria ticket de teste
- Retorna ID e URL do ticket

### 3. Documentação

Criado `docs/integracoes-service-desk.md` com:
- Guia de configuração para TOPdesk
- Guia de configuração para GLPI
- Requisitos em cada sistema
- Exemplos de chamados/tickets criados
- Troubleshooting
- Boas práticas
- Segurança

## Como Usar

### Configurar TOPdesk

1. Acesse **Configurações > Integrações e Notificações**
2. Ative **TOPdesk**
3. Preencha:
   - URL: `https://empresa.topdesk.net`
   - Usuário: `monitor@empresa.com`
   - Senha: senha do usuário
   - Grupo: `Infraestrutura`
   - Categoria: `Infraestrutura`
   - Subcategoria: `Monitoramento`
4. Clique em **Testar Criação de Chamado**
5. Salve as configurações

### Configurar GLPI

1. Acesse **Configurações > Integrações e Notificações**
2. Ative **GLPI**
3. Preencha:
   - URL: `https://glpi.empresa.com`
   - App Token: (gerado em Setup > API)
   - User Token: (gerado no perfil do usuário)
   - ID Entidade: `0` (raiz)
   - ID Categoria: ID da categoria desejada
   - Urgência: `4` (Alta)
   - Impacto: `3` (Médio)
4. Clique em **Testar Criação de Ticket**
5. Salve as configurações

## Requisitos

### TOPdesk
- API REST habilitada
- Usuário com permissão para criar chamados
- Categorias e grupos configurados

### GLPI
- API REST habilitada (Setup > Geral > API)
- App Token criado
- User Token do usuário
- Permissões para criar tickets

## Mapeamento de Severidade

### TOPdesk
- **Critical** → Prioridade P1, Impacto "Pessoa", Urgência "Urgente"
- **Warning** → Prioridade P2, Impacto "Departamento", Urgência "Normal"

### GLPI
- **Critical** → Urgência 5, Impacto 5, Prioridade 5
- **Warning** → Urgência 3, Impacto 3, Prioridade 3

## Estrutura de Chamado/Ticket

### Informações Incluídas:
- Nome do servidor
- IP do servidor
- Nome do sensor
- Tipo do sensor
- Valor atual
- Threshold crítico/aviso
- Duração do problema
- Ação recomendada

### Exemplo:
```
Título: CPU crítica - SERVIDOR-WEB-01

Descrição:
Servidor: SERVIDOR-WEB-01 (192.168.1.100)
Sensor: cpu_usage
Valor atual: 98.5%
Threshold crítico: 95%
Duração: 15 minutos

Ação recomendada: Verificar processos consumindo CPU
```

## Fluxo de Integração

```
Incidente Crítico
       ↓
Verificar Config TOPdesk/GLPI
       ↓
Criar Chamado/Ticket via API
       ↓
Registrar ID no Incidente
       ↓
Notificar Equipe
```

## Próximos Passos

### Para Usar em Produção:

1. **Configurar credenciais** nos sistemas
2. **Testar integração** com botão de teste
3. **Validar categorias** e grupos
4. **Configurar regras** de auto-atribuição no Service Desk
5. **Treinar equipe** sobre fluxo automático

### Melhorias Futuras:

1. **Auto-resolução**: Fechar chamado quando incidente for resolvido
2. **Atualização**: Adicionar comentários no chamado com atualizações
3. **Bi-direcional**: Sincronizar status do chamado com incidente
4. **Anexos**: Incluir gráficos e logs no chamado
5. **SLA**: Calcular SLA baseado em tempo de resolução

## Arquivos Modificados

- `frontend/src/components/Settings.js` - Interface de configuração
- `api/routers/notifications.py` - Backend e integrações
- `docs/integracoes-service-desk.md` - Documentação completa

## Testes

### Teste Manual:
1. Configure TOPdesk ou GLPI
2. Clique em "Testar Criação de Chamado/Ticket"
3. Verifique se chamado foi criado no sistema
4. Confirme que ID e URL são retornados

### Teste Automático:
1. Crie incidente crítico no sistema
2. Verifique se chamado é criado automaticamente
3. Confirme que ID do chamado está registrado no incidente
4. Valide notificações enviadas

## Segurança

- Credenciais armazenadas criptografadas no banco
- Comunicação via HTTPS
- Tokens com permissões mínimas
- Auditoria de todas as criações
- Logs de falhas para análise

## Suporte

Para problemas:
1. Verifique logs da API
2. Teste conexão manual com API do Service Desk
3. Valide credenciais e permissões
4. Consulte documentação em `docs/integracoes-service-desk.md`
