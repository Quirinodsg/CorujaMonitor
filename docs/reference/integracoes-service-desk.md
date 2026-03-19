# Integrações com Service Desk

## Visão Geral

O Coruja Monitor oferece integração nativa com os principais sistemas de Service Desk do mercado:
- **TOPdesk** - Sistema de Service Management holandês
- **GLPI** - Sistema open-source de Service Management
- **Zammad** - Sistema open-source moderno de Help Desk

Essas integrações permitem criar chamados/tickets automaticamente quando incidentes críticos ocorrem.

## TOPdesk

### Configuração

1. Acesse **Configurações > Integrações e Notificações**
2. Ative a integração **TOPdesk**
3. Preencha os campos:
   - **URL do TOPdesk**: URL base da sua instância (ex: `https://empresa.topdesk.net`)
   - **Usuário**: Login do operador (ex: `monitor@empresa.com`)
   - **Senha**: Senha do operador
   - **Grupo de Operadores**: Nome do grupo que receberá os chamados (ex: `Infraestrutura`)
   - **Categoria**: Categoria do chamado (ex: `Infraestrutura`)
   - **Subcategoria**: Subcategoria do chamado (ex: `Monitoramento`)

### Requisitos no TOPdesk

1. **Usuário com permissões**:
   - Permissão para criar chamados via API
   - Acesso ao grupo de operadores configurado

2. **API habilitada**:
   - A API REST deve estar habilitada na instância
   - Endpoint: `/tas/api/incidents`

3. **Categorias configuradas**:
   - As categorias e subcategorias devem existir no TOPdesk
   - O grupo de operadores deve estar ativo

### Teste de Integração

Após configurar, clique em **Testar Criação de Chamado** para validar:
- Conexão com a API
- Autenticação
- Permissões
- Criação de chamado de teste

### Funcionamento

Quando um incidente crítico ocorre:
1. Sistema verifica se TOPdesk está habilitado
2. Cria chamado automaticamente com:
   - **Título**: Nome do sensor + servidor
   - **Descrição**: Detalhes do incidente (valor, threshold, duração)
   - **Prioridade**: P1 (crítico) ou P2 (aviso)
   - **Impacto**: Pessoa (crítico) ou Departamento (aviso)
   - **Urgência**: Urgente (crítico) ou Normal (aviso)
   - **Categoria/Subcategoria**: Conforme configurado
   - **Grupo**: Conforme configurado

3. Retorna número do chamado e URL para acompanhamento

### Exemplo de Chamado Criado

```
Número: I 2024 0001234
Título: CPU crítica - SERVIDOR-WEB-01
Descrição: 
  Servidor: SERVIDOR-WEB-01 (192.168.1.100)
  Sensor: cpu_usage
  Valor atual: 98.5%
  Threshold crítico: 95%
  Duração: 15 minutos
  
  Ação recomendada: Verificar processos consumindo CPU
Categoria: Infraestrutura > Monitoramento
Prioridade: P1
Status: Aberto
```

## GLPI

### Configuração

1. Acesse **Configurações > Integrações e Notificações**
2. Ative a integração **GLPI**
3. Preencha os campos:
   - **URL do GLPI**: URL base da sua instância (ex: `https://glpi.empresa.com`)
   - **App Token**: Token da aplicação
   - **User Token**: Token do usuário
   - **ID da Entidade**: ID da entidade (0 = raiz)
   - **ID da Categoria**: ID da categoria de chamado
   - **Urgência**: Nível de urgência padrão (1-5)
   - **Impacto**: Nível de impacto padrão (1-5)

### Requisitos no GLPI

1. **API habilitada**:
   - Acesse **Setup > Geral > API**
   - Marque "Habilitar API REST"
   - Configure "Permitir acesso completo da API"

2. **App Token**:
   - Acesse **Setup > Geral > API**
   - Crie um novo "API client"
   - Copie o App Token gerado

3. **User Token**:
   - Acesse seu perfil (canto superior direito)
   - Vá em **Configurações Remotas**
   - Gere um "Token de acesso à API"
   - Copie o User Token

4. **Permissões**:
   - Usuário deve ter permissão para criar tickets
   - Usuário deve ter acesso à entidade configurada

### Teste de Integração

