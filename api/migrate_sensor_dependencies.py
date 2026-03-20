"""
Migration: Cria tabela sensor_dependencies para o DependencyEngine
Executar: python3 migrate_sensor_dependencies.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sensor_dependencies (
                id SERIAL PRIMARY KEY,
                parent_sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
                child_sensor_id  INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (parent_sensor_id, child_sensor_id),
                CHECK (parent_sensor_id <> child_sensor_id)
            )
        """))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_sensor_dep_parent ON sensor_dependencies(parent_sensor_id)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_sensor_dep_child ON sensor_dependencies(child_sensor_id)"
        ))
        conn.commit()
        print("✅ Tabela sensor_dependencies criada!")

if __name__ == "__main__":
    run()
