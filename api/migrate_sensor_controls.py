"""
Migration: Adiciona campos de controle de execução ao model Sensor
- enabled (bool, default True)
- paused_until (timestamp, nullable)
- priority (int 1-5, default 3)

Executar: python3 migrate_sensor_controls.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        # enabled
        try:
            conn.execute(text(
                "ALTER TABLE sensors ADD COLUMN IF NOT EXISTS enabled BOOLEAN NOT NULL DEFAULT TRUE"
            ))
            print("✅ Coluna 'enabled' adicionada")
        except Exception as e:
            print(f"⚠️  enabled: {e}")

        # paused_until
        try:
            conn.execute(text(
                "ALTER TABLE sensors ADD COLUMN IF NOT EXISTS paused_until TIMESTAMPTZ NULL"
            ))
            print("✅ Coluna 'paused_until' adicionada")
        except Exception as e:
            print(f"⚠️  paused_until: {e}")

        # priority
        try:
            conn.execute(text(
                "ALTER TABLE sensors ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 3"
            ))
            print("✅ Coluna 'priority' adicionada")
        except Exception as e:
            print(f"⚠️  priority: {e}")

        # Índice para busca por prioridade
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_sensors_priority ON sensors(priority)"
            ))
            print("✅ Índice idx_sensors_priority criado")
        except Exception as e:
            print(f"⚠️  índice priority: {e}")

        conn.commit()
        print("\n✅ Migration concluída!")

if __name__ == "__main__":
    run()
