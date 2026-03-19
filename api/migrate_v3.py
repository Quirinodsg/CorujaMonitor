"""
Migração DDL v3.0 — Coruja Monitor v3.0

Cria:
  - metrics_ts (hypertable TimescaleDB, retention 90 dias, compressão 7 dias)
  - ai_feedback_actions
  - topology_nodes
  - intelligent_alerts

Execução:
  python3 api/migrate_v3.py
  ou automaticamente via api/main.py na inicialização
"""
import logging
import os
import sys

logger = logging.getLogger(__name__)


DDL_METRICS_TS = """
CREATE TABLE IF NOT EXISTS metrics_ts (
    time            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    sensor_id       INTEGER         NOT NULL,
    server_id       INTEGER         NOT NULL,
    sensor_type     VARCHAR(100)    NOT NULL,
    value           DOUBLE PRECISION NOT NULL,
    unit            VARCHAR(50)     DEFAULT '',
    status          VARCHAR(20)     DEFAULT 'ok',
    labels          JSONB           DEFAULT '{}'
);
"""

DDL_METRICS_TS_HYPERTABLE = """
SELECT create_hypertable('metrics_ts', 'time', if_not_exists => TRUE);
"""

DDL_METRICS_TS_RETENTION = """
SELECT add_retention_policy('metrics_ts', INTERVAL '90 days', if_not_exists => TRUE);
"""

DDL_METRICS_TS_COMPRESSION = """
ALTER TABLE metrics_ts SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id'
);
"""

DDL_METRICS_TS_COMPRESSION_POLICY = """
SELECT add_compression_policy('metrics_ts', INTERVAL '7 days', if_not_exists => TRUE);
"""

DDL_AI_FEEDBACK_ACTIONS = """
CREATE TABLE IF NOT EXISTS ai_feedback_actions (
    action_id               UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name              VARCHAR(100)    NOT NULL,
    action_type             VARCHAR(100)    NOT NULL,
    target_host             VARCHAR(255)    NOT NULL,
    timestamp               TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    result                  VARCHAR(50)     DEFAULT 'pending',
    resolution_time_seconds DOUBLE PRECISION,
    outcome                 VARCHAR(50),
    metadata                JSONB           DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_ai_feedback_agent_name
    ON ai_feedback_actions (agent_name);

CREATE INDEX IF NOT EXISTS idx_ai_feedback_timestamp
    ON ai_feedback_actions (timestamp DESC);
"""

DDL_TOPOLOGY_NODES = """
CREATE TABLE IF NOT EXISTS topology_nodes (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    type        VARCHAR(50) NOT NULL,
    parent_id   UUID        REFERENCES topology_nodes(id) ON DELETE SET NULL,
    metadata    JSONB       DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_topology_nodes_parent
    ON topology_nodes (parent_id);

CREATE INDEX IF NOT EXISTS idx_topology_nodes_type
    ON topology_nodes (type);
"""

DDL_INTELLIGENT_ALERTS = """
CREATE TABLE IF NOT EXISTS intelligent_alerts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    event_ids       UUID[]      DEFAULT '{}',
    title           TEXT        NOT NULL,
    severity        VARCHAR(20) NOT NULL DEFAULT 'warning',
    status          VARCHAR(20) NOT NULL DEFAULT 'open',
    root_cause      TEXT,
    affected_hosts  UUID[]      DEFAULT '{}',
    root_cause_node UUID        REFERENCES topology_nodes(id) ON DELETE SET NULL,
    confidence      DOUBLE PRECISION DEFAULT 0.0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_intelligent_alerts_status
    ON intelligent_alerts (status);

CREATE INDEX IF NOT EXISTS idx_intelligent_alerts_severity
    ON intelligent_alerts (severity);

CREATE INDEX IF NOT EXISTS idx_intelligent_alerts_created_at
    ON intelligent_alerts (created_at DESC);
"""


def run_migration(conn):
    """Executa todas as migrações DDL v3."""
    cursor = conn.cursor()

    steps = [
        ("metrics_ts table", DDL_METRICS_TS),
        ("ai_feedback_actions table", DDL_AI_FEEDBACK_ACTIONS),
        ("topology_nodes table", DDL_TOPOLOGY_NODES),
        ("intelligent_alerts table", DDL_INTELLIGENT_ALERTS),
    ]

    for name, ddl in steps:
        try:
            cursor.execute(ddl)
            conn.commit()
            logger.info(f"migrate_v3: ✓ {name}")
        except Exception as e:
            conn.rollback()
            logger.error(f"migrate_v3: ✗ {name}: {e}")

    # TimescaleDB — executar separadamente (pode falhar se extensão não instalada)
    timescale_steps = [
        ("metrics_ts hypertable", DDL_METRICS_TS_HYPERTABLE),
        ("metrics_ts retention policy", DDL_METRICS_TS_RETENTION),
        ("metrics_ts compression", DDL_METRICS_TS_COMPRESSION),
        ("metrics_ts compression policy", DDL_METRICS_TS_COMPRESSION_POLICY),
    ]

    for name, ddl in timescale_steps:
        try:
            cursor.execute(ddl)
            conn.commit()
            logger.info(f"migrate_v3: ✓ {name} (TimescaleDB)")
        except Exception as e:
            conn.rollback()
            logger.warning(f"migrate_v3: ⚠ {name} (TimescaleDB não disponível ou já configurado): {e}")

    cursor.close()
    logger.info("migrate_v3: migração DDL v3 concluída")


def get_connection():
    import psycopg2
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "coruja_monitor"),
        user=os.getenv("POSTGRES_USER", "coruja"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )


def migrate():
    """Entry point para execução standalone."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        conn = get_connection()
        run_migration(conn)
        conn.close()
        print("migrate_v3: OK")
    except Exception as e:
        print(f"migrate_v3: ERRO — {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    migrate()
