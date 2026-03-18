"""
Migration: adiciona coluna sort_order na tabela servers
Execute: python migrate_sort_order.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Verifica se coluna já existe
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='servers' AND column_name='sort_order'
        """))
        if result.fetchone():
            print("✔ Coluna sort_order já existe")
            return

        conn.execute(text("ALTER TABLE servers ADD COLUMN sort_order INTEGER DEFAULT 0"))
        conn.commit()
        print("✔ Coluna sort_order adicionada com sucesso")

if __name__ == "__main__":
    migrate()
