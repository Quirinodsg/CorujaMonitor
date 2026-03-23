# Implementation Plan: Coruja Monitor v3.5 — Enterprise Hardening

## Overview

Implementação incremental das seis melhorias enterprise: suporte a `metric_only`, perfis padrão de sensores, pause completo no worker, redirect HTTPS via Nginx, consistência de alertas com cooldown/deduplicação/supressão por dependência, e suite de testes SDD.

## Tasks

---

### Backend — Migration e Models

- [x] 1. Criar script de migração SQL `api/migrate_v35_hardening.py`
  - Adicionar `ALTER TABLE sensors ADD COLUMN IF NOT EXISTS paused_until TIMESTAMP WITH TIME ZONE`
  - Adicionar `ALTER TABLE sensors ADD COLUMN IF NOT EXISTS cooldown_seconds INTEGER DEFAULT 300`
  - Criar tabela `default_sensor_profiles` com campos: `id`, `asset_type`, `sensor_type`, `enabled`, `alert_mode`, `threshold_warning`, `threshold_critical`, `created_at`, `updated_at`, constraint `UNIQUE(asset_type, sensor_type)`, índice em `asset_type`
  - Inserir seed com perfis de fábrica: VM e physical_server (cpu/memory/disk normal, network_in/network_out metric_only), network_device (ping normal, network_in/network_out metric_only)
  - _Requirements: 1.1, 2.1, 3.2, 5.1_

- [x] 2. Adicionar model `DefaultSensorProfile` e campo `cooldown_seconds` em `api/models.py`
  - Criar classe `DefaultSensorProfile(Base)` com todos os campos do schema SQL
  - Adicionar `UniqueConstraint('asset_type', 'sensor_type')` e `Index('idx_default_profiles_asset_type', 'asset_type')`
  - Adicionar campo `cooldown_seconds = Column(Integer, default=300)` na classe `Sensor`
  - _Requirements: 2.1, 5.1_

---

### Backend — Worker

- [x] 3. Adicionar checks de `paused_until` e `metric_only` em `worker/tasks.py`
  - Após o check de `enabled`, adicionar verificação de `paused_until`: normalizar timezone para UTC e comparar com `datetime.now(timezone.utc)`; se futuro, `continue`
  - Após o check de `paused_until`, verificar `alert_mode == 'metric_only'`: coletar e persistir métrica normalmente, mas não criar `Incident` e não enviar ao predictor (`continue` após persistir)
  - _Requirements: 1.3, 1.4, 1.7, 3.2, 3.3_

- [x] 4. Adicionar cooldown Redis e supressão por dependência em `worker/tasks.py`
  - Instanciar `redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)` no início da task
  - Antes de criar `Incident`, verificar deduplicação: se já existe `Incident` com `status='open'` para o sensor, `continue`
  - Antes de criar `Incident`, verificar supressão por dependência: query por sensor `ping` do mesmo `server_id`; se existe `Incident` aberto com `severity='critical'` para o ping e `sensor.sensor_type` está em `('cpu', 'memory', 'disk', 'network_in', 'network_out', 'network')`, logar e `continue`
  - Após criar `Incident`, setar chave Redis `cooldown:{sensor.id}` com TTL `sensor.cooldown_seconds or 300`; antes de criar, verificar se a chave existe e se sim, `continue`
  - Fallback: se Redis indisponível, logar warning e prosseguir sem cooldown Redis
  - _Requirements: 5.1, 5.2, 5.3, 5.5, 5.6_

---

### Backend — Alert Engine

- [x] 5. Adicionar `_apply_dependency_suppression` e Redis cooldown em `alert_engine/engine.py`
  - Adicionar parâmetros `dependency_engine: Optional[DependencyEngine] = None` e `redis_client=None` ao `__init__`
  - Implementar método `_apply_dependency_suppression(self, events)`: iterar eventos, chamar `self._dependency_engine.should_execute(sensor_id, host_id)` se disponível; se retornar `False`, incrementar `alerts_topology_suppressed` e logar sensor pai + filhos suprimidos; fail-open se `DependencyEngine` lançar exceção
  - Implementar método `_apply_redis_cooldown(self, events)`: verificar chave `cooldown:{sensor_id}:{event.type}` no Redis; se existir, suprimir; fallback para `_apply_cooldown` in-memory se Redis indisponível
  - Integrar `_apply_dependency_suppression` no pipeline `process_events` após `_apply_topology_suppression`
  - _Requirements: 5.3, 5.4, 5.5, 5.7_

---

### Backend — Routers

