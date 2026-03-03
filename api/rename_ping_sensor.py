"""
Script to rename ping sensor from ping_8_8_8_8 to PING
"""
from database import SessionLocal
from models import Sensor

def rename_ping_sensor():
    db = SessionLocal()
    
    try:
        # Find all ping sensors with the old name pattern
        sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'ping'
        ).all()
        
        updated_count = 0
        
        for sensor in sensors:
            # Rename to just "PING"
            if 'ping' in sensor.name.lower() or 'link' in sensor.name.lower():
                sensor.name = 'PING'
                updated_count += 1
        
        db.commit()
        print(f"✓ Renamed {updated_count} ping sensors to 'PING'")
        
    except Exception as e:
        print(f"✗ Error renaming sensors: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    rename_ping_sensor()
