# Coruja Monitor - Architecture

## Overview

Coruja Monitor is a microservices-based enterprise monitoring platform designed for multi-tenant environments with distributed probe architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                     Port 3000 (Dashboard)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Service (FastAPI)                     │
│                         Port 8000                            │
│  - Authentication & Authorization (JWT)                      │
│  - Multi-tenant Management                                   │
│  - Probe Registration                                        │
│  - Metrics Ingestion                                         │
│  - Dashboard Backend                                         │
└──────┬──────────────────────────┬───────────────────────────┘
       │                          │
       ▼                          ▼
┌─────────────────┐      ┌──────────────────────────┐
│   PostgreSQL    │      │    Redis (Message Queue)  │
│   Port 5432     │      │       Port 6379           │
└─────────────────┘      └────────┬─────────────────┘
                                  │
                                  ▼
                         ┌────────────────────────────┐
                         │  Worker Service (Celery)   │
                         │  - Threshold Evaluation    │
                         │  - Incident Creation       │
                         │  - Self-Healing Logic      │
                         │  - SLA Calculation         │
                         └────────┬───────────────────┘
                                  │
                                  ▼
                         ┌────────────────────────────┐
                         │   AI Agent (FastAPI)       │
                         │      Port 8001             │
                         │  - Root Cause Analysis     │
                         │  - Anomaly Detection       │
                         │  - Recommendations         │
                         │  - Monthly Summaries       │
                         └────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Distributed Probes                        │
│                  (Windows Services)                          │
│                                                              │
│  Client A Network          Client B Network                 │
│  ┌──────────────┐          ┌──────────────┐                │
│  │ Probe A      │          │ Probe B      │                │
│  │ - 30 Servers │          │ - 50 Servers │                │
│  │ - Collectors │          │ - Collectors │                │
│  └──────────────┘          └──────────────┘                │
│         │                          │                         │
│         └──────────HTTPS───────────┘                        │
│                    │                                         │
│                    ▼                                         │
│            API Service (Metrics Endpoint)                    │
└─────────────────────────────────────────────────────────────┘
```

## Microservices

### 1. API Service
- **Technology**: FastAPI (Python)
- **Responsibilities**:
  - REST API endpoints
  - JWT authentication
  - Multi-tenant isolation
  - Probe management
  - Metrics ingestion
  - Dashboard data aggregation
- **Scalability**: Stateless, horizontally scalable

### 2. Worker Service
- **Technology**: Celery (Python)
- **Responsibilities**:
  - Asynchronous metric processing
  - Threshold evaluation (every minute)
  - Incident creation
  - Self-healing execution
  - Monthly SLA calculation
- **Scalability**: Multiple workers can run in parallel

### 3. AI Agent Service
- **Technology**: FastAPI + OpenAI/Ollama
- **Responsibilities**:
  - Root cause analysis
  - Anomaly detection
  - Preventive recommendations
  - Executive report generation
- **Scalability**: Independent service, can be scaled separately

### 4. Probe (Distributed)
- **Technology**: Python Windows Service
- **Responsibilities**:
  - Local metric collection
  - Service monitoring
  - Hyper-V monitoring
  - UDM link monitoring
  - Local buffering
  - Secure communication with API
- **Deployment**: One per client network

## Data Flow

### Metric Collection Flow
1. Probe collects metrics every 60 seconds
2. Metrics buffered locally
3. Batch sent to API `/api/v1/metrics/bulk`
4. API stores in PostgreSQL
5. Worker evaluates thresholds
6. If threshold breached → Create incident
7. Worker attempts self-healing
8. AI Agent analyzes root cause
9. Dashboard displays real-time status

### Incident Flow
1. Worker detects threshold breach
2. Create incident in database
3. Trigger self-healing task
4. Log remediation attempt
5. Request AI analysis
6. AI Agent provides root cause
7. Update incident with analysis
8. Dashboard shows incident with AI insights

## Database Schema

### Core Tables
- `tenants` - Multi-tenant isolation
- `users` - User authentication
- `probes` - Registered probes
- `servers` - Monitored servers
- `sensors` - Individual metrics
- `metrics` - Time-series data (partitioned)
- `incidents` - Alert incidents
- `remediation_logs` - Self-healing actions
- `ai_analysis_logs` - AI analysis history
- `monthly_reports` - SLA reports
- `audit_logs` - Audit trail

## Security

### Authentication
- JWT tokens for API access
- Secure probe tokens
- Role-based access control (RBAC)

### Communication
- HTTPS for probe-to-API
- Encrypted probe tokens
- Environment-based secrets

### Multi-tenancy
- Tenant isolation at database level
- Row-level security
- Tenant-scoped queries

## Scalability

### Current Capacity
- 5,000+ sensors per instance
- Multiple probes per tenant
- Horizontal scaling ready

### Future Azure Deployment
- Azure Kubernetes Service (AKS)
- Azure Database for PostgreSQL
- Azure Redis Cache
- Azure Container Registry
- Azure Application Gateway
- Azure Monitor integration

## Monitoring Features

### Infrastructure
- CPU, Memory, Disk, Network
- Windows Services
- Hyper-V VMs
- Cluster status
- UDM links

### Self-Healing
- Automatic service restart
- Disk cleanup analysis
- Memory optimization
- Configurable remediation

### AI Capabilities
- Root cause analysis
- Anomaly detection
- Preventive recommendations
- Executive summaries

## Technology Stack

- **Backend**: Python 3.11, FastAPI, Celery
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **AI**: OpenAI API / Ollama
- **Frontend**: React 18
- **Containerization**: Docker, Docker Compose
- **Probe**: Python Windows Service
