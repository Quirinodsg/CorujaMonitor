"""
Migração: Corrigir thresholds de sensores PING existentes.

Padrão PRTG/Zabbix: Ping NÃO alerta por latência alta.
Alerta APENAS em DOWN (sem resposta / timeout).

Antes: threshold_warning=100ms, threshold_critical=200ms (gerava incidentes por latência)
Depois: threshold_warning=NULL, threshold_critical=NULL (só alerta em DOWN)

Executar no servidor Linux:
  cd /opt/coruja && python api/migrate_ping_thresholds.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import Sensor

def migrate():
    db = SessionLocal()
    try:
        ping_sensors = db.query(Sensor).filter(Sensor.sensor_type == 'ping').all()
        updated = 0

        for sensor in ping_sensors:
            changed = False
            if sensor.threshold_warning is not None:
                print(f"  Sensor {sensor.id} ({sensor.name}): threshold_warning {sensor.threshold_warning} → NULL")
                sensor.threshold_warning = None
                changed = True
            if sensor.threshold_critical is not None:
                print(f"  Sensor {sensor.id} ({sensor.name}): threshold_critical {sensor.threshold_critical} → NULL")
                sensor.threshold_critical = None
                changed = True
            if changed:
                updated += 1

        db.commit()
        print(f"\n✅ Migração concluída: {updated} sensores PING atualizados de {len(ping_sensors)} total.")
        print("   Ping agora só alerta em DOWN (sem resposta), nunca por latência alta.")
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
