#!/usr/bin/env python3
"""
Script para resetar sistema - apaga todos sensores, servidores, probes e tenants
Mantém apenas usuário admin
"""
from database import SessionLocal
from models import Tenant, Probe, Server, Sensor, Metric, Incident
from sqlalchemy import text
import sys

def reset_sistema():
    """Reseta o sistema apagando tudo exceto admin"""
    print("=" * 60)
    print("  RESET COMPLETO DO SISTEMA")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Desabilitar constraints temporariamente
        print("[1/8] Desabilitando constraints...")
        db.execute(text("SET session_replication_role = 'replica';"))
        db.commit()
        
        # 1. Apagar métricas
        print("[2/8] Apagando métricas...")
        count = db.query(Metric).delete()
        db.commit()
        print(f"    ✓ {count} métricas apagadas")
        
        # 2. Apagar incidentes
        print("[3/8] Apagando incidentes...")
        count = db.query(Incident).delete()
        db.commit()
        print(f"    ✓ {count} incidentes apagados")
        
        # 3. Apagar sensores
        print("[4/8] Apagando sensores...")
        count = db.query(Sensor).delete()
        db.commit()
        print(f"    ✓ {count} sensores apagados")
        
        # 4. Apagar servidores
        print("[5/8] Apagando servidores...")
        count = db.query(Server).delete()
        db.commit()
        print(f"    ✓ {count} servidores apagados")
        
        # 5. Apagar probes
        print("[6/8] Apagando probes...")
        count = db.query(Probe).delete()
        db.commit()
        print(f"    ✓ {count} probes apagadas")
        
        # 6. Apagar tenants (exceto Admin)
        print("[7/8] Apagando empresas (exceto Admin)...")
        count = db.execute(text("DELETE FROM tenants WHERE name != 'Admin'")).rowcount
        db.commit()
        print(f"    ✓ {count} empresas apagadas")
        
        # Reabilitar constraints
        print("[8/8] Reabilitando constraints...")
        db.execute(text("SET session_replication_role = 'origin';"))
        db.commit()
        
        print()
        print("=" * 60)
        print("  ✓ SISTEMA RESETADO COM SUCESSO!")
        print("=" * 60)
        print()
        print("O sistema está limpo. Você pode:")
        print("  1. Criar nova empresa")
        print("  2. Registrar nova probe")
        print("  3. Adicionar servidores")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = reset_sistema()
    sys.exit(0 if success else 1)