- [x] 6. Aceitar `metric_only` no endpoint `alert-mode` em `api/routers/sensor_controls.py`
  - Atualizar `AlertModeRequest.mode` description para `"normal | silent | metric_only"`
  - Alterar validação de `body.mode not in ("normal", "silent")` para `body.mode not in ("normal", "silent", "metric_only")`
  - Atualizar mensagem de erro e label de retorno para incluir `metric_only`
  - _Requirements: 1.1, 1.6_

- [x] 7. Criar router CRUD `api/routers/default_sensor_profiles.py`
  - Definir schema Pydantic `DefaultSensorProfileSchema` com campos: `asset_type`, `sensor_type`, `enabled`, `alert_mode`, `threshold_warning`, `threshold_critical`
  - Implementar `GET /default-sensor-profiles`: retorna todos os perfis agrupados por `asset_type`; se tabela vazia, retorna perfil de fábrica hardcoded
  - Implementar `PUT /default-sensor-profiles/{asset_type}`: valida `asset_type` em `('VM', 'physical_server', 'network_device')`, valida `alert_mode` em `('normal', 'silent', 'metric_only')`; faz upsert de todos os perfis do asset_type (delete + insert ou ON CONFLICT DO UPDATE)
  - Registrar router em `api/main.py`
  - _Requirements: 2.1, 2.4, 2.5, 2.7_

- [x] 8. Aplicar `DefaultSensorProfile` ao criar servidor em `api/routers/servers.py`
  - Após criar o `Server`, buscar perfis em `default_sensor_profiles` pelo `device_type` do servidor (mapeando para `asset_type`)
  - Se perfis encontrados, criar `Sensor` para cada perfil com `alert_mode`, `enabled`, `threshold_warning`, `threshold_critical` do perfil
  - Se nenhum perfil encontrado para o `asset_type`, aplicar perfil de fábrica hardcoded (cpu/memory/disk normal, network_in/network_out metric_only)
  - Sensores `network_in` e `network_out` criados sem `alert_mode` explícito devem ter `alert_mode = 'metric_only'` por padrão
  - _Requirements: 1.2, 2.2, 2.3, 2.5, 2.7_

---

### Infraestrutura — Nginx e Docker

- [x] 9. Criar configuração Nginx `nginx/nginx.conf`
  - Bloco `server { listen 80; return 301 https://$host$request_uri; }` para redirect HTTP→HTTPS
  - Bloco `server { listen 443 ssl; ssl_certificate /etc/nginx/ssl/coruja.crt; ssl_certificate_key /etc/nginx/ssl/coruja.key; ssl_protocols TLSv1.2 TLSv1.3; ssl_ciphers HIGH:!aNULL:!MD5; }`
  - Location `/api/` com `proxy_pass http://api:8000/api/` e headers `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`
  - Location `/` com `proxy_pass http://frontend:3000/` e suporte a WebSocket (`Upgrade`, `Connection`)
  - _Requirements: 4.1, 4.2, 4.6_

- [x] 10. Criar scripts SSL `scripts/generate-ssl-cert.sh` e `scripts/renew-ssl-cert.sh`
  - `generate-ssl-cert.sh`: criar diretório `/etc/nginx/ssl/` se não existir; executar `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/coruja.key -out /etc/nginx/ssl/coruja.crt` com subject padrão
  - `renew-ssl-cert.sh`: verificar data de expiração do certificado com `openssl x509 -enddate`; se expirar em menos de 30 dias, re-executar `generate-ssl-cert.sh` e recarregar nginx; logar resultado
  - Tornar ambos executáveis (`chmod +x`)
  - _Requirements: 4.3, 4.4_

- [x] 11. Adicionar serviço `nginx` ao `docker-compose.yml`
  - Adicionar serviço `nginx` com `image: nginx:alpine`, `restart: always`, `ports: ["80:80", "443:443"]`
  - Volumes: `./nginx/nginx.conf:/etc/nginx/nginx.conf:ro` e `./nginx/ssl:/etc/nginx/ssl:ro`
  - `depends_on: [api, frontend]`
  - Adicionar `REACT_APP_API_URL` configurado para `https://` no serviço `frontend` (comentado para produção)
  - _Requirements: 4.5, 4.7_

---

### Frontend

- [x] 12. Criar componente `frontend/src/components/DefaultSensorProfiles.js`
  - Tela em Configurações → Sensores Padrão com tabela por `asset_type` (VM, Servidor Físico, Network Device)
  - Para cada linha de sensor: toggle `enabled`, dropdown `alert_mode` (normal/silent/metric_only), campos numéricos `threshold_warning` e `threshold_critical`
  - Botão "Salvar" por `asset_type` que chama `PUT /default-sensor-profiles/{asset_type}`
  - Carregar dados via `GET /default-sensor-profiles` no mount
  - _Requirements: 2.6_

