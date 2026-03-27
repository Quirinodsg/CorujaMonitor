# Design Tecnico - Coruja Monitor Enterprise Architecture

## Visao Geral

Este documento descreve a arquitetura tecnica da refatoracao enterprise do Coruja Monitor.
O sistema atual ja possui fundacoes solidas em `probe/engine/` que serao expandidas e integradas em uma arquitetura coesa de alto desempenho.

---

## Estado Atual vs. Estado Alvo

### O que ja existe (probe/engine/)
- `wmi_engine.py` - WQL queries otimizadas, PerfCounter com fallback para Win32_Processor
- `wmi_pool.py` - Connection pool WMI com idle timeout (300s) e cleanup automatico
- `scheduler.py` - Scheduler com backoff exponencial e limites por host (10 sensores, 5 WMI)
- `sensor_engine.py` - Abstracao de sensores com dispatch por tipo
- `thread_pool.py` - WorkerPool com ThreadPoolExecutor (10 workers)

### O que falta implementar
- Protocol Engines para SNMP, TCP, ICMP, Registry, Docker, Kubernetes
- Cache de metricas (Redis + fallback local, TTL 5-10s)
- Pre-Check de conectividade em cascata (Ping -> TCP -> Protocolo)
- Monitoramento adaptativo por estado do host (300s/60s/30s)
- SNMP Bulk requests (GetBulk max-repetitions=25)
- Event Engine (WMI subscriptions, Docker/K8s events)
- TimescaleDB migration (hypertables, compressao, retention 365 dias)
- AIOps expandido (Isolation Forest, Prophet/ARIMA, correlacao de eventos)
- Prometheus exporter (endpoint /metrics porta 9090)
- Monitoramento interno do probe (psutil - cpu, memoria, latencia)
- Seguranca de credenciais (AES-256 via Fernet, HashiCorp Vault, Azure Key Vault)
- Multi-probe coordination (datacenter/cloud/edge)

---

## Estrutura de Diretorios

```
probe/
├── engine/                          # EXISTENTE - expandir
│   ├── wmi_engine.py                # Existente
│   ├── wmi_pool.py                  # Existente
│   ├── scheduler.py                 # Existente
│   ├── sensor_engine.py             # Existente - expandir
│   ├── thread_pool.py               # Existente
│   ├── smart_collector.py           # Existente
│   ├── pre_check.py                 # NOVO - Pre-check de conectividade
│   ├── adaptive_monitor.py          # NOVO - Monitoramento adaptativo
│   ├── metric_cache.py              # NOVO - Cache Redis + local
│   ├── internal_metrics.py          # NOVO - Saude do probe
│   └── prometheus_exporter.py       # NOVO - Endpoint /metrics
│
├── protocol_engines/                # NOVO diretorio
│   ├── __init__.py
│   ├── base_engine.py               # Interface base abstrata
│   ├── icmp_engine.py               # ICMP/Ping
│   ├── snmp_engine.py               # SNMP v1/v2c/v3 + Bulk
│   ├── tcp_engine.py                # TCP port check
│   ├── registry_engine.py           # Windows Registry
│   ├── docker_engine.py             # Docker API
│   └── kubernetes_engine.py         # Kubernetes API
│
├── connection_pool/                 # NOVO diretorio
│   ├── __init__.py
│   ├── snmp_pool.py                 # Pool SNMP (5 conn/host)
│   └── tcp_pool.py                  # Pool TCP (10 conn/host)
│
├── event_engine/                    # NOVO diretorio
│   ├── __init__.py
│   ├── wmi_event_listener.py        # WMI subscriptions
│   ├── docker_event_listener.py     # Docker event stream
│   └── kubernetes_event_listener.py # K8s event watch
│
├── security/                        # NOVO diretorio
│   ├── credential_manager.py        # AES-256 + Vault integration
│   └── vault_client.py              # HashiCorp/Azure Key Vault
│
├── collectors/                      # EXISTENTE - manter compatibilidade
│   └── ...
│
├── probe_core.py                    # EXISTENTE - refatorar loop principal
└── config.py                        # EXISTENTE - expandir

api/
└── routers/
    └── timescale_migration.py       # NOVO - Migracao TimescaleDB

ai-agent/
├── aiops_engine.py                  # EXISTENTE - expandir
├── anomaly_detector.py              # NOVO - Isolation Forest
├── failure_predictor.py             # NOVO - Prophet/ARIMA
└── event_correlator.py              # NOVO - Correlacao de eventos
```

