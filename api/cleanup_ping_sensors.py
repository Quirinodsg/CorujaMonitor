"""
Script to remove duplicate ping sensors and keep only PING
"""
from database import SessionLocal
from models import Sensor, Metric

def cleanup_ping_sensors():
    db = SessionLocal()
    
    try:
        # Find all ping sensors
        ping_sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'ping'
        ).all()
        
        print(f"Found {len(ping_sensors)} ping sensors")
        
        # Group by server_id
        servers_pings = {}
        for sensor in ping_sensors:
            if sensor.server_id not in servers_pings:
                servers_pings[sensor.server_id] = []
            servers_pings[sensor.server_id].append(sensor)
        
        deleted_count = 0
        
        for server_id, sensors in servers_pings.items():
            if len(sensors) > 1:
                print(f"\nServer {server_id} has {len(sensors)} ping sensors:")
                for s in sensors:
                    print(f"  - ID: {s.id}, Name: {s.name}")
                
                # Keep the one named "PING", or the first one if none is named PING
                keep_sensor = None
                for s in sensors:
                    if s.name == "PING":
                        keep_sensor = s
                        break
                
                if not keep_sensor:
                    # Rename the first one to PING and keep it
                    keep_sensor = sensors[0]
                    keep_sensor.name = "PING"
                    print(f"  → Renaming sensor {keep_sensor.id} to 'PING'")
                else:
                    print(f"  → Keeping sensor {keep_sensor.id} (PING)")
                
                # Delete the others
                for s in sensors:
                    if s.id != keep_sensor.id:
                        print(f"  → Deleting sensor {s.id} ({s.name})")
                        # Delete metrics first
                        db.query(Metric).filter(Metric.sensor_id == s.id).delete()
                        db.delete(s)
                        deleted_count += 1
        
        db.commit()
        print(f"\n✓ Cleanup complete! Deleted {deleted_count} duplicate ping sensors")
        
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_ping_sensors()
