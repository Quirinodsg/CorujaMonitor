"""
Fix: Seta alert_mode='metric_only' em todos os sensores network_in/network_out
que NÃO sejam link de internet (internet_link=True no config).
Fecha incidentes abertos desses sensores.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # 1. Setar alert_mode via SQL direto (mais confiável que ORM)
    result = db.execute(text("""
        UPDATE sensors
        SET alert_mode = 'metric_only'
        WHERE sensor_type IN ('network_in', 'network_out')
          AND (config IS NULL OR (config->>'internet_link')::boolean IS NOT TRUE)
    """))
    print(f"Sensores atualizados: {result.rowcount}")

    # 2. Fechar todos os incidentes abertos de network_in/network_out
    result2 = db.execute(text("""
        UPDATE incidents
        SET status = 'resolved', resolved_at = NOW()
        WHERE status = 'open'
          AND sensor_id IN (
              SELECT id FROM sensors
              WHERE sensor_type IN ('network_in', 'network_out')
                AND (config IS NULL OR (config->>'internet_link')::boolean IS NOT TRUE)
          )
    """))
    print(f"Incidentes fechados: {result2.rowcount}")

    db.commit()
    print("Concluído com sucesso.")

except Exception as e:
    db.rollback()
    print(f"ERRO: {e}")
    raise
finally:
    db.close()
