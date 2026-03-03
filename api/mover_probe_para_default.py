#!/usr/bin/env python3
"""
Script para mover probe, servidores, sensores e métricas para o tenant Default
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://coruja:coruja_secure_password@localhost:5432/coruja_monitor"

def main():
    print("=" * 60)
    print("  MOVER PROBE PARA TENANT DEFAULT")
    print("=" * 60)
    print()
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Verificar probe atual
        print("[1/5] Verificando probe atual...")
        result = session.execute(text("""
            SELECT p.id, p.name, p.tenant_id, t.name as tenant_name
            FROM probes p
            JOIN tenants t ON t.id = p.tenant_id
            WHERE p.token = 'TvQ8v6wdYAIhbtSdciuwbb8CP74LilEOMFSYL-4qWXk'
        """))
        probe = result.fetchone()
        
        if not probe:
            print("❌ Probe não encontrada!")
            return
        
        print(f"   Probe: {probe.name} (ID: {probe.id})")
        print(f"   Tenant atual: {probe.tenant_name} (ID: {probe.tenant_id})")
        print()
        
        if probe.tenant_id == 1:
            print("✅ Probe já está no tenant Default!")
            return
        
        # 2. Contar recursos
        print("[2/5] Contando recursos...")
        result = session.execute(text("""
            SELECT 
                COUNT(DISTINCT s.id) as servers,
                COUNT(DISTINCT sen.id) as sensors,
                COUNT(m.id) as metrics
            FROM servers s
            LEFT JOIN sensors sen ON sen.server_id = s.id
            LEFT JOIN metrics m ON m.sensor_id = sen.id
            WHERE s.probe_id = :probe_id
        """), {"probe_id": probe.id})
        counts = result.fetchone()
        
        print(f"   Servidores: {counts.servers}")
        print(f"   Sensores: {counts.sensors}")
        print(f"   Métricas: {counts.metrics}")
        print()
        
        # 3. Mover probe
        print("[3/5] Movendo probe para Default...")
        session.execute(text("""
            UPDATE probes
            SET tenant_id = 1
            WHERE id = :probe_id
        """), {"probe_id": probe.id})
        print("   ✅ Probe movida")
        print()
        
        # 4. Mover servidores
        print("[4/5] Movendo servidores para Default...")
        session.execute(text("""
            UPDATE servers
            SET tenant_id = 1
            WHERE probe_id = :probe_id
        """), {"probe_id": probe.id})
        print("   ✅ Servidores movidos")
        print()
        
        # 5. Commit
        print("[5/5] Salvando alterações...")
        session.commit()
        print("   ✅ Alterações salvas")
        print()
        
        # Verificar resultado
        print("=" * 60)
        print("  VERIFICAÇÃO FINAL")
        print("=" * 60)
        result = session.execute(text("""
            SELECT p.id, p.name, p.tenant_id, t.name as tenant_name
            FROM probes p
            JOIN tenants t ON t.id = p.tenant_id
            WHERE p.id = :probe_id
        """), {"probe_id": probe.id})
        new_probe = result.fetchone()
        
        print(f"Probe: {new_probe.name}")
        print(f"Tenant: {new_probe.tenant_name} (ID: {new_probe.tenant_id})")
        print()
        
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM servers
            WHERE probe_id = :probe_id AND tenant_id = 1
        """), {"probe_id": probe.id})
        server_count = result.fetchone().count
        
        print(f"Servidores no Default: {server_count}")
        print()
        
        print("=" * 60)
        print("  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("1. Recarregue o dashboard (F5)")
        print("2. Os sensores devem mostrar dados agora")
        print()
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