---

## Design dos Componentes

### 1. Protocol Engines (probe/protocol_engines/)

Interface base que todos os engines implementam:

```python
# probe/protocol_engines/base_engine.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class EngineResult:
    success: bool
    value: float
    unit: str
    metadata: Dict[str, Any]
    error: Optional[str] = None
    latency_ms: float = 0.0

class BaseProtocolEngine(ABC):
    @abstractmethod
    def execute(self, target: str, params: Dict[str, Any]) -> EngineResult:
        """Executa coleta e retorna resultado padronizado"""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se as dependencias do engine estao instaladas"""
        ...
```

Registro dinamico no SensorEngine (expandir `sensor_engine.py`):

```python
# Sem reinicializacao do probe
sensor_engine.register_engine("snmp_interface", SNMPEngine())
sensor_engine.register_engine("docker_container", DockerEngine())
```

---

### 2. SNMP Engine com Bulk Requests (protocol_engines/snmp_engine.py)

```python
class SNMPEngine(BaseProtocolEngine):
    # SNMPv2c/v3: GetBulk(max-repetitions=25) -> fallback GetNext
    # SNMPv1: GetNext individual

    def collect_bulk(self, host, community, oids, max_repetitions=25):
        # pysnmp bulkCmd - multiplos OIDs em uma requisicao
        ...

    def collect_interface_table(self, host, community):
        # SNMP walk OID 1.3.6.1.2.1.2.2 (ifTable) via GetBulk
        ...
```

---

### 3. Connection Pool SNMP/TCP (connection_pool/)

Complementa o `wmi_pool.py` existente com a mesma interface:

```python
# connection_pool/snmp_pool.py
MAX_SNMP_PER_HOST = 5
IDLE_TIMEOUT_SEC = 300

class SNMPConnectionPool:
    def acquire(self, host, community, version) -> SNMPSession: ...
    def release(self, host, session): ...
    def invalidate(self, host, session): ...
    def stats(self) -> Dict: ...

# connection_pool/tcp_pool.py
MAX_TCP_PER_HOST = 10

class TCPConnectionPool:
    def acquire(self, host, port) -> socket.socket: ...
    def release(self, host, sock): ...
```

---

### 4. Pre-Check de Conectividade (engine/pre_check.py)

Fluxo em cascata antes de sensores pesados:

```
WMI sensor:   Ping (2s) -> TCP:135 (2s) -> WMI namespace (3s) -> max 5s total
SNMP sensor:  Ping (2s) -> UDP:161 (2s)
TCP sensor:   Ping (2s) -> TCP:<port> (2s)
```

```python
class ConnectivityPreCheck:
    CACHE_TTL = 30  # segundos - evita verificacoes redundantes no mesmo host

    def check_wmi(self, host: str) -> PreCheckResult:
        # Cache hit -> retorna resultado anterior
        # 1. ICMP Ping
        # 2. TCP 135
        # 3. WMI namespace root/cimv2
        ...

    def check_snmp(self, host: str) -> PreCheckResult:
        # 1. ICMP Ping
        # 2. UDP 161
        ...
```

Integracao no `sensor_engine.py` (metodo `_dispatch`):

```python
def _dispatch(self, sensor):
    if sensor.type.startswith("wmi_"):
        check = self.pre_check.check_wmi(sensor.target)
        if not check.passed:
            return SensorResult(status=SensorStatus.CRITICAL, error=check.error)
    elif sensor.type.startswith("snmp_"):
        check = self.pre_check.check_snmp(sensor.target)
        if not check.passed:
            return SensorResult(status=SensorStatus.CRITICAL, error=check.error)
```

---

### 5. Metric Cache (engine/metric_cache.py)