- [x] 13. Adicionar badge "PAUSADO" em `frontend/src/components/Servers.js`
  - Para cada sensor listado, verificar `enabled === false` ou `paused_until` com valor futuro (comparar com `new Date()`)
  - Exibir badge visual "PAUSADO" (ex: `<span className="badge-paused">PAUSADO</span>`) ao lado do nome do sensor quando pausado
  - Atualizar estado local imediatamente após chamada bem-sucedida à API de pause/resume
  - _Requirements: 3.5_

---

### Testes

- [x] 14. Criar estrutura de testes `tests/v35/__init__.py`
  - Criar arquivo vazio `tests/v35/__init__.py` para reconhecimento como pacote Python pelo pytest
  - _Requirements: 6.7_

- [x] 15. Criar `tests/v35/test_network_alert_mode.py`
  - Teste unitário: sensor `network_in` criado sem `alert_mode` explícito tem `alert_mode == 'metric_only'`
  - Teste unitário: sensor `network_out` criado sem `alert_mode` explícito tem `alert_mode == 'metric_only'`
  - Teste unitário: sensor `network_in` com tag `internet_link` no `config` tem `alert_mode != 'metric_only'`
  - Teste unitário: `PATCH /sensors/{id}/alert-mode` com `mode='metric_only'` retorna HTTP 200
  - Teste unitário: `PATCH /sensors/{id}/alert-mode` com `mode='invalido'` retorna HTTP 400
  - [x]* 15.1 Escrever property test para Property 1 (network sensors default metric_only)
    - `@given(sensor_type=st.sampled_from(['network_in', 'network_out']))` — para qualquer sensor_type de rede, `alert_mode` deve ser `'metric_only'`
    - **Property 1: Sensores de rede têm metric_only por padrão**
    - **Validates: Requirements 1.2**
  - [x]* 15.2 Escrever property test para Property 2 (metric_only não cria Incident)
    - `@given(value=st.floats(min_value=96.0, max_value=200.0))` — para qualquer valor acima do threshold, sensor metric_only não cria Incident
    - **Property 2: metric_only não cria Incident**
    - **Validates: Requirements 1.3, 1.7**
  - [x]* 15.3 Escrever property test para Property 3 (metric_only não envia ao predictor)
    - `@given(value=st.floats(min_value=0.0, max_value=200.0))` — para qualquer valor, sensor metric_only não invoca failure predictor
    - **Property 3: metric_only não envia ao predictor**
    - **Validates: Requirements 1.4**
  - _Requirements: 6.1_

- [x] 16. Criar `tests/v35/test_sensor_pause.py`
  - Teste unitário: sensor com `enabled=False` não cria Incident mesmo com threshold ultrapassado
  - Teste unitário: sensor com `paused_until` no passado é processado normalmente
  - Teste unitário: sensor retomado (`paused_until=None`, `enabled=True`) volta a ser processado
  - [x]* 16.1 Escrever property test para Property 6 (disabled sensor ignorado)
    - `@given(value=st.floats(min_value=96.0, max_value=200.0))` — sensor com `enabled=False` nunca cria Incident
    - **Property 6: Sensor disabled ignorado pelo worker**
    - **Validates: Requirements 3.1, 3.3, 3.6**
  - [x]* 16.2 Escrever property test para Property 7 (paused_until futuro ignorado)
    - `@given(value=st.floats(min_value=96.0, max_value=200.0), minutes=st.integers(min_value=1, max_value=10080))` — sensor com `paused_until` futuro nunca cria Incident
    - **Property 7: Sensor com paused_until futuro ignorado pelo worker**
    - **Validates: Requirements 3.2**
  - _Requirements: 6.2_

- [x] 17. Criar `tests/v35/test_default_profiles.py`
  - Teste unitário: `GET /default-sensor-profiles` retorna HTTP 200 com lista não vazia
  - Teste unitário: `PUT /default-sensor-profiles/VM` persiste e retorna perfil atualizado
  - Teste unitário: `PUT /default-sensor-profiles/VM` com `alert_mode='invalido'` retorna HTTP 422
  - Teste unitário: `PUT /default-sensor-profiles/tipo_desconhecido` retorna HTTP 400
  - Teste unitário: criar servidor do tipo VM aplica sensores do perfil VM
  - [x]* 17.1 Escrever property test para Property 4 (perfil padrão aplicado ao criar servidor)
    - `@given(asset_type=st.sampled_from(['VM', 'physical_server', 'network_device']))` — sensores criados correspondem exatamente aos sensor_types do perfil
    - **Property 4: Perfil padrão aplicado ao criar servidor**
    - **Validates: Requirements 2.2, 2.3**
  - [x]* 17.2 Escrever property test para Property 5 (alert_mode do perfil propagado para o sensor)
    - `@given(alert_mode=st.sampled_from(['normal', 'silent', 'metric_only']))` — sensor criado herda `alert_mode` do perfil
    - **Property 5: alert_mode do perfil propagado para o sensor**
    - **Validates: Requirements 2.5**
  - _Requirements: 6.3_

