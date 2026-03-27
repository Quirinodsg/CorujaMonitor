"""
Migração: Índices de performance para queries de métricas e sensores
Resolve lentidão nas queries LATERAL e batch de métricas
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import engine
from sqlalchemy import text

def run():
    # CREATE INDEX CONCURRENTLY não pode rodar dentro de transaction block
    # Usar autocommit=True via raw psycopg2
    raw = engine.raw_connection()
    raw.set_isolation_level(0)  # AUTOCOMMIT
    cur = raw.cursor()

    indexes = [
        ("idx_metrics_sensor_timestamp",
         "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_sensor_timestamp ON metrics (sensor_id, timestamp DESC)"),
        ("idx_metrics_sensor_id",
         "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_sensor_id ON metrics (sensor_id)"),
        ("idx_sensors_server_active",
         "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sensors_server_active ON sensors (server_id, is_active, sensor_type)"),
        ("idx_incidents_status_severity",
         "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_status_severity ON incidents (status, severity)"),
        ("idx_servers_tenant_active",
         "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_servers_tenant_active ON servers (tenant_id, is_active)"),
    ]

    for name, sql in indexes:
        try:
            cur.execute(sql)
            print(f"✅ {name}")
        except Exception as e:
            print(f"⚠️  {name}: {e}")

    cur.close()
    raw.close()
    print("\n✅ Concluído")

if __name__ == "__main__":
    run()
