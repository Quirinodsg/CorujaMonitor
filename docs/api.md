# API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require JWT authentication.

### Headers
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login and get access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "User Name",
    "role": "admin",
    "tenant_id": 1,
    "language": "pt-BR"
  }
}
```

#### POST /auth/register
Register new tenant and admin user.

**Request:**
```json
{
  "email": "admin@company.com",
  "password": "secure_password",
  "full_name": "Admin User",
  "tenant_name": "Company Name"
}
```

### Probes

#### POST /probes
Create a new probe.

**Request:**
```json
{
  "name": "Probe - Office A"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Probe - Office A",
  "token": "secure_token_here",
  "is_active": true,
  "last_heartbeat": null,
  "version": null
}
```

#### GET /probes
List all probes for current tenant.

#### POST /probes/heartbeat
Probe heartbeat (no auth required, uses probe token).

**Query Parameters:**
- `probe_token`: Probe authentication token
- `version`: Probe version

### Servers

#### POST /servers
Register a new server.

**Request:**
```json
{
  "probe_id": 1,
  "hostname": "SERVER01",
  "ip_address": "192.168.1.100",
  "os_type": "Windows",
  "os_version": "Windows Server 2022"
}
```

#### GET /servers
List all servers for current tenant.

### Sensors

#### POST /sensors
Create a new sensor.

**Request:**
```json
{
  "server_id": 1,
  "name": "CPU Usage",
  "sensor_type": "cpu",
  "threshold_warning": 80.0,
  "threshold_critical": 95.0,
  "config": {}
}
```

**Sensor Types:**
- `cpu` - CPU usage
- `memory` - Memory usage
- `disk` - Disk usage
- `network` - Network throughput
- `service` - Windows Service
- `hyperv` - Hyper-V VM
- `udm` - UDM link status

#### GET /sensors
List sensors (optionally filtered by server_id).

**Query Parameters:**
- `server_id` (optional): Filter by server

### Metrics

#### POST /metrics/bulk
Submit metrics in bulk (probe endpoint).

**Request:**
```json
{
  "probe_token": "secure_token",
  "metrics": [
    {
      "sensor_id": 1,
      "value": 45.5,
      "unit": "percent",
      "status": "ok",
      "timestamp": "2024-01-15T10:30:00Z",
      "metadata": {}
    }
  ]
}
```

#### GET /metrics
Get metrics for a sensor.

**Query Parameters:**
- `sensor_id` (required): Sensor ID
- `start_time` (optional): Start timestamp
- `end_time` (optional): End timestamp
- `limit` (optional): Max results (default: 100)

### Incidents

#### GET /incidents
List incidents.

**Query Parameters:**
- `status` (optional): Filter by status (open, acknowledged, resolved, auto_resolved)
- `severity` (optional): Filter by severity (warning, critical)
- `limit` (optional): Max results (default: 100)

#### GET /incidents/{incident_id}
Get incident details.

#### GET /incidents/{incident_id}/remediation
Get remediation logs for an incident.

### Dashboard

#### GET /dashboard/overview
Get dashboard overview statistics.

**Response:**
```json
{
  "total_servers": 30,
  "total_sensors": 150,
  "open_incidents": 5,
  "critical_incidents": 2,
  "recent_incidents_24h": 8,
  "auto_resolved_30d": 45,
  "health_status": "warning"
}
```

#### GET /dashboard/health-summary
Get health summary by status.

**Response:**
```json
{
  "healthy": 120,
  "warning": 25,
  "critical": 5,
  "unknown": 0
}
```

### Reports

#### GET /reports/monthly
List monthly reports.

**Query Parameters:**
- `year` (optional): Filter by year

#### GET /reports/monthly/{year}/{month}
Get specific monthly report.

**Response:**
```json
{
  "id": 1,
  "year": 2024,
  "month": 1,
  "availability_percentage": 99.87,
  "total_incidents": 45,
  "auto_resolved_incidents": 38,
  "sla_compliance": 99.5,
  "report_data": {},
  "ai_summary": "Durante janeiro de 2024...",
  "generated_at": "2024-02-01T00:00:00Z"
}
```

## AI Agent API

### Base URL
```
http://localhost:8001/api/v1
```

### POST /analyze/root-cause
Request root cause analysis.

### POST /analyze/monthly-summary
Generate monthly summary.

### POST /analyze/anomaly
Detect anomalies in metrics.

### POST /analyze/recommendation
Get preventive recommendations.

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, implement rate limiting at the reverse proxy level.

## Pagination

For endpoints returning lists, use `limit` parameter to control result size. Future versions will include cursor-based pagination.
