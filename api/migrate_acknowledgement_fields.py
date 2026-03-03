"""
Migração para adicionar campos de reconhecimento (acknowledgement) na tabela incidents
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        print("🔄 Adicionando campos de acknowledgement na tabela incidents...")
        
        # Adicionar coluna acknowledged_at
        try:
            db.execute(text("""
                ALTER TABLE incidents 
                ADD COLUMN acknowledged_at TIMESTAMP WITH TIME ZONE
            """))
            print("✅ Coluna acknowledged_at adicionada")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("⚠️ Coluna acknowledged_at já existe")
            else:
                raise
        
        # Adicionar coluna acknowledged_by
        try:
            db.execute(text("""
                ALTER TABLE incidents 
                ADD COLUMN acknowledged_by INTEGER REFERENCES users(id)
            """))
            print("✅ Coluna acknowledged_by adicionada")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("⚠️ Coluna acknowledged_by já existe")
            else:
                raise
        
        # Adicionar coluna acknowledgement_notes
        try:
            db.execute(text("""
                ALTER TABLE incidents 
                ADD COLUMN acknowledgement_notes TEXT
            """))
            print("✅ Coluna acknowledgement_notes adicionada")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("⚠️ Coluna acknowledgement_notes já existe")
            else:
                raise
        
        # Adicionar coluna resolution_notes (se não existir)
        try:
            db.execute(text("""
                ALTER TABLE incidents 
                ADD COLUMN resolution_notes TEXT
            """))
            print("✅ Coluna resolution_notes adicionada")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("⚠️ Coluna resolution_notes já existe")
            else:
                raise
        
        db.commit()
        print("✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
