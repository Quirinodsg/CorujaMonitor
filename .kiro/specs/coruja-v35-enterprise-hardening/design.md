# Design Document — Coruja Monitor v3.5 Enterprise Hardening

## Overview

Este documento descreve o design técnico do conjunto de melhorias **Enterprise Hardening** do Coruja Monitor v3.5. O sistema é uma plataforma SaaS de monitoramento de infraestrutura composta por backend Python/FastAPI, worker Celery, frontend React, PostgreSQL/TimescaleDB e Redis, orquestrados via Docker Compose.

Os seis problemas endereçados são:
1. Alertas inúteis de sensores de rede (`network_in`/`network_out`) poluindo o painel de incidentes
2. Ausência de configuração de sensores padrão por tipo de ativo
3. Pause de sensor sem efeito completo no worker Celery
4. Ausência de redirect HTTP → HTTPS via Nginx
5. Inconsistência de alertas (duplicados, sem cooldown, sem supressão por dependência)
6. Suite de testes SDD cobrindo todos os problemas acima

### Arquitetura Geral

```
Internet
   │
   ▼
[Nginx :80/:443]  ← TLS termination, redirect 80→443
   │
   ├──/api/──────► [FastAPI :8000]
   │                    │
   │                    ├── PostgreSQL/TimescaleDB
   │                    ├── Redis (cooldown TTL keys)
   │                    └── Celery Worker
   │
   └──/──────────► [React Frontend :3000]
```

## Architecture

### Fluxo `evaluate_all_thresholds` — Worker Celery

O diagrama abaixo mostra o fluxo completo com os novos checks do v3.5:

```mermaid
flowchart TD
    A[evaluate_all_thresholds] --> B[Query: todos os sensores is_active=True]
    B --> C{sensor.enabled == False?}
    C -- Sim --> SKIP[Skip — não processa]
    C -- Não --> D{paused_until > now?}
    D -- Sim --> SKIP
    D -- Não --> E{alert_mode == 'metric_only'?}
    E -- Sim --> F[Coleta e persiste métrica normalmente]
    F --> SKIP2[Skip — não cria Incident, não envia ao predictor]
    E -- Não --> G[Avalia threshold]
    G --> H{Threshold ultrapassado?}
    H -- Não --> I[Auto-resolve Incidents abertos se existirem]
    H -- Sim --> J{Incident aberto já existe para este sensor?}
    J -- Sim --> K[Atualiza severity se mudou]
    J -- Não --> L{Ping do mesmo server_id está CRITICAL?}
    L -- Sim e sensor_type in cpu/memory/disk/network --> SKIP3[Skip — supressão por dependência]
    L -- Não --> M{Cooldown ativo? Redis key cooldown:{sensor_id}]
    M -- Sim --> SKIP4[Skip — cooldown]
    M -- Não --> N[Cria Incident]
    N --> O[SET Redis cooldown:{sensor_id} EX cooldown_seconds]
    O --> P[Dispara AIOps, self-healing, notificação se priority==5]
```

### Componentes Modificados / Novos

| Componente | Tipo | Mudança |
|---|---|---|
| `api/models.py` | Modificado | Novos campos em `Sensor`; nova model `DefaultSensorProfile` |
| `worker/tasks.py` | Modificado | Checks de `paused_until`, `metric_only`, cooldown Redis, supressão por dependência |
| `alert_engine/engine.py` | Modificado | Integração com `DependencyEngine`; cooldown via Redis |
| `api/routers/sensor_controls.py` | Modificado | Aceitar `metric_only` em `alert-mode` |
| `api/routers/default_sensor_profiles.py` | Novo | CRUD de perfis padrão |
| `api/routers/servers.py` | Modificado | Aplicar `DefaultSensorProfile` ao criar servidor |
| `api/migrate_v35_hardening.py` | Novo | Script de migração SQL |
| `nginx/nginx.conf` | Novo | Reverse proxy com TLS e redirect 80→443 |
| `nginx/ssl/` | Novo | Diretório para certificados |
| `scripts/generate-ssl-cert.sh` | Novo | Geração de certificado self-signed |
| `scripts/renew-ssl-cert.sh` | Novo | Renovação automática de certificado |
| `docker-compose.yml` | Modificado | Serviço `nginx` adicionado |
| `frontend/src/components/DefaultSensorProfiles.js` | Novo | Tela de perfis padrão |
| `frontend/src/components/Servers.js` | Modificado | Badge PAUSADO |
| `frontend/src/config.js` | Modificado | `REACT_APP_API_URL` para `https://` em produção |
| `tests/v35/` | Novo | Suite de testes SDD |