```python
class MetricCache:
    TTL_CPU_MEMORY    = 5   # segundos
    TTL_DISK_SERVICES = 10  # segundos

    def __init__(self):
        # Tenta Redis; fallback para dict em memoria
        try:
            import redis
            self._backend = redis.Redis(host="localhost", port=6379, db=0)
            self._backend.ping()
            self._use_redis = True
        except Exception:
            self._backend = {}
            self._use_redis = False

    def get(self, host: str, sensor_type: str, query_hash: str):
        key = f"{host}:{sensor_type}:{query_hash}"
        ...

    def set(self, host, sensor_type, query_hash, value, ttl=None):
        ...

    @property
    def stats(self) -> Dict:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": self._hits / max(1, self._hits + self._misses),
            "backend": "redis" if self._use_redis else "local",
        }
```

---

### 6. Adaptive Monitor (engine/adaptive_monitor.py)

```python
class AdaptiveMonitor:
    INTERVAL_STABLE   = 300  # 5 min - todos sensores OK por 3+ ciclos
    INTERVAL_WARNING  = 60   # 1 min - qualquer sensor WARNING
    INTERVAL_CRITICAL = 30   # 30s  - qualquer sensor CRITICAL
    RECOVERY_CYCLES   = 5    # ciclos OK consecutivos para restaurar intervalo normal

    def update(self, host: str, status: str) -> int:
        """Retorna novo intervalo em segundos e notifica o Scheduler"""
        ...
```

Integracao com o `Scheduler` existente: `AdaptiveMonitor.update()` chama
`scheduler.update_interval(sensor_id, new_interval)` dinamicamente.

---

### 7. Event Engine (event_engine/)

```python
# event_engine/wmi_event_listener.py
class WMIEventListener:
    SUBSCRIPTIONS = [
        "SELECT * FROM __InstanceModificationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_Service'",
        "SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE TargetInstance ISA 'Win32_NTLogEvent' AND TargetInstance.EventType <= 2",
    ]

    def start(self, callback):
        # Thread separada por subscription
        # Reconexao com backoff: 5s, 10s, 30s, 60s
        ...

# event_engine/docker_event_listener.py
class DockerEventListener:
    WATCHED_EVENTS = {"die", "oom", "health_status"}

    def start(self, callback):
        # docker.APIClient().events() stream
        # Converte evento -> SensorResult -> envia a API em < 5s
        ...

# event_engine/kubernetes_event_listener.py
class KubernetesEventListener:
    WATCHED_REASONS = {"OOMKilling", "BackOff", "Failed", "Evicted"}

    def start(self, callback):
        # /api/v1/watch/events stream
        # Filtra Warning + Normal com reason em WATCHED_REASONS
        ...
```

---

### 8. TimescaleDB Migration

Migracao nao-destrutiva: adiciona extensao ao PostgreSQL existente.

```sql
-- 1. Habilitar extensao
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 2. Converter tabela existente em hypertable
SELECT create_hypertable('sensor_metrics', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 3. Compressao automatica apos 7 dias
ALTER TABLE sensor_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'server_id, sensor_type'
);
SELECT add_compression_policy('sensor_metrics', INTERVAL '7 days');

-- 4. Retention: remover dados > 365 dias
SELECT add_retention_policy('sensor_metrics', INTERVAL '365 days');

-- 5. Continuous aggregates (downsampling)
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', timestamp) AS bucket,
       server_id, sensor_type,
       AVG(value) AS avg_value,
       MAX(value) AS max_value,
       MIN(value) AS min_value
FROM sensor_metrics
GROUP BY bucket, server_id, sensor_type;

SELECT add_continuous_aggregate_policy('metrics_hourly',
    start_offset      => INTERVAL '3 hours',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

CREATE MATERIALIZED VIEW metrics_daily
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 day', timestamp) AS bucket,
       server_id, sensor_type,
       AVG(value) AS avg_value,
       MAX(value) AS max_value
FROM sensor_metrics
GROUP BY bucket, server_id, sensor_type;
```

Logica de query no dashboard: periodo > 24h usa `metrics_hourly`; periodo > 7 dias usa `metrics_daily`.

---

### 9. AIOps Expandido (ai-agent/)

