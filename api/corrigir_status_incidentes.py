#!/usr/bin/env python3
"""
Script para corrigir status de incidentes resolvidos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://coruja:coruja_secure_password@postgres:5432/coruja_monitor"

def main():
    print("=" * 60)
    print("  CORRIGIR STATUS DE INCIDENTES")
    print("=" * 60)
    print()
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar incidentes com resolved_at preenchido mas status != 'resolved'
        print("[1/2] Buscando incidentes inconsistentes...")
        result = session.execute(text("""
            SELECT id, title, status, resolved_at
            FROM incidents
            WHERE resolved_at IS NOT NULL
            AND status != 'resolved'
            ORDER BY resolved_at DESC
        """))
        incidents = result.fetchall()
        
        if not incidents:
            print("   ✅ Nenhum incidente inconsistente encontrado")
            return 0
        
        print(f"   Encontrados: {len(incidents)} incidentes")
        for inc in incidents:
            print(f"   - ID {inc.id}: {inc.title[:50]}... (status: {inc.status})")
        print()
        
        # Corrigir status
        print("[2/2] Corrigindo status...")
        session.execute(text("""
            UPDATE incidents
            SET status = 'resolved'
            WHERE resolved_at IS NOT NULL
            AND status != 'resolved'
        """))
        session.commit()
        print(f"   ✅ {len(incidents)} incidentes corrigidos")
        print()
        
        print("=" * 60)
        print("  ✅ CORREÇÃO CONCLUÍDA!")
        print("=" * 60)
        print()
        print("Recarregue o dashboard (F5) para ver as mudanças")
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