## Components and Interfaces

### 1. Sensor Controls Router — `api/routers/sensor_controls.py`

**Mudança:** aceitar `'metric_only'` como valor válido em `PATCH /sensors/{id}/alert-mode`.

```python
class AlertModeRequest(BaseModel):
    mode: str = Field(description="normal | silent | metric_only")

@router.patch("/{sensor_id}/alert-mode")
async def set_alert_mode(sensor_id: int, body: AlertModeRequest, ...):
    if body.mode not in ("normal", "silent", "metric_only"):
        raise HTTPException(400, "mode deve ser 'normal', 'silent' ou 'metric_only'")
    ...
```

**Mudança:** `PATCH /sensors/{id}/pause` já existe com `PauseRequest(duration_minutes: int)`. Nenhuma alteração de assinatura necessária — o campo `paused_until` já existe no modelo.

---

### 2. Default Sensor Profiles Router — `api/routers/default_sensor_profiles.py`

```python
class DefaultSensorProfileSchema(BaseModel):
    asset_type: str          # "VM" | "physical_server" | "network_device"
    sensor_type: str         # "cpu" | "memory" | "disk" | "network_in" | ...
    enabled: bool = True
    alert_mode: str = "normal"   # "normal" | "silent" | "metric_only"
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None

@router.get("/default-sensor-profiles")
async def list_profiles(db: Session = Depends(get_db), ...):
    """Retorna todos os perfis padrão."""

@router.put("/default-sensor-profiles/{asset_type}")
async def upsert_profile(
    asset_type: str,
    profiles: List[DefaultSensorProfileSchema],
    db: Session = Depends(get_db),
    ...
):
    """Substitui todos os perfis de um asset_type."""
```

---

### 3. Worker Tasks — `worker/tasks.py`

Assinatura da função principal (sem alteração de assinatura, apenas lógica interna):

```python
@app.task
def evaluate_all_thresholds():
    """Evaluate thresholds for all active sensors — v3.5 Enterprise Hardening"""
    db = SessionLocal()
    redis_client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
    try:
        now = datetime.now(timezone.utc)
        sensors = db.query(Sensor).filter(Sensor.is_active == True).all()

        for sensor in sensors:
            # 1. Check enabled
            if not sensor.enabled:
                continue

            # 2. Check paused_until
            if sensor.paused_until:
                pu = sensor.paused_until
                if pu.tzinfo is None:
                    pu = pu.replace(tzinfo=timezone.utc)
                if pu > now:
                    continue

            # 3. Check metric_only — coleta mas não cria Incident
            is_metric_only = getattr(sensor, 'alert_mode', 'normal') == 'metric_only'

            # ... coleta métrica ...

            if is_metric_only:
                continue  # não cria Incident, não envia ao predictor

            # 4. Check silent
            if getattr(sensor, 'alert_mode', 'normal') == 'silent':
                continue

            # 5. Avalia threshold
            threshold_breached, severity = evaluate_thresholds(sensor, latest_metric.value)

            if threshold_breached:
                # 6. Deduplicação: Incident aberto?
                existing = db.query(Incident).filter(
                    Incident.sensor_id == sensor.id,
                    Incident.status == "open"
                ).first()
                if existing:
                    continue

                # 7. Supressão por dependência: ping do mesmo server CRITICAL?
                ping_sensor = db.query(Sensor).filter(
                    Sensor.server_id == sensor.server_id,
                    Sensor.sensor_type == 'ping'
                ).first()
                if ping_sensor and sensor.sensor_type in ('cpu', 'memory', 'disk', 'network_in', 'network_out', 'network'):
                    ping_incident = db.query(Incident).filter(
                        Incident.sensor_id == ping_sensor.id,
                        Incident.status == "open",
                        Incident.severity == "critical"
                    ).first()
                    if ping_incident:
                        logger.info("Supressão por dependência: ping CRITICAL, skip sensor %s", sensor.id)
                        continue

                # 8. Cooldown via Redis
                cooldown_key = f"cooldown:{sensor.id}"
                cooldown_secs = getattr(sensor, 'cooldown_seconds', None) or 300
                if redis_client.exists(cooldown_key):
                    continue
                redis_client.setex(cooldown_key, cooldown_secs, "1")

                # 9. Cria Incident
                incident = Incident(...)
                db.add(incident)
                db.commit()
                ...
    finally:
        db.close()
```

