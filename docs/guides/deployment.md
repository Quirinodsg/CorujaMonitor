# Deployment Guide

## Local Windows Deployment

### Prerequisites
- Windows 10/11 or Windows Server 2016+
- Docker Desktop for Windows
- Python 3.11+
- Node.js 18+
- 8GB RAM minimum
- 50GB disk space

### Quick Start

1. **Clone Repository**
```cmd
git clone https://github.com/your-org/coruja-monitor.git
cd coruja-monitor
```

2. **Configure Environment**
```cmd
copy .env.example .env
```

Edit `.env` and configure:
- Database credentials
- OpenAI API key (or Ollama URL)
- Secret keys

3. **Start Services**
```cmd
docker compose up --build
```

4. **Access Dashboard**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

5. **Create Admin User**
```cmd
docker exec -it coruja-api python -c "
from database import SessionLocal
from models import User, Tenant
from auth import get_password_hash

db = SessionLocal()
tenant = Tenant(name='Default', slug='default')
db.add(tenant)
db.flush()

user = User(
    email='admin@coruja.local',
    hashed_password=get_password_hash('admin123'),
    full_name='Administrator',
    tenant_id=tenant.id,
    role='admin'
)
db.add(user)
db.commit()
print('Admin user created: admin@coruja.local / admin123')
"
```

### Probe Installation

See `probe/README.md` for detailed probe installation instructions.

## Production Deployment

### Docker Compose (Single Server)

1. **Update docker-compose.yml**
   - Remove `--reload` flags
   - Configure resource limits
   - Set up volumes for persistence

2. **Configure Reverse Proxy**
   - Use Nginx or Traefik
   - Enable HTTPS with Let's Encrypt
   - Configure rate limiting

3. **Database Backup**
```cmd
docker exec coruja-postgres pg_dump -U coruja coruja_monitor > backup.sql
```

### Azure Deployment (Future)

#### Architecture
```
Azure Application Gateway (HTTPS)
    ↓
Azure Kubernetes Service (AKS)
    ├── API Pods (3+ replicas)
    ├── Worker Pods (2+ replicas)
    ├── AI Agent Pods (2+ replicas)
    └── Frontend Pods (2+ replicas)
    ↓
Azure Database for PostgreSQL (Flexible Server)
Azure Redis Cache
Azure Container Registry
Azure Monitor + Application Insights
```

#### Steps

1. **Create Azure Resources**
```bash
az group create --name coruja-rg --location eastus
az aks create --resource-group coruja-rg --name coruja-aks --node-count 3
az postgres flexible-server create --resource-group coruja-rg --name coruja-db
az redis create --resource-group coruja-rg --name coruja-redis --sku Basic
```

2. **Build and Push Images**
```bash
az acr create --resource-group coruja-rg --name corujaacr --sku Basic
docker tag coruja-api corujaacr.azurecr.io/api:latest
docker push corujaacr.azurecr.io/api:latest
```

3. **Deploy to AKS**
```bash
kubectl apply -f k8s/
```

4. **Configure Ingress**
```bash
kubectl apply -f k8s/ingress.yaml
```

## Monitoring & Maintenance

### Health Checks
- API: http://localhost:8000/health
- AI Agent: http://localhost:8001/health

### Logs
```cmd
docker logs coruja-api
docker logs coruja-worker
docker logs coruja-ai-agent
```

### Database Maintenance
```sql
-- Partition old metrics
CREATE TABLE metrics_2024_01 PARTITION OF metrics
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Clean old metrics
DELETE FROM metrics WHERE timestamp < NOW() - INTERVAL '90 days';
```

### Backup Strategy
- Daily database backups
- Weekly full system backup
- Offsite backup storage
- Test restore procedures monthly

## Scaling

### Horizontal Scaling
```cmd
docker compose up --scale api=3 --scale worker=2
```

### Database Optimization
- Enable connection pooling
- Configure indexes
- Partition metrics table by date
- Archive old data

## Troubleshooting

### API Not Starting
```cmd
docker logs coruja-api
docker exec -it coruja-api python -c "from database import engine; print(engine.url)"
```

### Worker Not Processing
```cmd
docker logs coruja-worker
docker exec -it coruja-redis redis-cli ping
```

### Probe Connection Issues
- Verify API URL in probe config
- Check firewall rules
- Validate probe token
- Review probe.log

## Security Checklist

- [ ] Change default passwords
- [ ] Configure HTTPS
- [ ] Enable firewall rules
- [ ] Rotate JWT secret keys
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup encryption
