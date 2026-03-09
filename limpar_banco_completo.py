#!/usr/bin/env python3
"""
Script para limpar banco de dados e recriar estrutura
Remove todas as empresas, probes e servidores
"""
import sys
import os

# Adicionar diretório api ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from database import SessionLocal, engine
from models import Base, Tenant, Probe, Server, User, Sensor, Metric
from sqlalchemy import text

def limpar_tudo():
    print("=" * 60)
    print("  LIMPAR BANCO DE DADOS COMPLETO")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        print("[1/6] Desabilitando constraints...")
        db.execute(text("SET session_replication_role = 'replica';"))
        db.commit()
        print("[OK] Constraints desabilitadas")
        
        print("\n[2/6] Removendo métricas...")
        db.query(Metric).delete()
        db.commit()
        print(f"[OK] Métricas removidas")
        
        print("\n[3/6] Removendo sensores...")
        db.query(Sensor).delete()
        db.commit()
        print(f"[OK] Sensores removidos")
        
        print("\n[4/6] Removendo servidores...")
        db.query(Server).delete()
        db.commit()
        print(f"[OK] Servidores removidos")
        
        print("\n[5/6] Removendo probes...")
        db.query(Probe).delete()
        db.commit()
        print(f"[OK] Probes removidas")
        
        print("\n[6/6] Removendo tenants (empresas)...")
        # Não remover o tenant do admin
        db.execute(text("DELETE FROM tenants WHERE name != 'Admin'"))
        db.commit()
        print(f"[OK] Tenants removidos (exceto Admin)")
        
        print("\n[7/7] Reabilitando constraints...")
        db.execute(text("SET session_replication_role = 'origin';"))
        db.commit()
        print("[OK] Constraints reabilitadas")
        
        print()
        print("=" * 60)
        print("  BANCO LIMPO COM SUCESSO!")
        print("=" * 60)
        print()
        print("Agora você pode:")
        print("1. Criar nova empresa (Techbiz)")
        print("2. Adicionar probe")
        print("3. Adicionar servidores")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(limpar_tudo())