- [x] 18. Criar `tests/v35/test_https_redirect.py`
  - Teste unitário: `nginx/nginx.conf` contém `return 301 https://`
  - Teste unitário: `nginx/nginx.conf` contém bloco `ssl_certificate`
  - Teste unitário: `nginx/nginx.conf` contém `listen 80` e `listen 443 ssl`
  - Teste unitário: `docker-compose.yml` contém serviço `nginx` com portas `80:80` e `443:443`
  - Teste unitário: `scripts/generate-ssl-cert.sh` contém `openssl req`
  - Teste unitário: `scripts/renew-ssl-cert.sh` verifica expiração (contém lógica de 30 dias)
  - _Requirements: 6.4_

- [x] 19. Criar `tests/v35/test_alert_consistency.py`
  - Teste unitário: supressão por dependência registra log com identificação do sensor pai e filhos suprimidos
  - Teste unitário: fail-open quando `DependencyEngine` não tem cache para o host (Incident é criado normalmente)
  - [x]* 19.1 Escrever property test para Property 8 (cooldown impede segundo Incident)
    - `@given(cooldown_seconds=st.integers(min_value=60, max_value=3600))` — segunda violação dentro do cooldown não cria novo Incident
    - **Property 8: Cooldown impede segundo Incident dentro da janela**
    - **Validates: Requirements 5.1**
  - [x]* 19.2 Escrever property test para Property 9 (deduplicação com Incident aberto)
    - `@given(value=st.floats(min_value=96.0, max_value=200.0))` — nova violação com Incident aberto não cria segundo Incident
    - **Property 9: Deduplicação impede Incident duplicado com Incident aberto**
    - **Validates: Requirements 5.2, 5.6**
  - [x]* 19.3 Escrever property test para Property 10 (ping CRITICAL suprime filhos)
    - `@given(sensor_type=st.sampled_from(['cpu', 'memory', 'disk', 'network_in', 'network_out']))` — ping CRITICAL impede criação de Incident nos filhos
    - **Property 10: Ping CRITICAL suprime sensores filhos do mesmo host**
    - **Validates: Requirements 5.3**
  - [x]* 19.4 Escrever property test para Property 11 (ping OK reativa filhos — round trip)
    - Sensor ping CRITICAL → filhos suprimidos; ping OK → filhos voltam a gerar Incident
    - **Property 11: Ping OK reativa geração de Incidents para filhos**
    - **Validates: Requirements 5.4**
  - _Requirements: 6.5_

- [x] 20. Checkpoint — Garantir que todos os testes em `tests/v35/` passam
  - Executar `pytest tests/v35/ -v` e verificar 0 falhas
  - Garantir que os testes existentes em `tests/` não foram quebrados
  - Perguntar ao usuário se há dúvidas antes de prosseguir

---

### Validação Final

- [x] 21. Validação end-to-end no servidor Linux via Docker
  - Executar migration: `docker cp api/migrate_v35_hardening.py coruja-api:/app/ && docker exec coruja-api python migrate_v35_hardening.py`
  - Reiniciar serviços afetados: `docker compose restart api worker`
  - Verificar logs do worker para confirmar checks de `paused_until` e `metric_only` ativos: `docker logs coruja-worker --tail=50`
  - Verificar que serviço nginx sobe sem erros: `docker compose up nginx -d && docker logs coruja-nginx`
  - Confirmar redirect HTTP→HTTPS: verificar configuração nginx com `docker exec coruja-nginx nginx -t`
  - _Requirements: 1.3, 3.2, 4.1, 4.5_

## Notes

- Sub-tarefas marcadas com `*` são property-based tests opcionais (podem ser puladas para MVP mais rápido)
- Cada tarefa referencia requisitos específicos para rastreabilidade
- A ordem das tarefas garante que dependências sejam implementadas antes dos consumidores (migration → models → worker → routers → frontend → testes)
- Testes em `tests/v35/` usam Hypothesis (já presente no projeto via `.hypothesis/`)
- O campo `cooldown_seconds` no model `Sensor` já tem default 300 — nenhuma alteração de schema de API é necessária para compatibilidade retroativa