```python
# ai-agent/anomaly_detector.py
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    TRAINING_WINDOW_DAYS = 7
    RETRAIN_INTERVAL_HOURS = 24

    def train(self, metric_type: str, host: str, data: List[float]):
        self.models[f"{host}:{metric_type}"] = IsolationForest(
            contamination=0.05, random_state=42
        ).fit([[v] for v in data])

    def detect(self, metric_type, host, value) -> AnomalyResult:
        # Retorna: anomaly_score, expected_range, confidence_level
        ...

# ai-agent/failure_predictor.py
# Prophet como primario, statsmodels ARIMA como fallback
class FailurePredictor:
    PREDICTION_HORIZON_HOURS = 24

    def predict_breach(self, host, metric_type, threshold) -> PredictionResult:
        # Retorna: predicted_breach_time, confidence_interval
        ...

# ai-agent/event_correlator.py
class EventCorrelator:
    CORRELATION_WINDOW_MINUTES = 5

    def correlate(self, alerts: List[Alert]) -> List[CorrelatedGroup]:
        # Agrupa alertas por janela temporal + host/grupo
        # Identifica causa raiz: ordem temporal + severidade + dependencias
        ...
```

---

### 10. Internal Metrics (engine/internal_metrics.py)

```python
import psutil, os

class InternalMetricsCollector:
    REPORT_INTERVAL  = 60    # segundos
    MEMORY_WARN_MB   = 512
    QUEUE_WARN_RATIO = 0.8

    def collect(self, worker_pool, wmi_pool, metric_cache) -> Dict:
        proc = psutil.Process(os.getpid())
        mem_mb = proc.memory_info().rss / 1024 / 1024

        if mem_mb > self.MEMORY_WARN_MB:
            logger.warning(f"Probe memory high: {mem_mb:.0f}MB - reduzindo workers para 10")
            worker_pool.resize(10)

        return {
            "probe_cpu_percent":        proc.cpu_percent(interval=1),
            "probe_memory_mb":          round(mem_mb, 1),
            "rpc_connections_active":   self._count_rpc_connections(),
            "wmi_query_latency_ms_avg": wmi_pool.avg_latency(),
            "sensor_execution_time_ms": worker_pool.stats()["avg_execution_ms"],
            "worker_queue_size":        worker_pool.active_count(),
            "cache_hit_ratio":          metric_cache.stats["hit_ratio"],
        }
```

---

### 11. Prometheus Exporter (engine/prometheus_exporter.py)

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server

class PrometheusExporter:
    PORT = 9090
    UPDATE_INTERVAL = 15  # segundos

    sensors_total      = Gauge('coruja_probe_sensors_total', '', ['probe_name'])
    execution_seconds  = Histogram('coruja_probe_sensor_execution_seconds', '',
                                   ['sensor_type', 'target_host'])
    wmi_queries_total  = Counter('coruja_probe_wmi_queries_total', '',
                                 ['target_host', 'status'])
    cache_hits_total   = Counter('coruja_probe_cache_hits_total', '')
    cache_misses_total = Counter('coruja_probe_cache_misses_total', '')
    worker_queue_size  = Gauge('coruja_probe_worker_queue_size', '')
    errors_total       = Counter('coruja_probe_errors_total', '',
                                 ['sensor_type', 'error_type'])

    def start(self):
        start_http_server(self.PORT)
        # Thread de atualizacao a cada 15s
        ...
```

---

### 12. Credential Manager (security/credential_manager.py)

```python
from cryptography.fernet import Fernet  # AES-256 via Fernet

class CredentialManager:
    def __init__(self, key: bytes):
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()

    def get_credential(self, name: str) -> Dict:
        # Prioridade:
        # 1. HashiCorp Vault (se VAULT_ADDR configurado)
        # 2. Azure Key Vault (se AZURE_KEYVAULT_URL configurado)
        # 3. Arquivo local criptografado com AES-256
        ...

    def redact_for_log(self, credential: Dict) -> Dict:
        """Substitui campos sensiveis por [REDACTED] nos logs"""
        sensitive = {"password", "token", "secret", "key"}
        return {k: "[REDACTED]" if k in sensitive else v
                for k, v in credential.items()}
```

---

### 13. Multi-Probe Architecture

A API ja suporta multiplos probes via `probe_token`. A expansao adiciona:

```
Core Server (API FastAPI)
├── /api/v1/probes/register      - registro com tipo: datacenter/cloud/edge
├── /api/v1/probes/heartbeat     - ja existe
├── /api/v1/probes/status        - dashboard de todos os probes
└── /api/v1/probes/redistribute  - redistribuicao de servidores

Probe Types:
  probe_datacenter - monitora hosts na rede local
  probe_cloud      - monitora recursos cloud (AWS/Azure/GCP)
  probe_edge       - monitora sites remotos/filiais
