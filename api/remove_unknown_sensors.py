"""
Script para remover sensores com tipo 'unknown' que são duplicados
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Sensor, Metric

def remove_unknown_sensors():
    """Remove sensores com tipo 'unknown'"""
    session = SessionLocal()
    
    try:
        print("🔍 Buscando sensores com tipo 'unknown'...\n")
        
        # Buscar sensores unknown
        unknown_sensors = session.query(Sensor).filter(Sensor.sensor_type == 'unknown').all()
        
        if not unknown_sensors:
            print("✅ Nenhum sensor 'unknown' encontrado!")
            return
        
        print(f"⚠️  Encontrados {len(unknown_sensors)} sensores com tipo 'unknown':\n")
        for sensor in unknown_sensors:
            print(f"  • ID {sensor.id}: {sensor.name}")
        
        # Remover métricas primeiro
        print(f"\n🗑️  Removendo métricas associadas...")
        sensor_ids = [s.id for s in unknown_sensors]
        metrics_deleted = session.query(Metric).filter(Metric.sensor_id.in_(sensor_ids)).delete(synchronize_session=False)
        print(f"   ✅ {metrics_deleted} métricas removidas")
        
        # Remover sensores
        print(f"\n🗑️  Removendo {len(unknown_sensors)} sensores...")
        for sensor in unknown_sensors:
            session.delete(sensor)
        
        session.commit()
        print(f"\n✅ {len(unknown_sensors)} sensores removidos com sucesso!")
        print("\n💡 Agora você deve ter 28 sensores no total:")
        print("   - 7 sensores de sistema (ping, cpu, memory, disk, uptime, network in/out)")
        print("   - 21 sensores Docker")
    
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    remove_unknown_sensors()
