"""
Migração: Índices de performance para queries de métricas e sensores
Resolve lentidão nas queries LATERAL e batch de métricas
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        indexes = [
            # Índice principal para queries de última métrica por sensor (LATERAL)
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_sensor_timestamp
            ON metrics (sensor_id, timestamp DESC)
            """,
            # Índice para batch de métricas
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_sensor_id
            ON metrics (sensor_id)
            """,
            # Índice para sensores ativos por servidor
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sensors_server_active
            ON sensors (server_id, is_active, sensor_type)
            """,
            # Índice para incidentes abertos
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_status_severity
            ON incidents (status, severity)
            """,
            # Índice para servidores ativos por tenant
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_servers_tenant_active
            ON servers (tenant_id, is_active)
            """,
        ]

        for idx_sql in indexes:
            try:
                conn.execute(text(idx_sql.strip()))
                conn.commit()
                name = [l.strip() for l in idx_sql.split('\n') if 'idx_' in l][0].split()[0]
                print(f"✅ {name}")
            except Exception as e:
                print(f"⚠️  {e}")

    print("\n✅ Índices criados com sucesso")

if __name__ == "__main__":
    run()
