"""
Script to update existing sensors with default threshold values
"""
from database import SessionLocal
from models import Sensor

def update_sensor_thresholds():
    db = SessionLocal()
    
    try:
        # Get all sensors without thresholds
        sensors = db.query(Sensor).filter(
            (Sensor.threshold_warning == None) | (Sensor.threshold_critical == None)
        ).all()
        
        updated_count = 0
        
        for sensor in sensors:
            # Set default thresholds based on sensor type
            if sensor.sensor_type == 'ping':
                # PING: sem threshold de latência — só alerta em DOWN (value=0)
                # Estilo PRTG/Zabbix
                sensor.threshold_warning = None
                sensor.threshold_critical = None
            elif sensor.sensor_type == 'system':  # uptime
                sensor.threshold_warning = 80.0
                sensor.threshold_critical = 95.0
            else:
                # Default for CPU, Memory, Disk, Network
                sensor.threshold_warning = 80.0
                sensor.threshold_critical = 95.0
            
            updated_count += 1
        
        db.commit()
        print(f"✓ Updated {updated_count} sensors with default thresholds")
        
    except Exception as e:
        print(f"✗ Error updating sensors: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_sensor_thresholds()
