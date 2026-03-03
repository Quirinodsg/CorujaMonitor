"""
Script para listar todos os sensores
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Sensor, Server
from collections import defaultdict

def list_sensors():
    """Lista todos os sensores"""
    session = SessionLocal()
    
    try:
        print("📊 Listando todos os sensores...\n")
        
        # Buscar todos os sensores
        sensors = session.query(Sensor).order_by(Sensor.server_id, Sensor.sensor_type, Sensor.name).all()
        servers = {s.id: s for s in session.query(Server).all()}
        
        print(f"Total: {len(sensors)} sensores\n")
        
        # Agrupar por servidor
        by_server = defaultdict(list)
        for sensor in sensors:
            by_server[sensor.server_id].append(sensor)
        
        # Listar por servidor
        for server_id, sensor_list in by_server.items():
            server = servers.get(server_id)
            server_name = server.hostname if server else f"Servidor ID {server_id}"
            
            print(f"\n🖥️  {server_name} ({len(sensor_list)} sensores):")
            print("=" * 80)
            
            # Agrupar por tipo
            by_type = defaultdict(list)
            for sensor in sensor_list:
                by_type[sensor.sensor_type].append(sensor)
            
            for sensor_type, type_sensors in sorted(by_type.items()):
                print(f"\n  📁 {sensor_type.upper()} ({len(type_sensors)} sensores):")
                for sensor in type_sensors:
                    print(f"     • {sensor.name} (ID: {sensor.id})")
        
        # Resumo por tipo
        print("\n\n📈 Resumo por tipo de sensor:")
        print("=" * 80)
        type_counts = defaultdict(int)
        for sensor in sensors:
            type_counts[sensor.sensor_type] += 1
        
        for sensor_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {sensor_type:15} : {count:3} sensores")
    
    finally:
        session.close()

if __name__ == "__main__":
    list_sensors()