---

### 4. Alert Engine — `alert_engine/engine.py`

**Mudanças:**
- Recebe instância de `DependencyEngine` no construtor (opcional, default `None`)
- Cooldown via Redis (chave `cooldown:{sensor_id}`, TTL = `cooldown_seconds`)
- Deduplicação: verifica `Incident` aberto antes de criar

```python
class AlertEngine:
    def __init__(
        self,
        ...,
        dependency_engine: Optional[DependencyEngine] = None,
        redis_client=None,
    ):
        self._dependency_engine = dependency_engine
        self._redis = redis_client
        ...

    def _apply_dependency_suppression(self, events: list[Event]) -> list[Event]:
        """
        Usa DependencyEngine para suprimir eventos de sensores filhos
        quando o sensor pai (ping) está CRITICAL.
        Fail-open: se DependencyEngine não tem cache para o host, permite.
        """
        if not self._dependency_engine:
            return events
        passed = []
        for event in events:
            host_id = str(event.host_id)
            sensor_id = str(event.sensor_id) if hasattr(event, 'sensor_id') else None
            if sensor_id and not self._dependency_engine.should_execute(sensor_id, host_id):
                self._metrics["alerts_topology_suppressed"] += 1
                logger.info(
                    "AlertEngine: supressão por dependência — sensor %s host %s",
                    sensor_id, host_id
                )
            else:
                passed.append(event)
        return passed

    def _apply_redis_cooldown(self, events: list[Event]) -> list[Event]:
        """Filtra eventos em cooldown usando Redis TTL keys."""
        if not self._redis:
            return self._apply_cooldown(events)  # fallback para cooldown in-memory
        passed = []
        for event in events:
            key = f"cooldown:{getattr(event, 'sensor_id', event.host_id)}:{event.type}"
            if self._redis.exists(key):
                self._metrics["alerts_cooldown_suppressed"] += 1
            else:
                passed.append(event)
        return passed
```

---

### 5. Nginx — `nginx/nginx.conf`

```nginx
# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS reverse proxy
server {
    listen 443 ssl;
    server_name _;

    ssl_certificate     /etc/nginx/ssl/coruja.crt;
    ssl_certificate_key /etc/nginx/ssl/coruja.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # API
    location /api/ {
        proxy_pass         http://api:8000/api/;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass         http://frontend:3000/;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
    }
}
```

## Data Models

### Schema SQL — Migration v3.5

