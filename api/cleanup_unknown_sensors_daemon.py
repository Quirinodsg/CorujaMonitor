"""
Daemon que remove automaticamente sensores 'unknown' a cada minuto
"""

import time
import logging
from sqlalchemy import func
from models import Sensor, Metric
from database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_unknown_sensors():
    """Remove todos os sensores com tipo 'unknown'"""
    db = SessionLocal()
    try:
        # Buscar sensores unknown
        unknown_sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'unknown'
        ).all()
        
        if not unknown_sensors:
            logger.info("✅ Nenhum sensor 'unknown' encontrado")
            return 0
        
        total_metrics = 0
        sensor_ids = []
        
        for sensor in unknown_sensors:
            sensor_ids.append(sensor.id)
            metrics_count = db.query(Metric).filter(Metric.sensor_id == sensor.id).count()
            total_metrics += metrics_count
        
        logger.info(f"🧹 Limpando {len(unknown_sensors)} sensores 'unknown' e {total_metrics} métricas")
        
        # Remover métricas primeiro
        for sensor_id in sensor_ids:
            db.query(Metric).filter(Metric.sensor_id == sensor_id).delete()
        
        # Remover sensores
        db.query(Sensor).filter(Sensor.sensor_type == 'unknown').delete()
        
        db.commit()
        
        logger.info(f"✅ Removidos {len(unknown_sensors)} sensores e {total_metrics} métricas")
        
        # Mostrar contagem final
        final_count = db.query(Sensor).count()
        logger.info(f"📊 Total de sensores restantes: {final_count}")
        
        return len(unknown_sensors)
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao limpar sensores: {e}")
        return 0
    finally:
        db.close()

def run_daemon():
    """Executa o daemon de limpeza"""
    logger.info("🚀 Daemon de limpeza de sensores 'unknown' iniciado")
    logger.info("⏰ Executando limpeza a cada 60 segundos")
    
    while True:
        try:
            cleanup_unknown_sensors()
            time.sleep(60)  # Aguarda 60 segundos
        except KeyboardInterrupt:
            logger.info("\n🛑 Daemon interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"❌ Erro no daemon: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_daemon()
