"""
Fix PING sensors: remove latency thresholds and close open latency incidents.

PRTG/Zabbix style: PING só alerta em DOWN (sem resposta / timeout).
Latência alta é apenas métrica, NUNCA cria incidente.

Executar: docker exec coruja-api python fix_ping_incidents_v2.py
"""
from database import SessionLocal
from models import Sensor, Incident, Metric
from datetime import datetime, timezone

def fix_ping():
    db = SessionLocal()
    try:
        # 1. Limpar thresholds de todos os sensores PING
        ping_sensors = db.query(Sensor).filter(Sensor.sensor_type == 'ping').all()
        cleared = 0
        for s in ping_sensors:
            if s.threshold_warning is not None or s.threshold_critical is not None:
                s.threshold_warning = None
                s.threshold_critical = None
                cleared += 1
        db.commit()
        print(f"✅ {cleared} sensores PING com thresholds limpos (de {len(ping_sensors)} total)")

        # 2. Fechar incidentes PING abertos onde o servidor está respondendo (latência > 0)
        open_ping_incidents = db.query(Incident).join(Sensor).filter(
            Sensor.sensor_type == 'ping',
            Incident.status.in_(['open', 'acknowledged'])
        ).all()

        resolved = 0
        for inc in open_ping_incidents:
            # Verificar última métrica — se value > 0, servidor está UP
            latest = db.query(Metric).filter(
                Metric.sensor_id == inc.sensor_id
            ).order_by(Metric.timestamp.desc()).first()

            if latest and latest.value > 0:
                inc.status = 'resolved'
                inc.resolved_at = datetime.now(timezone.utc)
                inc.resolution_notes = (
                    "Auto-resolvido: incidente de latência fechado. "
                    "PING agora só alerta em DOWN (sem resposta)."
                )
                resolved += 1

        db.commit()
        print(f"✅ {resolved} incidentes PING de latência fechados (de {len(open_ping_incidents)} abertos)")

    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_ping()
