"""
Fix: Fecha incidentes abertos de sensores Network IN/OUT (snmp)
Esses sensores são metric_only e não devem gerar incidentes.

Execute dentro do container:
  docker exec coruja-api python fix_network_incidents.py
"""
import sys
import os
sys.path.insert(0, '/app')

from database import SessionLocal
from models import Incident, Sensor
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix():
    db = SessionLocal()
    try:
        # Busca sensores SNMP com nome de network in/out
        network_sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'snmp'
        ).all()

        network_sensor_ids = []
        for s in network_sensors:
            name_lower = (s.name or '').lower()
            if any(kw in name_lower for kw in ('network in', 'network out', 'network_in', 'network_out')):
                network_sensor_ids.append(s.id)
                logger.info(f"Sensor metric_only identificado: id={s.id} name='{s.name}' type={s.sensor_type}")

        # Também inclui sensor_type network_in/network_out direto
        direct = db.query(Sensor).filter(
            Sensor.sensor_type.in_(['network_in', 'network_out'])
        ).all()
        for s in direct:
            if s.id not in network_sensor_ids:
                network_sensor_ids.append(s.id)

        if not network_sensor_ids:
            logger.info("Nenhum sensor de network encontrado.")
            return

        logger.info(f"Total de sensores network metric_only: {len(network_sensor_ids)}")

        # Fecha incidentes abertos desses sensores
        open_incidents = db.query(Incident).filter(
            Incident.sensor_id.in_(network_sensor_ids),
            Incident.status.in_(['open', 'acknowledged'])
        ).all()

        logger.info(f"Incidentes abertos a fechar: {len(open_incidents)}")

        now = datetime.utcnow()
        for inc in open_incidents:
            inc.status = 'resolved'
            inc.resolved_at = now
            inc.resolution_notes = 'Auto-resolvido: sensor é metric_only (Network IN/OUT não gera incidentes)'
            logger.info(f"  Fechando incidente id={inc.id} sensor_id={inc.sensor_id} severity={inc.severity}")

        db.commit()
        logger.info("Concluído.")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    fix()
