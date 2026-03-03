"""
Migração: Adicionar suporte para sensores independentes (standalone)
- Tornar server_id opcional (nullable=True)
- Adicionar probe_id para sensores independentes
"""

from sqlalchemy import create_engine, text
from config import settings
import os

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("🔧 Iniciando migração para sensores independentes...")
        
        try:
            # 1. Adicionar coluna probe_id (nullable)
            print("1. Adicionando coluna probe_id...")
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN IF NOT EXISTS probe_id INTEGER REFERENCES probes(id)
            """))
            conn.commit()
            print("   ✓ Coluna probe_id adicionada")
            
            # 2. Tornar server_id nullable
            print("2. Tornando server_id opcional...")
            conn.execute(text("""
                ALTER TABLE sensors 
                ALTER COLUMN server_id DROP NOT NULL
            """))
            conn.commit()
            print("   ✓ server_id agora é opcional")
            
            # 3. Criar índice para probe_id
            print("3. Criando índice para probe_id...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sensors_probe_id 
                ON sensors(probe_id)
            """))
            conn.commit()
            print("   ✓ Índice criado")
            
            print("\n✅ Migração concluída com sucesso!")
            print("\nAgora você pode:")
            print("- Criar sensores independentes (sem server_id)")
            print("- Vincular sensores diretamente a probes")
            print("- Monitorar Access Points, Azure Services, etc.")
            
        except Exception as e:
            print(f"\n❌ Erro na migração: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