Após configurar, clique em **Testar Criação de Ticket** para validar:
- Conexão com a API
- Autenticação (App Token + User Token)
- Permissões
- Criação de ticket de teste

### Funcionamento

Quando um incidente crítico ocorre:
1. Sistema verifica se GLPI está habilitado
2. Inicia sessão na API GLPI
3. Cria ticket automaticamente com:
   - **Nome**: Nome do sensor + servidor
   - **Conteúdo**: Detalhes do incidente
   - **Entidade**: Conforme configurado
   - **Categoria**: Conforme configurado
   - **Urgência**: 5 (crítico) ou 3 (aviso)
   - **Impacto**: 5 (crítico) ou 3 (aviso)
   - **Prioridade**: 5 (crítico) ou 3 (aviso)
   - **Tipo**: 1 (Incidente)
   - **Status**: 2 (Em atendimento)

4. Encerra sessão na API
5. Retorna ID do ticket e URL para acompanhamento

### Exemplo de Ticket Criado

```
ID: #12345
Nome: Memória crítica - SERVIDOR-DB-01
Conteúdo:
  Servidor: SERVIDOR-DB-01 (192.168.1.200)
  Sensor: memory_usage
  Valor atual: 97.2%
  Threshold crítico: 95%
  Duração: 8 minutos
  
  Ação recomendada: Verificar consumo de memória e processos
Categoria: Infraestrutura > Servidores
Urgência: Muito Alta (5)
Impacto: Muito Alto (5)
Prioridade: Muito Alta (5)
Status: Em atendimento (Assigned)
```

## Níveis de Urgência e Impacto (GLPI)

### Urgência
- **5**: Muito Alta - Incidentes críticos
- **4**: Alta - Incidentes importantes
- **3**: Média - Avisos (padrão)
- **2**: Baixa - Informações
- **1**: Muito Baixa - Observações

### Impacto
- **5**: Muito Alto - Afeta toda organização
- **4**: Alto - Afeta departamento
- **3**: Médio - Afeta grupo (padrão)
- **2**: Baixo - Afeta pessoa
- **1**: Muito Baixo - Sem impacto

### Prioridade (calculada automaticamente)
A prioridade é calculada pela matriz Urgência x Impacto:
- **5**: Muito Alta (Urgência 5 + Impacto 5)
- **4**: Alta
- **3**: Média
- **2**: Baixa
- **1**: Muito Baixa

## Fluxo de Criação Automática

```
┌─────────────────────┐
│  Incidente Crítico  │
│  Detectado          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Verificar Config   │
│  TOPdesk/GLPI       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Criar Chamado/     │
│  Ticket via API     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Registrar ID no    │
│  Incidente          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Notificar Equipe   │
│  (Teams/Telegram)   │
└─────────────────────┘
```

## Boas Práticas

### TOPdesk
1. Use um usuário dedicado para integração (ex: `monitor@empresa.com`)
2. Configure categorias específicas para monitoramento
3. Crie grupo de operadores dedicado para alertas automáticos
4. Configure SLA específico para chamados de monitoramento
5. Use templates de chamado para padronizar informações

### GLPI
1. Crie um usuário técnico dedicado para API
2. Configure categoria específica para monitoramento
3. Use entidade separada se necessário
4. Configure regras de negócio para auto-atribuição
5. Configure notificações para o grupo responsável

## Troubleshooting

### TOPdesk

**Erro: "Authentication failed"**
- Verifique usuário e senha
- Confirme que usuário tem permissão para API
- Teste login manual no TOPdesk

**Erro: "Category not found"**
- Verifique se categoria existe no TOPdesk
- Use nome exato (case-sensitive)
- Verifique se subcategoria pertence à categoria

**Erro: "Operator group not found"**
- Verifique se grupo existe e está ativo
- Use nome exato do grupo
- Confirme que usuário tem acesso ao grupo

### GLPI

**Erro: "Invalid App-Token"**
- Verifique se API está habilitada
- Confirme que App Token está correto
- Regenere App Token se necessário

**Erro: "Invalid user token"**
- Verifique se User Token está correto
- Regenere User Token no perfil do usuário
- Confirme que usuário está ativo

**Erro: "Entity not found"**
- Verifique ID da entidade (0 = raiz)
- Confirme que usuário tem acesso à entidade
- Use ID numérico, não nome

