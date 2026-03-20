"""
Migration: prediction_samples table
Cria tabela para persistência do FailurePredictor entre restarts.
Executar: docker-compose exec api python3 migrate_prediction_history.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS prediction_samples (
                id SERIAL PRIMARY KEY,
                sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
                timestamp TIMESTAMPTZ NOT NULL,
                value FLOAT NOT NULL
            );
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_prediction_samples_sensor_ts
            ON prediction_samples (sensor_id, timestamp);
        """))
        # Manter apenas últimas 2016 amostras por sensor (7 dias a 5min)
        # Limpeza automática via trigger não é necessária — o predictor limita em memória
        conn.commit()
        print("✅ Tabela prediction_samples criada com sucesso.")

if __name__ == "__main__":
    run()
