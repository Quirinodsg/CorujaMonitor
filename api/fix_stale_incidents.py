"""
Fecha incidentes abertos cujo sensor já voltou ao normal.
Executar: docker exec coruja-api python fix_stale_incidents.py
"""
from database import SessionLocal
from models import Sensor, Incident, Metric
from datetime import datetime, timezone

def fix():
    db = SessionLocal()
    try:
        open_incidents = db.query(Incident).filter(
            Incident.status.in_(['open', 'acknowledged'])
        ).all()

        resolved = 0
        for inc in open_incidents:
            latest = db.query(Metric).filter(
                Metric.sensor_id == inc.sensor_id
            ).order_by(Metric.timestamp.desc()).first()

            if latest and latest.status == 'ok':
                inc.status = 'resolved'
                inc.resolved_at = datetime.now(timezone.utc)
                inc.resolution_notes = 'Auto-resolvido: sensor voltou ao normal (fix_stale_incidents)'
                resolved += 1

        db.commit()
        print(f"✅ {resolved} incidentes fechados (de {len(open_incidents)} abertos)")
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix()
