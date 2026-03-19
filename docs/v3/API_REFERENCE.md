# Coruja Monitor v3.0 — Referência de API

## Endpoints Novos (v3)

Base URL: `http://<servidor>:8000`

---

## Observabilidade

### GET /api/v1/observability/health-score

Retorna o health score geral da infraestrutura (0-100).

**Response:**
```json
{
  "score": 87.5,
  "status": "healthy",
  "trend": "stable",
  "breakdown": {
    "sensors_ok": 142,
    "sensors_warning": 8,
    "sensors_critical": 3,
    "sensors_unknown": 2,
    "sensors_total": 155,
    "open_incidents": 2
  },
  "timestamp": "2026-03-19T10:00:00"
}
```

Status possíveis: `healthy` (≥90), `degraded` (70-89), `critical` (<70)

---

### GET /api/v1/observability/impact-map

Retorna servidores com sensores em estado crítico ou warning.

**Response:**
```json
{
  "nodes": [
    {
      "id": "uuid",
      "name": "SRVCRMPRD001",
      "ip": "192.168.1.10",
      "severity": "critical",
      "critical_sensors": 2,
      "warning_sensors": 1,
      "total_sensors": 15
    }
  ],
  "total_affected": 3,
  "timestamp": "2026-03-19T10:00:00"
}
```

---

## Alertas Inteligentes

### GET /api/v1/alerts/intelligent

Lista alertas inteligentes com filtros opcionais.

**Query params:**
- `status`: `open` | `acknowledged` | `resolved`
- `severity`: `critical` | `warning` | `info`
- `limit`: int (default 50)

**Response:**
```json
{
  "alerts": [
    {
      "id": "uuid",
      "title": "Switch SW-CORE-01 offline — 5 servidores afetados",
      "severity": "critical",
      "status": "open",
      "root_cause": "Falha no switch de core",
      "affected_hosts": ["uuid1", "uuid2"],
      "confidence": 0.92,
      "created_at": "2026-03-19T09:45:00",
      "resolved_at": null
    }
  ],
  "total": 1
}
```

---

### GET /api/v1/alerts/intelligent/{alert_id}/root-cause

Retorna análise detalhada de causa raiz de um alerta.

**Response:**
```json
{
  "alert_id": "uuid",
  "title": "Switch SW-CORE-01 offline",
  "root_cause": "Nó raiz: SW-CORE-01 (switch). 5 descendentes afetados.",
  "confidence": 0.92,
  "affected_hosts": ["uuid1", "uuid2", "uuid3"],
  "event_ids": ["uuid-e1", "uuid-e2"],
  "severity": "critical",
  "status": "open",
  "created_at": "2026-03-19T09:45:00"
}
```

---

## Topologia

### GET /api/v1/topology/nodes

Lista todos os nós de topologia.

### GET /api/v1/topology/graph

Retorna grafo completo no formato `{nodes: [...], edges: [...]}`.

**Response:**
```json
{
  "nodes": [
    {"id": "uuid", "name": "SW-CORE-01", "type": "switch", "status": "ok"}
  ],
  "edges": [
    {"source": "uuid-switch", "target": "uuid-server"}
  ]
}
```

### GET /api/v1/topology/impact/{node_id}

Retorna blast radius de um nó.

**Response:**
```json
{
  "node_id": "uuid",
  "affected_hosts": ["uuid1", "uuid2"],
  "affected_services": ["uuid-svc1"],
  "affected_applications": [],
  "total_impact": 3
}
```

---

## WebSocket

### WS /api/v1/ws/observability

Conexão WebSocket para atualizações em tempo real (≤5 segundos).

**Mensagem recebida:**
```json
{
  "type": "observability_update",
  "health_score": 87.5,
  "sensors_ok": 142,
  "sensors_critical": 3,
  "sensors_total": 155,
  "timestamp": "2026-03-19T10:00:05"
}
```

**Exemplo JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/observability');
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('Health score:', data.health_score);
};
```

---

## Probe Manager

### GET /api/v1/probe-manager/status

Status de todas as probes distribuídas.

### POST /api/v1/probe-manager/assign

Atribui um host a uma probe (weighted round-robin).

---

## Endpoints Existentes (v2 — mantidos)

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/dashboard/summary` | Resumo do dashboard |
| `GET /api/v1/servers` | Lista servidores |
| `GET /api/v1/sensors` | Lista sensores |
| `GET /api/v1/metrics` | Métricas com filtros |
| `GET /api/v1/incidents` | Incidentes |
| `GET /api/v1/aiops/analysis` | Análise AIOps v2 |
| `GET /api/v1/noc/status` | Status NOC |
| `WS /api/v1/ws/dashboard` | WebSocket dashboard v2 |
| `GET /api/v1/topology/nodes` | Nós de topologia |
| `GET /api/v1/probe-nodes` | Probe nodes distribuídas |