```sql
-- ============================================================
-- Migration: coruja_v35_enterprise_hardening
-- ============================================================

-- 1. Adicionar valor 'metric_only' ao campo alert_mode (VARCHAR já suporta)
--    Apenas documentação — não requer ALTER TABLE pois é VARCHAR(20)

-- 2. Adicionar coluna paused_until (já existe no modelo ORM, garantir no banco)
ALTER TABLE sensors
    ADD COLUMN IF NOT EXISTS paused_until TIMESTAMP WITH TIME ZONE;

-- 3. Adicionar coluna cooldown_seconds
ALTER TABLE sensors
    ADD COLUMN IF NOT EXISTS cooldown_seconds INTEGER DEFAULT 300;

-- 4. Nova tabela default_sensor_profiles
CREATE TABLE IF NOT EXISTS default_sensor_profiles (
    id                  SERIAL PRIMARY KEY,
    asset_type          VARCHAR(50)  NOT NULL,   -- VM | physical_server | network_device
    sensor_type         VARCHAR(50)  NOT NULL,   -- cpu | memory | disk | network_in | ...
    enabled             BOOLEAN      NOT NULL DEFAULT TRUE,
    alert_mode          VARCHAR(20)  NOT NULL DEFAULT 'normal',
    threshold_warning   FLOAT,
    threshold_critical  FLOAT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (asset_type, sensor_type)
);

-- 5. Índice para lookup rápido por asset_type
CREATE INDEX IF NOT EXISTS idx_default_profiles_asset_type
    ON default_sensor_profiles (asset_type);

-- 6. Seed: perfis padrão de fábrica
INSERT INTO default_sensor_profiles
    (asset_type, sensor_type, enabled, alert_mode, threshold_warning, threshold_critical)
VALUES
    -- VM
    ('VM', 'cpu',         TRUE, 'normal',      80, 95),
    ('VM', 'memory',      TRUE, 'normal',      80, 95),
    ('VM', 'disk',        TRUE, 'normal',      80, 95),
    ('VM', 'network_in',  TRUE, 'metric_only', 80, 95),
    ('VM', 'network_out', TRUE, 'metric_only', 80, 95),
    -- physical_server
    ('physical_server', 'cpu',         TRUE, 'normal',      80, 95),
    ('physical_server', 'memory',      TRUE, 'normal',      80, 95),
    ('physical_server', 'disk',        TRUE, 'normal',      80, 95),
    ('physical_server', 'network_in',  TRUE, 'metric_only', 80, 95),
    ('physical_server', 'network_out', TRUE, 'metric_only', 80, 95),
    -- network_device
    ('network_device', 'ping',         TRUE, 'normal',      100, 200),
    ('network_device', 'network_in',   TRUE, 'metric_only', 80,  95),
    ('network_device', 'network_out',  TRUE, 'metric_only', 80,  95)
ON CONFLICT (asset_type, sensor_type) DO NOTHING;
```

### SQLAlchemy Model — `DefaultSensorProfile`

```python
class DefaultSensorProfile(Base):
    __tablename__ = "default_sensor_profiles"

    id                 = Column(Integer, primary_key=True, index=True)
    asset_type         = Column(String(50), nullable=False)
    sensor_type        = Column(String(50), nullable=False)
    enabled            = Column(Boolean, default=True)
    alert_mode         = Column(String(20), default='normal')
    threshold_warning  = Column(Float, nullable=True)
    threshold_critical = Column(Float, nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('asset_type', 'sensor_type', name='uq_profile_asset_sensor'),
        Index('idx_default_profiles_asset_type', 'asset_type'),
    )
```

### Campos Adicionados ao Model `Sensor`

```python
# Novos campos em api/models.py — classe Sensor
cooldown_seconds = Column(Integer, default=300)  # Cooldown por sensor em segundos
# paused_until já existe; alert_mode já existe (VARCHAR 20)
# Garantir que alert_mode aceita 'metric_only' (sem constraint de CHECK no banco)
```

### Redis Keys — Cooldown

| Chave | Tipo | TTL | Descrição |
|---|---|---|---|
| `cooldown:{sensor_id}` | String | `sensor.cooldown_seconds` (default 300s) | Bloqueia criação de novo Incident durante cooldown |

### Estrutura de Arquivos Novos/Modificados

