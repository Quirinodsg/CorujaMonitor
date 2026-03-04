# 🔧 Correção Crítica: TOPdesk Caller vs Operator

## 🐛 Problema Identificado

O código da API estava confundindo o conceito de **Requisitante (Caller)** com **Operador (Operator)** no TOPdesk.

### Erro no Código Original

```python
# ERRADO - Linha 383 de api/routers/notifications.py
payload = {
    'callerLookup': {'email': username},  # ❌ username não é email!
    'category': {'name': config.get('category', 'Infraestrutura')},  # ❌ Sempre enviava
    'subcategory': {'name': config.get('subcategory', 'Monitoramento')},  # ❌ Sempre enviava
    'operatorGroup': {'name': config.get('operator_group', '')},  # ❌ Enviava vazio
    ...
}
```

**Problemas:**
1. Usava `email` mas o campo `username` contém o login (`coruja.monitor`), não email
2. Enviava campos opcionais sempre, mesmo vazios, causando erros na API
3. Não havia comentários explicando a diferença entre caller e operator

## ✅ Correção Aplicada

### Código Corrigido

```python
# CORRETO - api/routers/notifications.py
# Build incident payload
# Note: username is the caller (person who opens the ticket), not the operator
# operatorGroup is where the ticket will be assigned (infrastructure team)
payload = {
    'callerLookup': {'loginName': username},  # ✅ Usa loginName para identificar o requisitante
    'briefDescription': incident_data.get('title', 'Alerta do Coruja Monitor'),
    'request': incident_data.get('description', ''),
    'priority': {'name': 'P1' if incident_data.get('severity') == 'critical' else 'P2'},
    'impact': {'name': 'Pessoa' if incident_data.get('severity') == 'critical' else 'Departamento'},
    'urgency': {'name': 'Urgente' if incident_data.get('severity') == 'critical' else 'Normal'}
}

# Add optional fields only if configured
if config.get('category'):
    payload['category'] = {'name': config.get('category')}
if config.get('subcategory'):
    payload['subcategory'] = {'name': config.get('subcategory')}
if config.get('operator_group'):
    payload['operatorGroup'] = {'name': config.get('operator_group')}
```

## 📚 Conceitos do TOPdesk

### Requisitante (Caller)
- **O que é**: Pessoa que **abre** o chamado
- **No nosso caso**: `coruja.monitor`
- **Tipo de usuário**: Usuário comum do TOPdesk (não precisa ser operador)
- **Onde aparece**: Campo "Requisitante" do chamado
- **API**: `callerLookup: {loginName: 'coruja.monitor'}`

### Operador (Operator)
- **O que é**: Pessoa ou grupo que **atende** o chamado
- **No nosso caso**: Equipe de Infraestrutura (configurável)
- **Tipo de usuário**: Operadores/Técnicos do TOPdesk
- **Onde aparece**: Campo "Operador" ou "Grupo de Operadores" do chamado
- **API**: `operatorGroup: {name: 'Infraestrutura'}`

### Fluxo Completo

```
┌─────────────────┐
│ coruja.monitor  │ ← Requisitante (abre o chamado)
│  (Caller)       │
└────────┬────────┘
         │
         │ Cria chamado
         ▼
┌─────────────────┐
│   TOPdesk       │
│   Chamado #123  │
└────────┬────────┘
         │
         │ Atribuído para
         ▼
┌─────────────────┐
│ Infraestrutura  │ ← Operadores (atendem o chamado)
│  (Operators)    │
└─────────────────┘
```

## 🎯 Configuração Correta

### Campos Obrigatórios

1. **URL do TOPdesk**: `https://grupotechbiz.topdesk.net`
2. **Usuário (Login)**: `coruja.monitor`
   - Este é o REQUISITANTE
   - Não precisa ser operador
   - Apenas precisa ter permissão para criar chamados
3. **Senha**: Senha do usuário `coruja.monitor`

### Campos Opcionais

