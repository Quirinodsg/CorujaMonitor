"""
Migração: cria tabela topology_edges para persistir relações do grafo.
Execução: docker-compose exec api python3 migrate_topology_edges.py
"""
import os, sys, logging, psycopg2

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DDL = """
CREATE TABLE IF NOT EXISTS topology_edges (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id   UUID        NOT NULL REFERENCES topology_nodes(id) ON DELETE CASCADE,
    target_id   UUID        NOT NULL REFERENCES topology_nodes(id) ON DELETE CASCADE,
    type        VARCHAR(50) NOT NULL DEFAULT 'dependency',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_id, target_id)
);

CREATE INDEX IF NOT EXISTS idx_topology_edges_source ON topology_edges (source_id);
CREATE INDEX IF NOT EXISTS idx_topology_edges_target ON topology_edges (target_id);
"""

def migrate():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "coruja_monitor"),
        user=os.getenv("POSTGRES_USER", "coruja"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    cur = conn.cursor()
    try:
        cur.execute(DDL)
        conn.commit()
        logger.info("✓ topology_edges criada")
        print("migrate_topology_edges: OK")
    except Exception as e:
        conn.rollback()
        logger.error(f"✗ {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
