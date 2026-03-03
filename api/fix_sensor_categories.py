"""
Script para corrigir automaticamente as categorias dos sensores baseado no nome
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Sensor

def detect_sensor_type(sensor_name: str, current_type: str) -> str:
    """Detecta o tipo correto do sensor baseado no nome"""
    name_lower = sensor_name.lower()
    
    # Docker
    if any(keyword in name_lower for keyword in ['docker', 'container']):
        return 'docker'
    
    # Network
    if any(keyword in name_lower for keyword in ['network', 'rede', '_in', '_out', 'bandwidth', 'traffic']):
        return 'network'
    
    # Ping
    if 'ping' in name_lower:
        return 'ping'
    
    # CPU
    if 'cpu' in name_lower or 'processor' in name_lower:
        return 'cpu'
    
    # Memory
    if any(keyword in name_lower for keyword in ['memory', 'mem', 'ram', 'memória']):
        return 'memory'
    
    # Disk
    if any(keyword in name_lower for keyword in ['disk', 'disco', 'hdd', 'ssd', 'storage']):
        return 'disk'
    
    # System/Uptime
    if any(keyword in name_lower for keyword in ['uptime', 'system', 'sistema']):
        return 'system'
    
    # Service
    if any(keyword in name_lower for keyword in ['service', 'serviço', 'servico']):
        return 'service'
    
    # Hyper-V
    if 'hyperv' in name_lower or 'hyper-v' in name_lower:
        return 'hyperv'
    
    # HTTP
    if 'http' in name_lower or 'https' in name_lower:
        return 'http'
    
    # Port
    if 'port' in name_lower or 'porta' in name_lower:
        return 'port'
    
    # DNS
    if 'dns' in name_lower:
        return 'dns'
    
    # SSL
    if 'ssl' in name_lower or 'tls' in name_lower or 'certificate' in name_lower:
        return 'ssl'
    
    # SNMP
    if 'snmp' in name_lower:
        return 'snmp'
    
    # Se não detectou nada, mantém o tipo atual
    return current_type

def fix_sensor_categories():
    """Corrige as categorias de todos os sensores"""
    db = SessionLocal()
    try:
        sensors = db.query(Sensor).all()
        fixed_count = 0
        
        print(f"Analisando {len(sensors)} sensores...")
        print("-" * 80)
        
        for sensor in sensors:
            detected_type = detect_sensor_type(sensor.name, sensor.sensor_type)
            
            if detected_type != sensor.sensor_type:
                print(f"Sensor: {sensor.name}")
                print(f"  Tipo Atual: {sensor.sensor_type}")
                print(f"  Tipo Detectado: {detected_type}")
                print(f"  ✓ CORRIGIDO")
                print()
                
                sensor.sensor_type = detected_type
                fixed_count += 1
        
        db.commit()
        print("-" * 80)
        print(f"✅ Correção concluída!")
        print(f"Total de sensores: {len(sensors)}")
        print(f"Sensores corrigidos: {fixed_count}")
        print(f"Sensores já corretos: {len(sensors) - fixed_count}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_sensor_categories()
