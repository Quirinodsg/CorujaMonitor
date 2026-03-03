# SOLUÇÃO: Sensores "Aguardando dados" - Tenant Errado

## PROBLEMA IDENTIFICADO

Os sensores mostravam "Aguardando dados..." mesmo com a probe enviando métricas com sucesso (200 OK) e métricas sendo salvas no banco de dados.

### Causa Raiz

**Incompatibilidade de Tenant:**
- Admin estava logado no tenant_id=1 (Default)
- Probe, servidores e sensores estavam no tenant_id=7 (Techbiz)
- O endpoint `/api/v1/metrics/` verifica se o sensor pertence ao tenant do usuário
- Como os sensores estavam em tenant diferente, retornava 404 Not Found

### Evidências

```sql
-- Admin no tenant Default
SELECT id, email, tenant_id FROM users WHERE email = 'admin@coruja.com';
-- Resultado: tenant_id = 1

-- Probe no tenant Techbiz
SELECT id, name, tenant_id FROM probes WHERE id = 3;
-- Resultado: tenant_id = 7

-- Métricas existiam no banco
SELECT COUNT(*) FROM metrics WHERE timestamp > NOW() - INTERVAL '10 minutes';
-- Resultado: 99 métricas por sensor
```

## SOLUÇÃO APLICADA

Movemos a probe e todos os servidores para o tenant Default:

```sql
UPDATE probes SET tenant_id = 1 WHERE id = 3;
UPDATE servers SET tenant_id = 1 WHERE probe_id = 3;
```

### Resultado

```
Probe: BH (ID: 3)
Tenant: Default (ID: 1)

Servidor: DESKTOP-P9VGN04 (ID: 11)
Tenant: Default (ID: 1)

28 sensores com 99 métricas cada
```

## VERIFICAÇÃO

Após a migração:

1. **Probe está no Default:**
   ```sql
   SELECT p.id, p.name, t.name as tenant_name 
   FROM probes p 
   JOIN tenants t ON t.id = p.tenant_id 
   WHERE p.id = 3;
   ```
   Resultado: Default

2. **Servidor está no Default:**
   ```sql
   SELECT s.id, s.hostname, t.name as tenant_name 
   FROM servers s 
   JOIN tenants t ON t.id = s.tenant_id 
   WHERE s.probe_id = 3;
   ```
   Resultado: Default

3. **Métricas acessíveis:**
   - Admin (tenant_id=1) agora pode acessar sensores (tenant_id=1)
   - Endpoint `/api/v1/metrics/?sensor_id=198` retorna dados (não mais 404)

## PRÓXIMOS PASSOS

1. **Recarregue o dashboard** (F5 ou Ctrl+R)
2. Os sensores devem mudar de:
   - ❌ ❓ 28 Desconhecido
   - ✅ ✅ 28 OK (com valores reais)

3. Verifique que os cards mostram:
   - CPU: XX%
   - Memória: XX%
   - Disco C: XX%
   - Ping: XX ms
   - Etc.

## POR QUE ACONTECEU?

Quando você criou a probe na interface, selecionou a empresa "Techbiz" em vez de "Default". A probe foi criada corretamente na empresa selecionada, mas você estava logado como admin no tenant Default.

## COMO EVITAR NO FUTURO

### Opção 1: Usar sempre Default para admin
- Ao criar probes como admin, selecione "Default"
- Ou crie usuários específicos para cada empresa

### Opção 2: Trocar de empresa no login
- Faça logout
- No login, selecione a empresa correta
- Você verá apenas os recursos daquela empresa

### Opção 3: Admin ver tudo (futuro)
- Implementar permissão especial para admin ver todos os tenants
- Requer modificação no código da API

## COMANDOS ÚTEIS

### Verificar tenant de uma probe
```sql
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT p.id, p.name, t.name as tenant_name 
FROM probes p 
JOIN tenants t ON t.id = p.tenant_id 
WHERE p.token = 'SEU_TOKEN_AQUI';
"
```

### Verificar tenant de servidores
```sql
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT s.id, s.hostname, t.name as tenant_name 
FROM servers s 
JOIN tenants t ON t.id = s.tenant_id;
"
```

### Mover probe para outro tenant
```sql
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
UPDATE probes SET tenant_id = 1 WHERE id = PROBE_ID;
UPDATE servers SET tenant_id = 1 WHERE probe_id = PROBE_ID;
"
```

## RESUMO TÉCNICO

### Fluxo Normal
1. Probe envia métricas → API recebe (200 OK)
2. API salva no banco com tenant_id da probe
3. Frontend busca métricas → API verifica tenant do usuário
4. Se tenant do usuário = tenant do sensor → retorna dados
5. Se tenant diferente → retorna 404

### O que estava acontecendo
1. Probe enviava métricas → API recebia (200 OK) ✅
2. API salvava no banco com tenant_id=7 ✅
3. Frontend buscava métricas → API verificava tenant do admin (tenant_id=1) ✅
4. Sensor estava em tenant_id=7 ≠ tenant_id=1 → 404 ❌
5. Frontend mostrava "Aguardando dados..." ❌

### Solução
- Movemos probe e servidores para tenant_id=1
- Agora admin (tenant_id=1) consegue acessar sensores (tenant_id=1)
- Frontend recebe dados e mostra valores reais

---

**Data**: 24/02/2026
**Problema**: Tenant incompatível entre admin e probe
**Solução**: Mover probe e servidores para tenant Default
**Status**: ✅ Resolvido