```

Redistribuicao automatica: quando probe fica offline > 120s, a API redistribui
seus servidores para outros probes do mesmo tipo via round-robin ponderado por carga.
Quando o probe volta online, a distribuicao original e restaurada.

---

## Fluxo de Execucao de um Sensor (End-to-End)

```
Scheduler.tick() - a cada 1s
    |
    +- Verifica sensores com next_run <= now
    +- Verifica MAX_CONCURRENT (20 total, 10/host, 5 WMI/host)
    |
    +- WorkerPool.submit(sensor)
           |
           +- AdaptiveMonitor.get_interval(host)
           |     +- Ajusta proxima execucao dinamicamente
           |
           +- PreCheck.check(host, protocol)  [cache 30s]
           |     +- HIT -> skip check
           |     +- Ping -> TCP -> Protocol test
           |           +- FAIL -> SensorResult(CRITICAL, host_unreachable)
           |
           +- MetricCache.get(host, type, query_hash)  [TTL 5-10s]
           |     +- HIT -> retorna cached, skip engine
           |
           +- ProtocolEngine.execute(sensor)
           |     +- ConnectionPool.acquire(host)
           |     +- Execute query (WQL/SNMP/ICMP/TCP)
           |     +- ConnectionPool.release(host)
           |
           +- MetricCache.set(result, ttl)
           |
           +- AdaptiveMonitor.update(host, status)
           |     +- Ajusta intervalo: OK=300s | WARNING=60s | CRITICAL=30s
           |
           +- API.send_metric(result)
```

---

## Modelo de Dados - SensorDefinition Expandido

```python
@dataclass
class SensorDefinition:
    # Campos existentes
    id: str
    type: str           # icmp_ping, wmi_cpu, snmp_interface, docker_container, ...
    target: str         # hostname ou IP
    interval: int       # 30 | 60 | 300 segundos
    timeout: int        # timeout por execucao (segundos)
    retries: int        # tentativas em caso de falha
    query: Optional[str]          # WQL customizada
    port: Optional[int]           # TCP port
    service_name: Optional[str]   # WMI service name
    credentials: Optional[Dict]   # resolvido via CredentialManager
    tags: Dict[str, str]
    # Novos campos
    protocol: str                 # icmp | wmi | snmp | tcp | registry | docker | k8s
    snmp_community: Optional[str]
    snmp_version: str = "2c"      # 1 | 2c | 3
    snmp_oids: List[str] = field(default_factory=list)
    adaptive: bool = True         # habilitar monitoramento adaptativo
    cache_ttl: Optional[int]      # override do TTL padrao do cache
```

---

## Dependencias Novas (probe/requirements.txt)

```
# Ja existentes
wmi
pythoncom
pysnmp
httpx
pyyaml

# Novas
cryptography>=41.0           # AES-256 (Fernet)
prometheus-client>=0.19      # Prometheus exporter
psutil>=5.9                  # Internal metrics (CPU/mem do probe)
redis>=5.0                   # Cache backend (opcional, fallback local)
scikit-learn>=1.4            # Isolation Forest (AIOps)
prophet>=1.1                 # Predicao de falhas (AIOps)
statsmodels>=0.14            # ARIMA fallback
docker>=7.0                  # Docker engine
kubernetes>=29.0             # Kubernetes engine
hvac>=2.0                    # HashiCorp Vault client
azure-keyvault-secrets>=4.8  # Azure Key Vault client
```

---

## Estrategia de Migracao (sem downtime)

1. Protocol Engines - novos arquivos em `protocol_engines/`, sem alterar collectors existentes
2. Connection Pool SNMP/TCP - adicionados ao lado do `wmi_pool.py` existente
3. Pre-Check + Cache - integrados ao `sensor_engine.py` via injecao de dependencia
4. Adaptive Monitor - integrado ao `scheduler.py` existente via callback
5. TimescaleDB - script SQL aplicado ao banco existente, tabela convertida em hypertable
6. AIOps - novos modulos em `ai-agent/`, sem alterar `aiops_engine.py` existente
7. Prometheus - endpoint adicional na porta 9090, nao interfere com API existente
8. `probe_core.py` - refatorado para usar novo pipeline, mantendo compatibilidade de API HTTP