```
coruja-monitor/
├── api/
│   ├── models.py                          # + DefaultSensorProfile, + cooldown_seconds em Sensor
│   ├── migrate_v35_hardening.py           # Script de migração
│   └── routers/
│       ├── sensor_controls.py             # + aceitar 'metric_only'
│       ├── servers.py                     # + aplicar DefaultSensorProfile
│       └── default_sensor_profiles.py     # NOVO
├── worker/
│   └── tasks.py                           # + paused_until, metric_only, cooldown Redis, dep. suppression
├── alert_engine/
│   └── engine.py                          # + DependencyEngine, Redis cooldown
├── nginx/
│   ├── nginx.conf                         # NOVO
│   └── ssl/                               # NOVO (gitignored)
│       ├── coruja.crt
│       └── coruja.key
├── scripts/
│   ├── generate-ssl-cert.sh               # NOVO
│   └── renew-ssl-cert.sh                  # NOVO
├── docker-compose.yml                     # + serviço nginx
├── frontend/
│   └── src/
│       ├── config.js                      # + REACT_APP_API_URL https
│       └── components/
│           ├── Servers.js                 # + badge PAUSADO
│           └── DefaultSensorProfiles.js   # NOVO
└── tests/
    └── v35/
        ├── __init__.py
        ├── test_network_alert_mode.py
        ├── test_sensor_pause.py
        ├── test_default_profiles.py
        ├── test_https_redirect.py
        └── test_alert_consistency.py
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Sensores de rede têm metric_only por padrão

*Para qualquer* sensor criado com `sensor_type` igual a `'network_in'` ou `'network_out'` sem `alert_mode` explícito, o `alert_mode` resultante deve ser `'metric_only'`.

**Validates: Requirements 1.2**

---

### Property 2: metric_only não cria Incident

*Para qualquer* sensor com `alert_mode = 'metric_only'` cujo valor de métrica ultrapasse o threshold configurado, o worker não deve criar nenhum `Incident` para esse sensor.

**Validates: Requirements 1.3, 1.7**

---

### Property 3: metric_only não envia ao predictor

*Para qualquer* sensor com `alert_mode = 'metric_only'`, o worker não deve invocar o serviço de predição de falhas (failure predictor), independentemente do valor da métrica coletada.

**Validates: Requirements 1.4**

---

### Property 4: Perfil padrão aplicado ao criar servidor

*Para qualquer* `device_type` com `DefaultSensorProfile` definido, ao criar um servidor com esse `device_type`, o conjunto de sensores criados automaticamente deve corresponder exatamente aos `sensor_type`s definidos no perfil para aquele `asset_type`.

**Validates: Requirements 2.2, 2.3**

---

### Property 5: alert_mode do perfil propagado para o sensor

*Para qualquer* `DefaultSensorProfile` com `alert_mode = 'metric_only'` para um `sensor_type`, ao criar um servidor que aplica esse perfil, o sensor correspondente deve ter `alert_mode = 'metric_only'`.

**Validates: Requirements 2.5**

---

### Property 6: Sensor disabled ignorado pelo worker

*Para qualquer* sensor com `enabled = False`, o worker não deve criar `Incident`, não deve persistir métricas e não deve enviar dados ao predictor durante o ciclo `evaluate_all_thresholds`.

**Validates: Requirements 3.1, 3.3, 3.6**

---

### Property 7: Sensor com paused_until futuro ignorado pelo worker

*Para qualquer* sensor com `paused_until` definido como um timestamp no futuro, o worker deve tratá-lo como desabilitado — sem criar `Incident`, sem persistir métricas e sem enviar ao predictor — até que `paused_until` seja ultrapassado.

**Validates: Requirements 3.2**

---

### Property 8: Cooldown impede segundo Incident dentro da janela

*Para qualquer* sensor com `cooldown_seconds = N`, se um `Incident` foi criado para esse sensor, uma segunda violação de threshold dentro de `N` segundos não deve gerar um novo `Incident`.

**Validates: Requirements 5.1**

---

### Property 9: Deduplicação impede Incident duplicado com Incident aberto

*Para qualquer* sensor que já possui um `Incident` com `status = 'open'`, uma nova violação de threshold não deve criar um segundo `Incident` enquanto o primeiro permanecer aberto.

**Validates: Requirements 5.2, 5.6**

---

### Property 10: Ping CRITICAL suprime sensores filhos do mesmo host

*Para qualquer* host onde o sensor do tipo `ping` possui um `Incident` aberto com `severity = 'critical'`, o worker não deve criar `Incident` para sensores do tipo `cpu`, `memory`, `disk`, `network_in`, `network_out` ou `network` do mesmo `server_id`.

**Validates: Requirements 5.3**

---

### Property 11: Ping OK reativa geração de Incidents para filhos — round trip

*Para qualquer* host onde o sensor `ping` estava `CRITICAL` (suprimindo filhos) e retorna ao status `OK` (Incident resolvido), o worker deve voltar a criar `Incident` para os sensores filhos quando estes violarem seus thresholds.

**Validates: Requirements 5.4**

## Error Handling

### Worker — `evaluate_all_thresholds`

| Situação | Comportamento |
|---|---|
| Redis indisponível | Fallback para cooldown in-memory (`_cooldown_tracker` existente no `AlertEngine`); log de warning |
| `paused_until` sem timezone | Normalizar para UTC antes de comparar (`replace(tzinfo=timezone.utc)`) |
| `DefaultSensorProfile` não encontrado para `asset_type` | Aplicar perfil de fábrica hardcoded (CPU, Memória, Disco normal; Network metric_only) |
| Sensor sem `cooldown_seconds` | Usar default de 300 segundos |
| `DependencyEngine` sem cache para o host | Fail-open: permitir criação de Incident normalmente (Requirement 5.7) |

### Nginx

| Situação | Comportamento |
|---|---|
| Certificado SSL ausente no path | Nginx falha ao iniciar com erro no log; não expõe HTTP sem TLS |
| Certificado expirado | `renew-ssl-cert.sh` detecta com antecedência de 30 dias e renova |

### API — Default Sensor Profiles

| Situação | Comportamento |
|---|---|
| `PUT /default-sensor-profiles/{asset_type}` com `alert_mode` inválido | HTTP 422 com detalhe de validação |
| `asset_type` desconhecido | HTTP 400 — asset_type deve ser `VM`, `physical_server` ou `network_device` |

### Alert Engine

| Situação | Comportamento |
|---|---|
| `DependencyEngine` lança exceção | Capturar, logar, fail-open (não suprimir) |
| Redis key de cooldown expirada antes do esperado | Comportamento correto — novo Incident pode ser criado após TTL |

---

## Testing Strategy

### Abordagem Dual

A suite de testes usa **testes unitários** para exemplos específicos e casos de borda, e **testes baseados em propriedades** (property-based testing com [Hypothesis](https://hypothesis.readthedocs.io/)) para validar as propriedades universais definidas acima.

- Testes unitários: exemplos concretos, integrações entre componentes, casos de borda
- Testes de propriedade: validação universal com inputs gerados aleatoriamente (mínimo 100 iterações por propriedade)

### Estrutura dos Testes

```
tests/v35/
├── __init__.py                  # Req 6.7
├── test_network_alert_mode.py   # Req 6.1 — Properties 1, 2, 3
├── test_sensor_pause.py         # Req 6.2 — Properties 6, 7
├── test_default_profiles.py     # Req 6.3 — Properties 4, 5
├── test_https_redirect.py       # Req 6.4 — Nginx config examples
└── test_alert_consistency.py    # Req 6.5 — Properties 8, 9, 10, 11
```

### Biblioteca de Property-Based Testing

**Hypothesis** (já presente no projeto via `.hypothesis/` directory).

Configuração mínima por teste de propriedade:
```python
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(...)
def test_property_N(...):
    # Feature: coruja-v35-enterprise-hardening, Property N: <texto da propriedade>
    ...