4. **Grupo de Operadores**: (exemplo: "Infraestrutura", "Suporte TI")
   - Este é o grupo que vai ATENDER os chamados
   - Se não preencher, o chamado fica sem atribuição
   - Recomendado preencher para direcionar automaticamente

5. **Categoria**: (exemplo: "Infraestrutura", "Servidores")
   - Ajuda a organizar os chamados
   - Opcional, mas recomendado

6. **Subcategoria**: (exemplo: "Monitoramento", "Alertas")
   - Detalha ainda mais a categoria
   - Opcional

## 🔍 Verificações no TOPdesk

### Após criar um chamado de teste, verifique:

1. **Campo Requisitante**: Deve mostrar `coruja.monitor`
2. **Campo Operador/Grupo**: Deve mostrar o grupo configurado (se preenchido)
3. **Status**: Deve estar "Novo" ou "Em Andamento"
4. **Prioridade**: P1 (crítico) ou P2 (normal)

### Permissões Necessárias

O usuário `coruja.monitor` precisa ter:
- ✅ Permissão para criar chamados (incident)
- ✅ Acesso à API REST do TOPdesk
- ❌ NÃO precisa ser operador
- ❌ NÃO precisa ter permissões administrativas

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes (Errado) | Depois (Correto) |
|---------|----------------|------------------|
| Identificação do Caller | `email: username` | `loginName: username` |
| Tipo de dado | Email (mas username é login) | Login name |
| Campos opcionais | Sempre enviados | Só enviados se preenchidos |
| Comentários | Nenhum | Explicação clara |
| Tratamento de erros | Genérico | Específico por tipo |

## 🚀 Testando a Correção

### Passo 1: Reiniciar a API

```bash
docker restart coruja-api
```

### Passo 2: Configurar no Frontend

1. Vá em Configurações > Integrações e Notificações
2. Ative o TOPdesk
3. Preencha:
   - URL: `https://grupotechbiz.topdesk.net`
   - Usuário: `coruja.monitor`
   - Senha: [sua senha]
   - Grupo de Operadores: `Infraestrutura` (opcional mas recomendado)
4. Clique em "Salvar Configurações"
5. Clique em "Testar Criação de Chamado"

### Passo 3: Verificar no TOPdesk

1. Acesse `https://grupotechbiz.topdesk.net`
2. Vá em "Chamados" ou "Incidents"
3. Procure por "Teste de Integração - Coruja Monitor"
4. Verifique:
   - ✅ Requisitante: coruja.monitor
   - ✅ Grupo: Infraestrutura (se configurado)
   - ✅ Status: Novo/Em Andamento
   - ✅ Prioridade: P2

## 📝 Logs para Debug

Se houver erro, verifique os logs:

```bash
# Logs da API
docker logs coruja-api --tail 50

# Procure por:
# - "TOPdesk API error"
# - "authentication"
# - "callerLookup"
```

## ✅ Checklist de Validação

- [ ] API reiniciada
- [ ] Configuração salva no frontend
- [ ] Teste executado com sucesso
- [ ] Chamado criado no TOPdesk
- [ ] Requisitante correto (coruja.monitor)
- [ ] Grupo de operadores atribuído (se configurado)
- [ ] Prioridade e urgência corretas

## 🎉 Resultado Esperado

Ao testar a integração, você deve ver:

```
✅ Sucesso!

Chamado de teste criado com sucesso no TOPdesk!
Incident ID: INC-12345
URL: https://grupotechbiz.topdesk.net/tas/secure/incident?unid=...
```

E no TOPdesk:

```
Chamado: INC-12345
Título: Teste de Integração - Coruja Monitor
Requisitante: coruja.monitor
Grupo: Infraestrutura
Status: Novo
Prioridade: P2 - Normal
```

---

**Data da Correção**: 25 de Fevereiro de 2026  
**Arquivo Modificado**: `api/routers/notifications.py` (linhas 382-401)  
**Status**: ✅ Corrigido e documentado
