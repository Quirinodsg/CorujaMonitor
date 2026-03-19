"""
Migração: tabela ai_agent_logs para o pipeline v3.
Execução: python3 api/migrate_aiops_pipeline.py
"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DDL = """
CREATE TABLE IF NOT EXISTS ai_agent_logs (
    id              BIGSERIAL       PRIMARY KEY,
    run_id          UUID            NOT NULL DEFAULT gen_random_uuid(),
    agent_name      VARCHAR(100)    NOT NULL,
    input           JSONB           DEFAULT '{}',
    output          JSONB           DEFAULT '{}',
    status          VARCHAR(20)     NOT NULL DEFAULT 'success',
    error           TEXT,
    duration_ms     INTEGER,
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_agent_logs_run_id   ON ai_agent_logs (run_id);
CREATE INDEX IF NOT EXISTS idx_ai_agent_logs_agent    ON ai_agent_logs (agent_name);
CREATE INDEX IF NOT EXISTS idx_ai_agent_logs_ts       ON ai_agent_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_agent_logs_status   ON ai_agent_logs (status);
"""

def migrate():
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "coruja_monitor"),
        user=os.getenv("POSTGRES_USER", "coruja"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    cur = conn.cursor()
    cur.execute(DDL)
    conn.commit()
    cur.close()
    conn.close()
    logger.info("migrate_aiops_pipeline: ✓ ai_agent_logs criada")
    print("migrate_aiops_pipeline: OK")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
