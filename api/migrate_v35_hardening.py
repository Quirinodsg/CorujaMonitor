"""
Migration v3.5 Enterprise Hardening
- Adiciona cooldown_seconds em sensors
- Garante paused_until em sensors
- Cria tabela default_sensor_profiles com seed de fábrica
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

SQL = """
-- 1. Garantir coluna paused_until (pode já existir)
ALTER TABLE sensors
    ADD COLUMN IF NOT EXISTS paused_until TIMESTAMP WITH TIME ZONE;

-- 2. Adicionar cooldown_seconds
ALTER TABLE sensors
    ADD COLUMN IF NOT EXISTS cooldown_seconds INTEGER DEFAULT 300;

-- 3. Criar tabela default_sensor_profiles
CREATE TABLE IF NOT EXISTS default_sensor_profiles (
    id                  SERIAL PRIMARY KEY,
    asset_type          VARCHAR(50)  NOT NULL,
    sensor_type         VARCHAR(50)  NOT NULL,
    enabled             BOOLEAN      NOT NULL DEFAULT TRUE,
    alert_mode          VARCHAR(20)  NOT NULL DEFAULT 'normal',
    threshold_warning   FLOAT,
    threshold_critical  FLOAT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (asset_type, sensor_type)
);

-- 4. Índice para lookup rápido
CREATE INDEX IF NOT EXISTS idx_default_profiles_asset_type
    ON default_sensor_profiles (asset_type);

-- 5. Seed: perfis padrão de fábrica
INSERT INTO default_sensor_profiles
    (asset_type, sensor_type, enabled, alert_mode, threshold_warning, threshold_critical)
VALUES
    ('VM', 'cpu',         TRUE, 'normal',      80, 95),
    ('VM', 'memory',      TRUE, 'normal',      80, 95),
    ('VM', 'disk',        TRUE, 'normal',      80, 95),
    ('VM', 'network_in',  TRUE, 'metric_only', 80, 95),
    ('VM', 'network_out', TRUE, 'metric_only', 80, 95),
    ('physical_server', 'cpu',         TRUE, 'normal',      80, 95),
    ('physical_server', 'memory',      TRUE, 'normal',      80, 95),
    ('physical_server', 'disk',        TRUE, 'normal',      80, 95),
    ('physical_server', 'network_in',  TRUE, 'metric_only', 80, 95),
    ('physical_server', 'network_out', TRUE, 'metric_only', 80, 95),
    ('network_device', 'ping',         TRUE, 'normal',      100, 200),
    ('network_device', 'network_in',   TRUE, 'metric_only', 80,  95),
    ('network_device', 'network_out',  TRUE, 'metric_only', 80,  95)
ON CONFLICT (asset_type, sensor_type) DO NOTHING;
"""

def run():
    with engine.connect() as conn:
        for stmt in SQL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("✅ Migration v3.5 Enterprise Hardening aplicada com sucesso")

if __name__ == "__main__":
    run()
