"""
Migração para Alertas Kubernetes
Data: 27 FEV 2026
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Usar variáveis de ambiente do Docker se disponíveis
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "coruja")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

Base = declarative_base()

class KubernetesAlert(Base):
    """Alertas de Kubernetes"""
    __tablename__ = "kubernetes_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("kubernetes_resources.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Tipo e severidade
    alert_type = Column(String(50), nullable=False, index=True)  # node_down, pod_crashloop, high_cpu, etc
    severity = Column(String(20), nullable=False, index=True)  # critical, warning, info
    
    # Detalhes
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_name = Column(String(255), nullable=True)
    namespace = Column(String(255), nullable=True)
    
    # Métricas
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), default="active", index=True)  # active, acknowledged, resolved
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(Integer, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Metadados
    alert_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KubernetesAlertRule(Base):
    """Regras de Alerta para Kubernetes"""
    __tablename__ = "kubernetes_alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Configuração da regra
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Condições
    resource_type = Column(String(50), nullable=True)  # node, pod, deployment, etc
    metric_name = Column(String(100), nullable=False)  # cpu_usage, memory_usage, restart_count, etc
    operator = Column(String(20), nullable=False)  # gt, lt, eq, gte, lte
    threshold = Column(Float, nullable=False)
    duration = Column(Integer, default=60)  # Duração em segundos antes de alertar
    
    # Filtros
    namespace_filter = Column(String(255), nullable=True)
    label_filter = Column(JSON, default={})
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Notificações
    notify_email = Column(Boolean, default=True)
    notify_webhook = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def migrate():
    """Executar migração"""
    print("Iniciando migração de alertas Kubernetes...")
    
    engine = create_engine(DATABASE_URL)
    
    # Criar tabelas
    Base.metadata.create_all(engine)
    
    print("✅ Tabelas criadas:")
    print("  - kubernetes_alerts")
    print("  - kubernetes_alert_rules")
    
    # Criar regras padrão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verificar se já existem regras
        existing_rules = session.query(KubernetesAlertRule).count()
        
        if existing_rules == 0:
            print("\nCriando regras de alerta padrão...")
            
            default_rules = [
                {
                    "name": "Node NotReady",
                    "description": "Alerta quando um node fica NotReady",
                    "alert_type": "node_not_ready",
                    "severity": "critical",
                    "resource_type": "node",
                    "metric_name": "ready",
                    "operator": "eq",
                    "threshold": 0,
                    "duration": 300,
                    "tenant_id": 1
                },
                {
                    "name": "High CPU Usage (Node)",
                    "description": "Alerta quando CPU do node > 90%",
                    "alert_type": "high_cpu",
                    "severity": "warning",
                    "resource_type": "node",
                    "metric_name": "node_cpu_usage",
                    "operator": "gt",
                    "threshold": 90.0,
                    "duration": 300,
                    "tenant_id": 1
                },
                {
                    "name": "High Memory Usage (Node)",
                    "description": "Alerta quando memória do node > 90%",
                    "alert_type": "high_memory",
                    "severity": "warning",
                    "resource_type": "node",
                    "metric_name": "node_memory_usage",
                    "operator": "gt",
                    "threshold": 90.0,
                    "duration": 300,
                    "tenant_id": 1
                },
                {
                    "name": "Pod CrashLoopBackOff",
                    "description": "Alerta quando pod tem muitos restarts",
                    "alert_type": "pod_crashloop",
                    "severity": "critical",
                    "resource_type": "pod",
                    "metric_name": "pod_restart_count",
                    "operator": "gt",
                    "threshold": 5,
                    "duration": 600,
                    "tenant_id": 1
                },
                {
                    "name": "Deployment Unhealthy",
                    "description": "Alerta quando deployment não tem réplicas prontas",
                    "alert_type": "deployment_unhealthy",
                    "severity": "warning",
                    "resource_type": "deployment",
                    "metric_name": "ready_replicas",
                    "operator": "lt",
                    "threshold": 1,
                    "duration": 300,
                    "tenant_id": 1
                }
            ]
            
            for rule_data in default_rules:
                rule = KubernetesAlertRule(**rule_data)
                session.add(rule)
            
            session.commit()
            print(f"✅ {len(default_rules)} regras padrão criadas")
        else:
            print(f"\n⚠️  {existing_rules} regras já existem, pulando criação de regras padrão")
        
    except Exception as e:
        print(f"❌ Erro ao criar regras padrão: {e}")
        session.rollback()
    finally:
        session.close()
    
    print("\n✅ Migração concluída com sucesso!")


if __name__ == "__main__":
    migrate()
