from database import SessionLocal
from models import Sensor, Metric

db = SessionLocal()

# Find sensors to remove
sensors = db.query(Sensor).filter(
    (Sensor.sensor_type == 'unknown') | (Sensor.sensor_type == 'udm')
).all()

print(f"Encontrados {len(sensors)} sensores para remover:")
for s in sensors:
    print(f"  - {s.sensor_type}: {s.name}")

# Remove metrics first
for sensor in sensors:
    metrics_count = db.query(Metric).filter(Metric.sensor_id == sensor.id).count()
    db.query(Metric).filter(Metric.sensor_id == sensor.id).delete()
    print(f"  Removidas {metrics_count} métricas do sensor {sensor.name}")
    db.delete(sensor)

db.commit()
print(f"\n✓ Removidos {len(sensors)} sensores com sucesso!")
