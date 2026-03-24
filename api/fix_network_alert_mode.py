"""
Fix: Seta alert_mode='metric_only' em todos os sensores network_in/network_out
que NÃO sejam link de internet (internet_link=True no config).
Fecha incidentes abertos desses sensores.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Sensor, Incident
from sqlalchemy import text

db = SessionLocal()

try:
    # 1. Buscar sensores network_in/network_out sem internet_link
    sensors = db.query(Sensor).filter(
        Sensor.sensor_type.in_(['network_in', 'network_out'])
    ).all()

    fixed = 0
    skipped = 0
    for s in sensors:
        config = s.config or {}
        if config.get('internet_link'):
            skipped += 1
            continue
        if s.alert_mode != 'metric_only':
            s.alert_mode = 'metric_only'
            fixed += 1

    print(f"Sensores corrigidos (metric_only): {fixed}")
    print(f"Sensores ignorados (internet_link=True): {skipped}")

    # 2. Fechar incidentes abertos de sensores network_in/network_out (sem internet_link)
    network_sensor_ids = [
        s.id for s in sensors
        if not (s.config or {}).get('internet_link')
    ]

    if network_sensor_ids:
        closed = db.query(Incident).filter(
            Incident.sensor_id.in_(network_sensor_ids),
            Incident.status == 'open'
        ).update({'status': 'resolved'}, synchronize_session=False)
        print(f"Incidentes fechados: {closed}")
    else:
        print("Nenhum incidente para fechar")

    db.commit()
    print("Concluído com sucesso.")

except Exception as e:
    db.rollback()
    print(f"ERRO: {e}")
    raise
finally:
    db.close()
