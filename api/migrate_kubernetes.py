"""
Migração para adicionar tabelas de monitoramento Kubernetes
Data: 27 FEV 2026
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import engine
from models import Base, KubernetesCluster, KubernetesResource, KubernetesMetric

def migrate():
    print("🚀 Iniciando migração Kubernetes...")
    
    try:
        # Criar tabelas
        print("📊 Criando tabelas...")
        Base.metadata.create_all(bind=engine, tables=[
            KubernetesCluster.__table__,
            KubernetesResource.__table__,
            KubernetesMetric.__table__
        ])
        
        print("✅ Tabelas criadas com sucesso!")
        print("")
        print("Tabelas criadas:")
        print("  - kubernetes_clusters")
        print("  - kubernetes_resources")
        print("  - kubernetes_metrics")
        print("")
        print("🎉 Migração concluída!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        raise

if __name__ == "__main__":
    migrate()
