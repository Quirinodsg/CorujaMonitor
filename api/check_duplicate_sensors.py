"""
Script para verificar e remover sensores duplicados
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from models import Sensor
from collections import defaultdict

def check_duplicates():
    """Verifica sensores duplicados"""
    session = SessionLocal()
    
    try:
        print("🔍 Verificando sensores duplicados...\n")
        
        # Buscar todos os sensores
        sensors = session.query(Sensor).all()
        print(f"📊 Total de sensores no banco: {len(sensors)}\n")
        
        # Agrupar por servidor e tipo
        by_server = defaultdict(list)
        for sensor in sensors:
            key = f"{sensor.server_id}_{sensor.sensor_type}_{sensor.name}"
            by_server[key].append(sensor)
        
        # Encontrar duplicados
        duplicates = {k: v for k, v in by_server.items() if len(v) > 1}
        
        if duplicates:
            print(f"⚠️  Encontrados {len(duplicates)} grupos de sensores duplicados:\n")
            for key, sensor_list in duplicates.items():
                print(f"  🔸 {key}:")
                for sensor in sensor_list:
                    print(f"     - ID: {sensor.id}, Criado: {sensor.created_at}")
            
            print(f"\n💡 Total de sensores duplicados: {sum(len(v) - 1 for v in duplicates.values())}")
            
            # Perguntar se deseja remover
            response = input("\n❓ Deseja remover os sensores duplicados (mantendo o mais antigo)? (s/n): ")
            if response.lower() == 's':
                remove_duplicates(session, duplicates)
        else:
            print("✅ Nenhum sensor duplicado encontrado!")
        
        # Mostrar contagem por servidor
        print("\n📋 Sensores por servidor:")
        server_counts = defaultdict(int)
        for sensor in sensors:
            server_counts[sensor.server_id] += 1
        
        for server_id, count in server_counts.items():
            print(f"  🖥️  Servidor ID {server_id}: {count} sensores")
    
    finally:
        session.close()

def remove_duplicates(session, duplicates):
    """Remove sensores duplicados, mantendo o mais antigo"""
    removed_count = 0
    
    for key, sensor_list in duplicates.items():
        # Ordenar por data de criação (mais antigo primeiro)
        sensor_list.sort(key=lambda x: x.created_at)
        
        # Manter o primeiro (mais antigo), remover os outros
        to_keep = sensor_list[0]
        to_remove = sensor_list[1:]
        
        print(f"\n🔸 {key}:")
        print(f"   ✅ Mantendo: ID {to_keep.id} (criado em {to_keep.created_at})")
        
        for sensor in to_remove:
            print(f"   ❌ Removendo: ID {sensor.id} (criado em {sensor.created_at})")
            session.delete(sensor)
            removed_count += 1
    
    # Commit das mudanças
    try:
        session.commit()
        print(f"\n✅ {removed_count} sensores duplicados removidos com sucesso!")
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erro ao remover sensores: {e}")

if __name__ == "__main__":
    check_duplicates()
