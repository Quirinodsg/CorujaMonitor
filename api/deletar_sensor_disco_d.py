#!/usr/bin/env python3
"""
Script para deletar sensor DISCO D diretamente no banco
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://coruja:coruja123@localhost:5432/coruja')

print("=" * 70)
print("  DELETAR SENSOR DISCO D")
print("=" * 70)
print()

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Find DISCO D sensor
    result = session.execute(text("""
        SELECT s.id, s.name, s.sensor_type, srv.hostname
        FROM sensors s
        JOIN servers srv ON s.server_id = srv.id
        WHERE s.name LIKE '%DISCO D%' OR s.name LIKE '%Disco D%'
    """))
    
    sensors = result.fetchall()
    
    if not sensors:
        print("❌ Nenhum sensor 'DISCO D' encontrado")
        sys.exit(0)
    
    print(f"✅ Encontrados {len(sensors)} sensor(es) DISCO D:")
    print()
    
    for sensor in sensors:
        sensor_id, name, sensor_type, hostname = sensor
        print(f"  ID: {sensor_id}")
        print(f"  Nome: {name}")
        print(f"  Tipo: {sensor_type}")
        print(f"  Servidor: {hostname}")
        print()
    
    # Confirm deletion
    confirm = input("Deseja deletar TODOS estes sensores? (sim/não): ")
    
    if confirm.lower() != 'sim':
        print("❌ Operação cancelada")
        sys.exit(0)
    
    # Delete each sensor
    for sensor in sensors:
        sensor_id = sensor[0]
        name = sensor[1]
        
        print(f"🗑️  Deletando sensor '{name}' (ID: {sensor_id})...")
        
        # Delete metrics
        result = session.execute(text("""
            DELETE FROM metrics WHERE sensor_id = :sensor_id
        """), {"sensor_id": sensor_id})
        metrics_deleted = result.rowcount
        print(f"   ✓ {metrics_deleted} métricas deletadas")
        
        # Delete incidents
        result = session.execute(text("""
            DELETE FROM incidents WHERE sensor_id = :sensor_id
        """), {"sensor_id": sensor_id})
        incidents_deleted = result.rowcount
        print(f"   ✓ {incidents_deleted} incidentes deletados")
        
        # Delete sensor notes
        result = session.execute(text("""
            DELETE FROM sensor_notes WHERE sensor_id = :sensor_id
        """), {"sensor_id": sensor_id})
        notes_deleted = result.rowcount
        print(f"   ✓ {notes_deleted} notas deletadas")
        
        # Delete sensor
        result = session.execute(text("""
            DELETE FROM sensors WHERE id = :sensor_id
        """), {"sensor_id": sensor_id})
        print(f"   ✓ Sensor deletado")
        print()
    
    # Commit changes
    session.commit()
    
    print("=" * 70)
    print("✅ SENSORES DELETADOS COM SUCESSO!")
    print("=" * 70)
    print()
    print("Aguarde 60 segundos e recarregue o dashboard")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    session.close()
