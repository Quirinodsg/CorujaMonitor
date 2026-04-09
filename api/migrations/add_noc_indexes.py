"""
Migration: Adiciona índices para otimizar queries do NOC
Resolve: CPU 100% ao entrar/sair do modo NOC

Execute: python api/migrations/add_noc_indexes.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


INDEXES = [
    # Incident — colunas mais filtradas nas queries do NOC
    ("idx_incident_status",          "incidents",  "CREATE INDEX IF NOT EXISTS idx_incident_status ON incidents(status)"),
    ("idx_incident_severity",        "incidents",  "CREATE INDEX IF NOT EXISTS idx_incident_severity ON incidents(severity)"),
    ("idx_incident_created_at",      "incidents",  "CREATE INDEX IF NOT EXISTS idx_incident_created_at ON incidents(created_at)"),
    ("idx_incident_resolved_at",     "incidents",  "CREATE INDEX IF NOT EXISTS idx_incident_resolved_at ON incidents(resolved_at)"),
    # Índice composto para a query mais comum: status + severity
    ("idx_incident_status_severity", "incidents",  "CREATE INDEX IF NOT EXISTS idx_incident_status_severity ON incidents(status, severity)"),
    # sensor_id já tem FK index, mas composto com status acelera o join
    ("idx_incident_sensor_status",   "incidents",  "CREATE INDEX IF NOT EXISTS idx_incident_sensor_status ON incidents(sensor_id, status, severity)"),

    # Sensor — server_id é muito usado nos joins
    ("idx_sensor_server_active",     "sensors",    "CREATE INDEX IF NOT EXISTS idx_sensor_server_active ON sensors(server_id, is_active)"),

    # Server — tenant_id + is_active
    ("idx_server_tenant_active",     "servers",    "CREATE INDEX IF NOT EXISTS idx_server_tenant_active ON servers(tenant_id, is_active)"),

    # Metric — status + timestamp para queries de disponibilidade
    ("idx_metrics_status_ts",        "metrics",    "CREATE INDEX IF NOT EXISTS idx_metrics_status_ts ON metrics(sensor_id, status, timestamp)"),
]


def run(db_url: str = None):
    from sqlalchemy import create_engine

    if db_url is None:
        # Tenta importar do config da aplicação
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from config import DATABASE_URL
            db_url = DATABASE_URL
        except ImportError:
            db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        logger.error("DATABASE_URL não definida. Passe como argumento ou defina a variável de ambiente.")
        sys.exit(1)

    engine = create_engine(db_url)
    with engine.connect() as conn:
        for name, table, sql in INDEXES:
            try:
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"✅ Índice criado/verificado: {name} em {table}")
            except Exception as e:
                logger.warning(f"⚠️  {name}: {e}")

    logger.info("Migration concluída.")


if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    run(db_url)
