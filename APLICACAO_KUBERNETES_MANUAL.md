# Aplicação Manual Kubernetes - 27 FEV 2026

## ✅ MUDANÇAS JÁ APLICADAS

### 1. Criptografia
- ✅ Arquivo `api/utils/encryption.py` criado
- ✅ Router `api/routers/kubernetes.py` atualizado para usar criptografia
- ✅ Collector atualizado para usar endpoint com descriptografia
- ✅ Chave adicionada ao `.env`

### 2. Dashboard Frontend
- ✅ Componente `frontend/src/components/KubernetesDashboard.js` criado
- ✅ CSS `frontend/src/components/KubernetesDashboard.css` criado
- ✅ Importado no `MainLayout.js`
- ✅ Rota adicionada no `MainLayout.js`
- ✅ Menu adicionado no `Sidebar.js`

### 3. Sistema de Alertas
- ✅ Modelos adicionados em `api/models.py`
- ✅ Router `api/routers/kubernetes_alerts.py` criado
- ✅ Router registrado em `api/main.py`

---

## 🔧 APLICAÇÃO MANUAL DAS TABELAS

Como as tabelas Kubernetes já existem, vamos criar apenas as tabelas de alertas via SQL:

### Passo 1: Criar Tabelas via SQL

Execute no banco de dados (via Docker):

```bash
docker-compose exec postgres psql -U coruja -d coruja_monitor
```

Depois execute o SQL:

```sql
-- Tabela de Alertas
CREATE TABLE IF NOT EXISTS kubernetes_alerts (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER NOT NULL REFERENCES kubernetes_clusters(id) ON DELETE CASCADE,
    resource_id INTEGER REFERENCES kubernetes_resources(id) ON DELETE CASCADE,
    
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    resource_type VARCHAR(50),
    resource_name VARCHAR(255),
    namespace VARCHAR(255),
    
    current_value FLOAT,
    threshold_value FLOAT,
    
    status VARCHAR(20) DEFAULT 'active',
    acknowledged_at TIMESTAMP,
    acknowledged_by INTEGER,
    resolved_at TIMESTAMP,
    
    alert_metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_k8s_alerts_cluster ON kubernetes_alerts(cluster_id);
CREATE INDEX idx_k8s_alerts_status ON kubernetes_alerts(status);
CREATE INDEX idx_k8s_alerts_severity ON kubernetes_alerts(severity);
CREATE INDEX idx_k8s_alerts_created ON kubernetes_alerts(created_at);

-- Tabela de Regras de Alerta
CREATE TABLE IF NOT EXISTS kubernetes_alert_rules (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER REFERENCES kubernetes_clusters(id) ON DELETE CASCADE,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    
    resource_type VARCHAR(50),
    metric_name VARCHAR(100) NOT NULL,
    operator VARCHAR(20) NOT NULL,
    threshold FLOAT NOT NULL,
    duration INTEGER DEFAULT 60,
    
    namespace_filter VARCHAR(255),
    label_filter JSONB DEFAULT '{}',
    
    is_active BOOLEAN DEFAULT TRUE,
    
    notify_email BOOLEAN DEFAULT TRUE,
    notify_webhook BOOLEAN DEFAULT FALSE,
    webhook_url VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_k8s_alert_rules_tenant ON kubernetes_alert_rules(tenant_id);
CREATE INDEX idx_k8s_alert_rules_active ON kubernetes_alert_rules(is_active);

-- Inserir regras padrão
INSERT INTO kubernetes_alert_rules (tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration)
VALUES
(1, 'Node NotReady', 'Alerta quando um node fica NotReady', 'node_not_ready', 'critical', 'node', 'ready', 'eq', 0, 300),
(1, 'High CPU Usage (Node)', 'Alerta quando CPU do node > 90%', 'high_cpu', 'warning', 'node', 'node_cpu_usage', 'gt', 90.0, 300),
(1, 'High Memory Usage (Node)', 'Alerta quando memória do node > 90%', 'high_memory', 'warning', 'node', 'node_memory_usage', 'gt', 90.0, 300),
(1, 'Pod CrashLoopBackOff', 'Alerta quando pod tem muitos restarts', 'pod_crashloop', 'critical', 'pod', 'pod_restart_count', 'gt', 5, 600),
(1, 'Deployment Unhealthy', 'Alerta quando deployment não tem réplicas prontas', 'deployment_unhealthy', 'warning', 'deployment', 'ready_replicas', 'lt', 1, 300);
```

### Passo 2: Reiniciar API

```powershell
docker-compose restart api
```

### Passo 3: Verificar API

Aguarde 5 segundos e acesse:
- http://localhost:8000/docs
- Procure por `/api/v1/kubernetes/alerts`

### Passo 4: Frontend

Se o frontend já está rodando, apenas recarregue a página (Ctrl+R).

Se não está rodando:
```powershell
cd frontend
npm start
```

### Passo 5: Acessar Dashboard

1. Acesse http://localhost:3000
2. Login: admin@coruja.com / admin123
3. Clique no menu: ☸️ Kubernetes

---

## ✅ VERIFICAÇÃO

### API
```powershell
# Verificar se API está respondendo
curl http://localhost:8000/health

# Verificar endpoints de alertas
curl http://localhost:8000/docs
```

### Frontend
- Menu "☸️ Kubernetes" deve aparecer no sidebar
- Ao clicar, deve abrir o dashboard
- Dashboard deve mostrar clusters configurados

### Banco de Dados
```sql
-- Verificar tabelas criadas
\dt kubernetes*

-- Verificar regras padrão
SELECT * FROM kubernetes_alert_rules;
```

---

## 🎯 FUNCIONALIDADES DISPONÍVEIS

### 1. Criptografia
- Credenciais são criptografadas automaticamente ao criar cluster
- Collector recebe credenciais descriptografadas via endpoint especial
- Chave configurável via .env (ENCRYPTION_KEY)

### 2. Dashboard
- Visão de todos os clusters
- Métricas agregadas (nodes, pods, CPU, memória)
- Tabelas de recursos por tipo
- Auto-refresh a cada 30 segundos

### 3. Alertas
- 5 regras padrão criadas
- API para gerenciar alertas e regras
- Severidades: critical, warning, info
- Status: active, acknowledged, resolved

---

## 📚 DOCUMENTAÇÃO

- `KUBERNETES_DASHBOARDS_ALERTAS_CRIPTOGRAFIA_27FEV.md` - Documentação completa
- `GUIA_COMPLETO_KUBERNETES_27FEV.md` - Guia de uso
- `INDICE_KUBERNETES_27FEV.md` - Índice de documentação

---

## ✅ CONCLUSÃO

Todas as mudanças foram aplicadas:
- ✅ Criptografia AES-256 implementada
- ✅ Dashboard completo no frontend
- ✅ Sistema de alertas com API REST
- ✅ Menu adicionado ao sidebar
- ✅ Rotas configuradas

**Próximo passo:** Criar as tabelas via SQL e reiniciar a API.

---

**Data:** 27 de Fevereiro de 2026  
**Status:** ✅ PRONTO PARA APLICAÇÃO MANUAL