```

### Exemplos de Testes por Arquivo

#### `test_network_alert_mode.py`
```python
# Property 1: network_in/network_out default metric_only
@given(sensor_type=st.sampled_from(['network_in', 'network_out']))
def test_network_sensors_default_metric_only(sensor_type):
    # Feature: coruja-v35-enterprise-hardening, Property 1: network sensors default metric_only
    sensor = create_sensor(sensor_type=sensor_type)  # sem alert_mode explícito
    assert sensor.alert_mode == 'metric_only'

# Property 2: metric_only não cria Incident
@given(value=st.floats(min_value=96.0, max_value=200.0))  # acima do threshold_critical=95
def test_metric_only_no_incident(value):
    # Feature: coruja-v35-enterprise-hardening, Property 2: metric_only não cria Incident
    sensor = create_sensor(alert_mode='metric_only', threshold_critical=95.0)
    incidents_before = count_incidents(sensor.id)
    run_evaluate_for_sensor(sensor, value)
    assert count_incidents(sensor.id) == incidents_before

# Example: sensor com tag internet_link gera Incident normalmente
def test_internet_link_tag_generates_incident():
    sensor = create_sensor(
        sensor_type='network_in',
        config={'internet_link': True}
    )
    assert sensor.alert_mode != 'metric_only'
