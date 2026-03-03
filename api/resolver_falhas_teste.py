#!/usr/bin/env python3
"""
Script para resolver automaticamente falhas de teste antigas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = "postgresql://coruja:coruja_secure_password@postgres:5432/coruja_monitor"

def main():
    print("=" * 60)
    print("  RESOLVER FALHAS DE TESTE ANTIGAS")
    print("=" * 60)
    print()
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar incidentes de teste não resolvidos com mais de 5 minutos
        print("[1/3] Buscando incidentes de teste antigos...")
        result = session.execute(text("""
            SELECT id, sensor_id, description, created_at
            FROM incidents
            WHERE resolved_at IS NULL
            AND description LIKE '%TESTE%'
            AND created_at < NOW() - INTERVAL '5 minutes'
            ORDER BY created_at DESC
        """))
        incidents = result.fetchall()
        
        if not incidents:
            print("   ✅ Nenhum incidente de teste antigo encontrado")
            return 0
        
        print(f"   Encontrados: {len(incidents)} incidentes")
        for inc in incidents:
            age = datetime.now() - inc.created_at.replace(tzinfo=None)
            print(f"   - ID {inc.id}: {inc.description[:50]}... (há {age.seconds//60} minutos)")
        print()
        
        # Resolver incidentes
        print("[2/3] Resolvendo incidentes...")
        session.execute(text("""
            UPDATE incidents
            SET resolved_at = NOW()
            WHERE resolved_at IS NULL
            AND description LIKE '%TESTE%'
            AND created_at < NOW() - INTERVAL '5 minutes'
        """))
        session.commit()
        print(f"   ✅ {len(incidents)} incidentes resolvidos")
        print()
        
        # Verificar resultado
        print("[3/3] Verificando...")
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM incidents
            WHERE resolved_at IS NULL
            AND description LIKE '%TESTE%'
        """))
        remaining = result.fetchone().count
        
        print(f"   Incidentes de teste abertos: {remaining}")
        print()
        
        print("=" * 60)
        print("  ✅ CONCLUÍDO!")
        print("=" * 60)
        print()
        print("Recarregue o dashboard para ver as mudanças")
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
