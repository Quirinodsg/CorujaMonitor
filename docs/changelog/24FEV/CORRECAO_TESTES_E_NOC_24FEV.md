# CORREÇÃO: Testes e NOC - 24/02/2026

## PROBLEMAS CORRIGIDOS

### 1. Falha de Teste Não Desaparecia Automaticamente

**Problema:**
- Falha simulada criada às 14:18:39
- Após 5 minutos, ainda aparecia como "Incidente Aberto"
- Dashboard mostrava: "⚠️1 Incidentes Abertos 🔥1 Críticos"

**Causa:**
- Incidente criado mas não tinha auto-resolução implementada
- Campo `resolved_at` permanecia NULL

**Solução:**
- Resolvido manualmente via SQL: `UPDATE incidents SET resolved_at = NOW() WHERE id = 8`
- Criado script `api/resolver_falhas_teste.py` para resolver automaticamente falhas antigas

**Como usar o script:**
```bash
docker exec coruja-api python resolver_falhas_teste.py
```

### 2. NOC Desatualizado (Mostrando 0 Servidores)

**Problema:**
- NOC mostrava: "✅0 SERVIDORES OK ⚠️0 EM AVISO 🔥0 CRÍTICOS"
- Mas havia 1 servidor ativo com 28 sensores

**Causa:**
- Erro no arquivo `api/routers/test_tools.py`
- Import faltando: `Server` não estava importado
- Erro: `NameError: name 'Server' is not defined`

**Solução:**
- Adicionado import: `from models import Sensor, Metric, Incident, User, Server`
- API reiniciada: `docker restart coruja-api`

## VERIFICAÇÃO

### Incidentes Resolvidos
```sql
SELECT id, description, created_at, resolved_at 
FROM incidents 
WHERE description LIKE '%TESTE%' 
ORDER BY created_at DESC;
```

Resultado esperado:
- Todos os incidentes de teste devem ter `resolved_at` preenchido

### NOC Funcionando
Acesse: http://192.168.30.189:3000 → Modo NOC

Deve mostrar:
- ✅ 1 SERVIDOR OK (ou o número correto de servidores)
- Disponibilidade: ~99.9%
- Empresas listadas com status correto

## SISTEMA DE TESTES

### Como Criar Falha Simulada

1. Vá em "Ferramentas de Teste" no menu
2. Selecione um sensor (ex: CPU)
3. Clique em "Simular Falha"
4. Falha será criada com valor acima do threshold crítico

### O Que Acontece

1. **Criação (t=0s):**
   - Incidente criado no banco
   - Aparece em "Incidentes Recentes"
   - Dashboard atualiza contadores

2. **Durante (t=0-5min):**
   - Incidente permanece ativo
   - Mostra como "Crítico" ou "Aviso"
   - Pode ser visto no NOC

3. **Resolução (t=5min):**
   - **MANUAL**: Execute o script de resolução
   - **AUTOMÁTICO**: Implementar worker que resolve após 5 minutos

### Resolver Manualmente

**Opção 1: Via Script**
```bash
docker exec coruja-api python resolver_falhas_teste.py
```

**Opção 2: Via SQL**
```sql
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
UPDATE incidents 
SET resolved_at = NOW() 
WHERE resolved_at IS NULL 
AND description LIKE '%TESTE%' 
AND created_at < NOW() - INTERVAL '5 minutes';
"
```

**Opção 3: Via Interface**
- Vá em "Ferramentas de Teste"
- Clique em "Resolver Todas as Falhas"

## MELHORIAS FUTURAS

### Auto-Resolução Automática

Criar worker Celery que roda a cada minuto:

```python
@celery.task
def auto_resolve_test_failures():
    """Resolve falhas de teste com mais de 5 minutos"""
    db = SessionLocal()
    try:
        db.execute(text("""
            UPDATE incidents 
            SET resolved_at = NOW() 
            WHERE resolved_at IS NULL 
            AND description LIKE '%TESTE%'
            AND created_at < NOW() - INTERVAL '5 minutes'
        """))
        db.commit()
    finally:
        db.close()
```

Agendar no Celery Beat:
```python
CELERYBEAT_SCHEDULE = {
    'auto-resolve-test-failures': {
        'task': 'tasks.auto_resolve_test_failures',
        'schedule': timedelta(minutes=1),
    },
}
```

### Notificações de Teste

- Email de teste quando falha é criada
- Webhook de teste para integração
- Slack/Teams notification de teste

## COMANDOS ÚTEIS

### Verificar Incidentes Abertos
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT id, sensor_id, description, severity, created_at 
FROM incidents 
WHERE resolved_at IS NULL 
ORDER BY created_at DESC;
"
```

### Verificar Status do NOC
```bash
curl -X GET "http://192.168.30.189:8000/api/v1/noc/global-status" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Verificar Logs da API
```bash
docker logs coruja-api --tail 50
```

### Reiniciar API
```bash
docker restart coruja-api
```

## RESUMO DAS CORREÇÕES

| Problema | Causa | Solução | Status |
|----------|-------|---------|--------|
| Falha não desaparece | Sem auto-resolução | Script manual + SQL | ✅ Resolvido |
| NOC mostra 0 servidores | Import faltando | Adicionar `Server` import | ✅ Resolvido |
| Erro no test_tools.py | `NameError: Server` | Corrigir imports | ✅ Resolvido |

## ARQUIVOS MODIFICADOS

1. `api/routers/test_tools.py` - Adicionado import `Server`
2. `api/resolver_falhas_teste.py` - Script para resolver falhas antigas (NOVO)

## PRÓXIMOS PASSOS

1. ✅ Recarregar dashboard (F5)
2. ✅ Verificar NOC mostra servidor correto
3. ✅ Verificar incidentes resolvidos
4. 🔄 Implementar auto-resolução automática (futuro)
5. 🔄 Adicionar notificações de teste (futuro)

---

**Data**: 24/02/2026
**Problemas**: Falha de teste não resolvia + NOC desatualizado
**Soluções**: Script de resolução + Correção de import
**Status**: ✅ Todos os problemas resolvidos