**Erro: "Category not found"**
- Verifique ID da categoria
- Confirme que categoria existe
- Use ID numérico, não nome

## Segurança

### Credenciais
- Senhas e tokens são armazenados criptografados no banco
- Use HTTPS para comunicação com APIs
- Rotacione tokens periodicamente
- Use usuários dedicados com permissões mínimas

### Auditoria
- Todas as criações de chamados são registradas
- Logs incluem usuário, timestamp e resultado
- Falhas são registradas para análise

## Próximos Passos

Após configurar as integrações:
1. Teste com incidente real
2. Ajuste categorias e prioridades conforme necessário
3. Configure regras de auto-atribuição no Service Desk
4. Treine equipe sobre fluxo de chamados automáticos
5. Monitore taxa de criação de chamados

## Zammad

### Configuração

1. Acesse **Configurações > Integrações e Notificações**
2. Ative a integração **Zammad**
3. Preencha os campos:
   - **URL do Zammad**: URL base da sua instância (ex: `https://zammad.empresa.com`)
   - **Token de API**: Token de acesso HTTP
   - **ID do Grupo**: ID do grupo que receberá os tickets
   - **ID do Cliente**: ID do cliente/usuário que criará os tickets
   - **Prioridade**: Nível de prioridade padrão (1-3)
   - **Tags**: Tags para identificar tickets automáticos (ex: `monitoramento,automatico`)

### Requisitos no Zammad

1. **Token de API**:
   - Acesse **Perfil > Token Access**
   - Clique em **Create**
   - Dê um nome (ex: `Coruja Monitor`)
   - Marque permissões: `ticket.agent` ou `admin.api`
   - Copie o token gerado (só aparece uma vez!)

2. **Grupo configurado**:
   - Acesse **Manage > Groups**
   - Anote o ID do grupo (visível na URL ao editar)
   - Exemplo: `/groups/3/edit` → ID = 3

3. **Cliente/Usuário**:
   - Crie ou use usuário existente
   - Anote o ID do usuário (visível na URL ao editar)
   - Exemplo: `/users/profile/5` → ID = 5
   - Este usuário aparecerá como criador dos tickets

### Teste de Integração

Após configurar, clique em **Testar Criação de Ticket** para validar:
- Conexão com a API
- Autenticação via token
- Permissões
- Criação de ticket de teste

### Funcionamento

Quando um incidente crítico ocorre:
1. Sistema verifica se Zammad está habilitado
2. Cria ticket automaticamente com:
   - **Título**: Nome do sensor + servidor
   - **Corpo**: Detalhes do incidente (HTML formatado)
   - **Grupo**: Conforme configurado
   - **Cliente**: Conforme configurado
   - **Prioridade**: 3 (alta - crítico) ou 2 (normal - aviso)
   - **Estado**: open (aberto)
   - **Tags**: Conforme configurado + `incidente-critico` ou `incidente-aviso`
   - **Artigo**: Primeiro artigo com detalhes técnicos

3. Retorna número do ticket e URL para acompanhamento

### Exemplo de Ticket Criado

```
Número: #12345
Título: 🔥 Disco crítico - SERVIDOR-APP-01
Corpo:
  ⚠️ ALERTA CRÍTICO DE MONITORAMENTO
  
  📊 Detalhes do Incidente:
  • Servidor: SERVIDOR-APP-01 (192.168.1.150)
  • Sensor: disk_c_usage
  • Valor atual: 96.8%
  • Threshold crítico: 95%
  • Duração: 12 minutos
  • Detectado em: 19/02/2026 14:35:22
  
  💡 Ação Recomendada:
  Verificar espaço em disco e limpar arquivos temporários
  
  🔗 Link: http://monitor.empresa.com/servers/5
  
Grupo: Infraestrutura
Cliente: Sistema de Monitoramento
Prioridade: 3 - Alta
Estado: Aberto
Tags: monitoramento, automatico, incidente-critico, disco
```

### Níveis de Prioridade (Zammad)

- **3**: Alta - Incidentes críticos
- **2**: Normal - Avisos e alertas (padrão)
- **1**: Baixa - Informações

### Estados de Ticket

