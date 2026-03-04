# 🎯 SOLUÇÃO ENCONTRADA: Notificações Automáticas

## ❌ Problema Identificado

**Erro:** `column servers.updated_at does not exist`

**Causa Raiz:**
- O modelo `Server` no SQLAlchemy tem um campo `updated_at` definido
- MAS a tabela `servers` no PostgreSQL NÃO tem essa coluna
- Quando o worker tenta buscar o servidor, o SQLAlchemy gera um SELECT incluindo `updated_at`
- PostgreSQL retorna erro e a query falha
- A função `send_incident_notifications` falha silenciosamente ao tentar buscar o server

## 📊 Evidências

```
[2026-02-25 17:36:02,846: WARNING/ForkPoolWorker-4] DEBUG: Buscando incidente 21...
[2026-02-25 17:36:02,848: WARNING/ForkPoolWorker-4] DEBUG: Incidente encontrado: Memória - Limite warning ultrapassado
[2026-02-25 17:36:02,849: WARNING/ForkPoolWorker-4] DEBUG: Sensor encontrado: Memória
[2026-02-25 17:36:02,852: ERROR/ForkPoolWorker-3] Task tasks.request_ai_analysis raised unexpected: ProgrammingError('column servers.updated_at does not exist')
```

**Análise:**
1. ✅ Incidente encontrado
2. ✅ Sensor encontrado
3. ❌ Server query FALHA (updated_at não existe)
4. ❌ Função retorna sem enviar notificações

## ✅ Solução

### Opção 1: Adicionar coluna no banco (RECOMENDADO)

```sql
ALTER TABLE servers ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
```

### Opção 2: Remover campo do modelo

Editar `api/models.py` e `worker/models.py`:
```python
class Server(Base):
    __tablename__ = "servers"
    # ... outros campos ...
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # REMOVER
```

## 🔧 Aplicando a Solução

### Passo 1: Adicionar coluna no banco

```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "ALTER TABLE servers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"
```

### Passo 2: Reiniciar worker

```bash
docker-compose restart worker
```

### Passo 3: Testar novamente

```bash
# Resolver incidentes abertos
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "UPDATE incidents SET status = 'resolved', resolved_at = NOW() WHERE status = 'open';"

# Criar nova falha
docker exec coruja-api python criar_falha_teste.py

# Aguardar 70 segundos
# Verificar logs
docker logs coruja-worker --tail 100 | findstr "DEBUG"
```

## 📝 O que vai acontecer após a correção

1. Worker detecta falha
2. Cria incidente
3. Chama `send_incident_notifications`
4. Busca incidente ✅
5. Busca sensor ✅
6. Busca server ✅ (agora vai funcionar!)
7. Busca tenant ✅
8. Busca configuração ✅
9. Envia para TOPdesk ✅
10. Envia para Teams ✅
11. Logs mostram sucesso ✅

## 🎉 Resultado Esperado

```
[INFO] 🔔 INICIANDO envio de notificações para incidente 22
[INFO] DEBUG: Buscando incidente 22...
[INFO] DEBUG: Incidente encontrado: PING - Limite critical ultrapassado
[INFO] DEBUG: Sensor encontrado: PING
[INFO] DEBUG: Server encontrado: DESKTOP-P9VGN04
[INFO] DEBUG: Tenant encontrado: Default
[INFO] DEBUG: Configuração encontrada, TOPdesk enabled: True
[INFO] 📋 Configuração encontrada para tenant Default
[INFO] 📢 Enviando notificações para incidente 22: PING - Limite critical ultrapassado
[INFO] 🔵 TOPdesk está habilitado, tentando enviar...
[INFO] ✅ TOPdesk: Chamado INC-12345 criado
[INFO] 🔵 Teams está habilitado, tentando enviar...
[INFO] ✅ Teams: Mensagem enviada
[INFO] ⚪ Email desabilitado
[INFO] 📊 Resumo: 2 enviadas, 0 falharam
[INFO] ✅ Enviadas: TOPdesk: INC-12345, Teams
```

## 🚀 Comando Rápido para Aplicar

```bash
# Tudo em um comando
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "ALTER TABLE servers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();" && docker-compose restart worker && echo "✅ Correção aplicada! Aguarde 10 segundos e teste novamente."
```

---

**Data:** 25/02/2026 17:40  
**Problema:** column servers.updated_at does not exist  
**Solução:** Adicionar coluna no banco  
**Status:** Solução identificada, aguardando aplicação
