-- Criar Tabelas de Alertas Kubernetes
-- Data: 27 FEV 2026

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

CREATE INDEX IF NOT EXISTS idx_k8s_alerts_cluster ON kubernetes_alerts(cluster_id);
CREATE INDEX IF NOT EXISTS idx_k8s_alerts_status ON kubernetes_alerts(status);
CREATE INDEX IF NOT EXISTS idx_k8s_alerts_severity ON kubernetes_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_k8s_alerts_created ON kubernetes_alerts(created_at);

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

CREATE INDEX IF NOT EXISTS idx_k8s_alert_rules_tenant ON kubernetes_alert_rules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_k8s_alert_rules_active ON kubernetes_alert_rules(is_active);

-- Inserir regras padrão (apenas se não existirem)
INSERT INTO kubernetes_alert_rules (tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration)
SELECT 1, 'Node NotReady', 'Alerta quando um node fica NotReady', 'node_not_ready', 'critical', 'node', 'ready', 'eq', 0, 300
WHERE NOT EXISTS (SELECT 1 FROM kubernetes_alert_rules WHERE alert_type = 'node_not_ready');

INSERT INTO kubernetes_alert_rules (tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration)
SELECT 1, 'High CPU Usage (Node)', 'Alerta quando CPU do node > 90%', 'high_cpu', 'warning', 'node', 'node_cpu_usage', 'gt', 90.0, 300
WHERE NOT EXISTS (SELECT 1 FROM kubernetes_alert_rules WHERE alert_type = 'high_cpu' AND resource_type = 'node');

INSERT INTO kubernetes_alert_rules (tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration)
SELECT 1, 'High Memory Usage (Node)', 'Alerta quando memória do node > 90%', 'high_memory', 'warning', 'node', 'node_memory_usage', 'gt', 90.0, 300
WHERE NOT EXISTS (SELECT 1 FROM kubernetes_alert_rules WHERE alert_type = 'high_memory' AND resource_type = 'node');

INSERT INTO kubernetes_alert_rules (tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration)
SELECT 1, 'Pod CrashLoopBackOff', 'Alerta quando pod tem muitos restarts', 'pod_crashloop', 'critical', 'pod', 'pod_restart_count', 'gt', 5, 600
WHERE NOT EXISTS (SELECT 1 FROM kubernetes_alert_rules WHERE alert_type = 'pod_crashloop');

INSERT INTO kubernetes_alert_rules (tenant_id, name, description, alert_type, severity, resource_type, metric_name, operator, threshold, duration)
SELECT 1, 'Deployment Unhealthy', 'Alerta quando deployment não tem réplicas prontas', 'deployment_unhealthy', 'warning', 'deployment', 'ready_replicas', 'lt', 1, 300
WHERE NOT EXISTS (SELECT 1 FROM kubernetes_alert_rules WHERE alert_type = 'deployment_unhealthy');