- **new**: Novo (não atribuído)
- **open**: Aberto (em atendimento)
- **pending reminder**: Aguardando lembrete
- **pending close**: Aguardando fechamento
- **closed**: Fechado

### Tags Automáticas

O sistema adiciona automaticamente:
- `monitoramento`: Identifica origem
- `automatico`: Criado automaticamente
- `incidente-critico`: Para alertas críticos
- `incidente-aviso`: Para avisos
- Tipo do sensor: `cpu`, `memoria`, `disco`, `rede`, etc.
- Tags personalizadas configuradas

### Artigos do Ticket

Cada ticket criado contém um artigo inicial com:
- **Tipo**: note (nota interna) ou email (visível ao cliente)
- **Remetente**: Sistema de Monitoramento
- **Corpo**: Detalhes técnicos formatados em HTML
- **Interno**: Sim (não visível ao cliente final)

### Troubleshooting Zammad

**Erro: "Authentication failed"**
- Verifique se token está correto
- Confirme que token tem permissões adequadas
- Regenere token se necessário
- Use header: `Authorization: Token token=SEU_TOKEN`

**Erro: "Group not found"**
- Verifique ID do grupo (número, não nome)
- Confirme que grupo existe e está ativo
- Acesse `/api/v1/groups` para listar grupos

**Erro: "Customer not found"**
- Verifique ID do cliente/usuário
- Confirme que usuário existe e está ativo
- Acesse `/api/v1/users` para listar usuários

**Erro: "Invalid priority"**
- Use valores 1, 2 ou 3
- Prioridade 3 = Alta (crítico)
- Prioridade 2 = Normal (padrão)

**Erro: "Connection refused"**
- Verifique URL do Zammad
- Confirme que API está acessível
- Teste: `curl https://zammad.empresa.com/api/v1/tickets`

### Webhooks Zammad (Opcional)

Para receber atualizações do Zammad de volta no Coruja:

1. **Configure Webhook no Zammad**:
   - Acesse **Manage > Webhooks**
   - Crie novo webhook
   - URL: `https://coruja.empresa.com/api/v1/webhooks/zammad`
   - Eventos: `ticket.update`, `ticket.close`
   - Ativo: Sim

2. **Eventos Suportados**:
   - Ticket atualizado → Atualiza status no Coruja
   - Ticket fechado → Marca incidente como resolvido
   - Comentário adicionado → Registra no histórico

### Boas Práticas Zammad

1. **Token de API**:
   - Crie token dedicado para integração
   - Use permissões mínimas necessárias
   - Rotacione token periodicamente
   - Armazene token de forma segura

2. **Organização**:
   - Crie grupo específico para monitoramento
   - Use tags consistentes para filtrar tickets
   - Configure views personalizadas para tickets automáticos
   - Defina SLA específico para alertas críticos

3. **Automação**:
   - Configure triggers para auto-atribuição
   - Crie templates de resposta para incidentes comuns
   - Use macros para ações repetitivas
   - Configure notificações para equipe

4. **Monitoramento**:
   - Acompanhe taxa de criação de tickets
   - Monitore tempo de resposta
   - Analise tickets recorrentes
   - Ajuste thresholds conforme necessário

### Comparação: TOPdesk vs GLPI vs Zammad

| Característica | TOPdesk | GLPI | Zammad |
|---------------|---------|------|--------|
| **Licença** | Comercial | Open Source | Open Source |
| **Facilidade** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **API** | REST | REST | REST |
| **Autenticação** | Basic Auth | Token duplo | Token único |
| **Webhooks** | ✅ | ❌ | ✅ |
| **Tags** | ❌ | ✅ | ✅ |
| **Interface** | Tradicional | Tradicional | Moderna |
| **Mobile** | ✅ | ⚠️ | ✅ |
| **Custo** | Alto | Grátis | Grátis |

### Quando Usar Cada Sistema

**TOPdesk**:
- Empresas que já usam TOPdesk
- Necessidade de ITIL completo
- Orçamento disponível para licenças

**GLPI**:
- Necessidade de inventário de ativos
- Gestão de contratos e licenças
- Orçamento limitado

**Zammad**:
- Interface moderna e intuitiva
- Foco em atendimento rápido
- Equipe técnica familiarizada com ferramentas modernas
- Necessidade de webhooks e automação avançada