```

#### `test_sensor_pause.py`
```python
# Property 6: enabled=False ignorado
@given(value=st.floats(min_value=96.0, max_value=200.0))
def test_disabled_sensor_no_incident(value):
    # Feature: coruja-v35-enterprise-hardening, Property 6: disabled sensor ignored
    sensor = create_sensor(enabled=False, threshold_critical=95.0)
    run_evaluate_for_sensor(sensor, value)
    assert count_incidents(sensor.id) == 0

# Property 7: paused_until futuro ignorado
@given(
    value=st.floats(min_value=96.0, max_value=200.0),
    minutes=st.integers(min_value=1, max_value=10080)
)
def test_paused_sensor_no_incident(value, minutes):
    # Feature: coruja-v35-enterprise-hardening, Property 7: paused sensor ignored
    sensor = create_sensor(
        paused_until=datetime.now(timezone.utc) + timedelta(minutes=minutes),
        threshold_critical=95.0
    )
    run_evaluate_for_sensor(sensor, value)
    assert count_incidents(sensor.id) == 0
```

#### `test_alert_consistency.py`
```python
# Property 8: cooldown impede segundo Incident
@given(cooldown_seconds=st.integers(min_value=60, max_value=3600))
def test_cooldown_prevents_second_incident(cooldown_seconds):
    # Feature: coruja-v35-enterprise-hardening, Property 8: cooldown prevents duplicate
    sensor = create_sensor(cooldown_seconds=cooldown_seconds, threshold_critical=95.0)
    run_evaluate_for_sensor(sensor, 99.0)  # cria Incident + seta Redis key
    run_evaluate_for_sensor(sensor, 99.0)  # deve ser bloqueado pelo cooldown
    assert count_incidents(sensor.id) == 1

# Property 9: deduplicação com Incident aberto
@given(value=st.floats(min_value=96.0, max_value=200.0))
def test_dedup_open_incident(value):
    # Feature: coruja-v35-enterprise-hardening, Property 9: dedup open incident
    sensor = create_sensor(threshold_critical=95.0)
    create_open_incident(sensor.id)
    run_evaluate_for_sensor(sensor, value)
    assert count_incidents(sensor.id, status='open') == 1

# Property 10: ping CRITICAL suprime filhos
@given(sensor_type=st.sampled_from(['cpu', 'memory', 'disk', 'network_in', 'network_out']))
def test_ping_critical_suppresses_children(sensor_type):
    # Feature: coruja-v35-enterprise-hardening, Property 10: ping CRITICAL suppresses children
    server = create_server()
    ping = create_sensor(server_id=server.id, sensor_type='ping')
    child = create_sensor(server_id=server.id, sensor_type=sensor_type, threshold_critical=95.0)
    create_open_incident(ping.id, severity='critical')
    run_evaluate_for_sensor(child, 99.0)
    assert count_incidents(child.id) == 0
```

### Testes Unitários (Exemplos Específicos)

Cada arquivo de teste inclui também exemplos concretos para:
- Verificar que `PATCH /sensors/{id}/alert-mode` aceita `metric_only` (HTTP 200)
- Verificar que `PATCH /sensors/{id}/alert-mode` rejeita valores inválidos (HTTP 400)
- Verificar que `GET /default-sensor-profiles` retorna lista (HTTP 200)
- Verificar que `PUT /default-sensor-profiles/VM` persiste e retorna perfil atualizado
- Verificar que `nginx.conf` contém `return 301 https://`
- Verificar que `nginx.conf` contém bloco `ssl_certificate`
- Verificar que `docker-compose.yml` contém serviço `nginx` com portas `80:80` e `443:443`
- Verificar que `scripts/generate-ssl-cert.sh` contém `openssl req`
- Verificar que `scripts/renew-ssl-cert.sh` verifica expiração com antecedência de 30 dias
- Verificar que supressão por dependência registra log com identificação do sensor pai e filhos suprimidos
- Verificar fail-open quando DependencyEngine não tem cache para o host
