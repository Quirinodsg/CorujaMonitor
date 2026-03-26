"""
Migração DDL — Hyper-V Observability Dashboard

Cria:
  - hyperv_hosts (hosts Hyper-V monitorados)
  - hyperv_vms (máquinas virtuais por host)
  - hyperv_metrics (métricas time-series de hosts e VMs)
  - hyperv_finops_recommendations (recomendações FinOps)

Execução:
  python3 api/migrate_hyperv.py
"""
import logging
import os
import sys

logger = logging.getLogger(__name__)


DDL_HYPERV_HOSTS = """
CREATE TABLE IF NOT EXISTS hyperv_hosts (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    hostname            VARCHAR(255)    NOT NULL,
    ip_address          VARCHAR(50)     NOT NULL,
    total_cpus          INTEGER         NOT NULL,
    total_memory_gb     DOUBLE PRECISION NOT NULL,
    total_storage_gb    DOUBLE PRECISION NOT NULL,
    cpu_percent         DOUBLE PRECISION,
    memory_percent      DOUBLE PRECISION,
    storage_percent     DOUBLE PRECISION,
    vm_count            INTEGER         DEFAULT 0,
    running_vm_count    INTEGER         DEFAULT 0,
    status              VARCHAR(20)     DEFAULT 'unknown',
    health_score        DOUBLE PRECISION DEFAULT 0,
    wmi_latency_ms      DOUBLE PRECISION,
    last_seen           TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     DEFAULT NOW()
);
"""

DDL_HYPERV_VMS = """
CREATE TABLE IF NOT EXISTS hyperv_vms (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id             UUID            NOT NULL REFERENCES hyperv_hosts(id),
    name                VARCHAR(255)    NOT NULL,
    state               VARCHAR(20)     NOT NULL,
    vcpus               INTEGER,
    memory_mb           INTEGER,
    disk_bytes          BIGINT,
    cpu_percent         DOUBLE PRECISION,
    memory_percent      DOUBLE PRECISION,
    uptime_seconds      BIGINT,
    last_updated        TIMESTAMPTZ     DEFAULT NOW()
);
"""

DDL_HYPERV_METRICS = """
CREATE TABLE IF NOT EXISTS hyperv_metrics (
    id                  BIGSERIAL       PRIMARY KEY,
    host_id             UUID            NOT NULL REFERENCES hyperv_hosts(id),
    vm_id               UUID            REFERENCES hyperv_vms(id),
    metric_type         VARCHAR(50)     NOT NULL,
    value               DOUBLE PRECISION NOT NULL,
    timestamp           TIMESTAMPTZ     NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hyperv_metrics_host_ts
    ON hyperv_metrics (host_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_hyperv_metrics_vm_ts
    ON hyperv_metrics (vm_id, timestamp);
"""

DDL_HYPERV_FINOPS_RECOMMENDATIONS = """
CREATE TABLE IF NOT EXISTS hyperv_finops_recommendations (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    vm_id               UUID            REFERENCES hyperv_vms(id),
    host_id             UUID            REFERENCES hyperv_hosts(id),
    category            VARCHAR(50)     NOT NULL,
    description         TEXT            NOT NULL,
    suggested_action    TEXT            NOT NULL,
    estimated_savings   DOUBLE PRECISION,
    confidence          DOUBLE PRECISION,
    status              VARCHAR(20)     DEFAULT 'active',
    created_at          TIMESTAMPTZ     DEFAULT NOW()
);
"""


def run_migration(conn):
    """Executa todas as migrações DDL Hyper-V."""
    cursor = conn.cursor()

    steps = [
        ("hyperv_hosts table", DDL_HYPERV_HOSTS),
        ("hyperv_vms table", DDL_HYPERV_VMS),
        ("hyperv_metrics table + indexes", DDL_HYPERV_METRICS),
        ("hyperv_finops_recommendations table", DDL_HYPERV_FINOPS_RECOMMENDATIONS),
    ]

    for name, ddl in steps:
        try:
            cursor.execute(ddl)
            conn.commit()
            logger.info(f"migrate_hyperv: ✓ {name}")
        except Exception as e:
            conn.rollback()
            logger.error(f"migrate_hyperv: ✗ {name}: {e}")

    cursor.close()
    logger.info("migrate_hyperv: migração DDL Hyper-V concluída")


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
        print("migrate_hyperv: OK")
    except Exception as e:
        print(f"migrate_hyperv: ERRO — {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    migrate()
