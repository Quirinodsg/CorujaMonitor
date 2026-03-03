"""
Remove automaticamente sensores com sensor_type='unknown'
"""

from sqlalchemy import func
from models import Sensor, Metric
from database import SessionLocal

def remove_unknown_sensors():
    """Remove todos os sensores com tipo 'unknown'"""
    db = SessionLocal()
    try:
        # Buscar sensores unknown
        unknown_sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'unknown'
        ).all()
        
        print(f"\n{'='*80}")
        print(f"SENSORES COM TIPO 'UNKNOWN': {len(unknown_sensors)}")
        print(f"{'='*80}\n")
        
        if not unknown_sensors:
            print("✅ Nenhum sensor 'unknown' encontrado!\n")
            return
        
        total_metrics = 0
        
        for sensor in unknown_sensors:
            metrics_count = db.query(Metric).filter(Metric.sensor_id == sensor.id).count()
            total_metrics += metrics_count
            print(f"ID: {sensor.id} | Nome: {sensor.name} | Servidor: {sensor.server_id} | Métricas: {metrics_count}")
        
        print(f"\n{'='*80}")
        print(f"REMOVENDO AUTOMATICAMENTE...")
        print(f"{'='*80}\n")
        
        # Remover métricas primeiro
        for sensor in unknown_sensors:
            db.query(Metric).filter(Metric.sensor_id == sensor.id).delete()
        
        # Remover sensores
        db.query(Sensor).filter(Sensor.sensor_type == 'unknown').delete()
        
        db.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ REMOÇÃO CONCLUÍDA!")
        print(f"{'='*80}")
        print(f"Sensores removidos: {len(unknown_sensors)}")
        print(f"Métricas removidas: {total_metrics}")
        print(f"{'='*80}\n")
        
        # Verificar contagem final
        final_count = db.query(Sensor).count()
        print(f"Total de sensores restantes: {final_count}\n")
        
        # Mostrar contagem por tipo
        type_counts = db.query(
            Sensor.sensor_type,
            func.count(Sensor.id)
        ).group_by(Sensor.sensor_type).all()
        
        print("Contagem por tipo:")
        for sensor_type, count in type_counts:
            print(f"  {sensor_type}: {count}")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERRO: {e}\n")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    remove_unknown_sensors()
