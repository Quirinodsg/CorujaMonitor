"""
Script para verificar e corrigir sensores duplicados
"""

import sys
from sqlalchemy import func
from models import Sensor, Metric
from database import SessionLocal

def check_duplicates():
    """Verifica sensores duplicados"""
    db = SessionLocal()
    try:
        # Buscar todos os sensores
        sensors = db.query(Sensor).order_by(Sensor.id).all()
        
        print(f"\n{'='*80}")
        print(f"TOTAL DE SENSORES NO BANCO: {len(sensors)}")
        print(f"{'='*80}\n")
        
        # Agrupar por servidor e tipo
        by_server = {}
        for sensor in sensors:
            key = f"{sensor.server_id}_{sensor.sensor_type}_{sensor.name}"
            if key not in by_server:
                by_server[key] = []
            by_server[key].append(sensor)
        
        # Encontrar duplicados
        duplicates = []
        for key, sensor_list in by_server.items():
            if len(sensor_list) > 1:
                duplicates.append((key, sensor_list))
        
        if duplicates:
            print(f"⚠️  ENCONTRADOS {len(duplicates)} GRUPOS DE SENSORES DUPLICADOS:\n")
            for key, sensor_list in duplicates:
                print(f"Grupo: {key}")
                for sensor in sensor_list:
                    metrics_count = db.query(Metric).filter(Metric.sensor_id == sensor.id).count()
                    print(f"  - ID: {sensor.id} | Nome: {sensor.name} | Tipo: {sensor.sensor_type} | Métricas: {metrics_count}")
                print()
        else:
            print("✅ Nenhum sensor duplicado encontrado!\n")
        
        # Mostrar contagem por tipo
        print(f"\n{'='*80}")
        print("CONTAGEM POR TIPO DE SENSOR:")
        print(f"{'='*80}\n")
        
        type_counts = db.query(
            Sensor.sensor_type,
            func.count(Sensor.id)
        ).group_by(Sensor.sensor_type).all()
        
        for sensor_type, count in type_counts:
            print(f"  {sensor_type}: {count}")
        
        print(f"\n{'='*80}\n")
        
        return duplicates
        
    finally:
        db.close()

def remove_duplicates(dry_run=True):
    """Remove sensores duplicados mantendo o mais antigo"""
    db = SessionLocal()
    try:
        duplicates = check_duplicates()
        
        if not duplicates:
            print("Nenhum duplicado para remover.")
            return
        
        if dry_run:
            print("\n⚠️  MODO DRY-RUN - Nenhuma alteração será feita")
            print("Execute com --fix para aplicar as correções\n")
        
        total_removed = 0
        total_metrics_removed = 0
        
        for key, sensor_list in duplicates:
            # Ordenar por ID (manter o mais antigo)
            sensor_list.sort(key=lambda s: s.id)
            keep = sensor_list[0]
            remove = sensor_list[1:]
            
            print(f"\nGrupo: {key}")
            print(f"  ✅ MANTER: ID {keep.id} (mais antigo)")
            
            for sensor in remove:
                metrics_count = db.query(Metric).filter(Metric.sensor_id == sensor.id).count()
                print(f"  ❌ REMOVER: ID {sensor.id} ({metrics_count} métricas)")
                
                if not dry_run:
                    # Remover métricas
                    db.query(Metric).filter(Metric.sensor_id == sensor.id).delete()
                    # Remover sensor
                    db.delete(sensor)
                    total_removed += 1
                    total_metrics_removed += metrics_count
        
        if not dry_run:
            db.commit()
            print(f"\n{'='*80}")
            print(f"✅ CORREÇÃO CONCLUÍDA!")
            print(f"{'='*80}")
            print(f"Sensores removidos: {total_removed}")
            print(f"Métricas removidas: {total_metrics_removed}")
            print(f"{'='*80}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERRO: {e}\n")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        print("\n🔧 MODO CORREÇÃO - Removendo duplicados...\n")
        remove_duplicates(dry_run=False)
    else:
        print("\n🔍 MODO VERIFICAÇÃO - Apenas listando duplicados...\n")
        remove_duplicates(dry_run=True)
