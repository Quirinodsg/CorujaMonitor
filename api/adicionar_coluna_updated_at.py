"""
Script para adicionar coluna updated_at na tabela servers
"""
import psycopg2
from datetime import datetime

# Configurações do banco (usar hostname do Docker)
DB_HOST = "postgres"  # Nome do container no docker-compose
DB_PORT = 5432
DB_NAME = "coruja_monitor"
DB_USER = "coruja_user"
DB_PASSWORD = "coruja_secure_password"

def adicionar_coluna_updated_at():
    """Adiciona coluna updated_at na tabela servers se não existir"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print("🔍 Verificando se coluna updated_at existe...")
        
        # Verificar se coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='servers' AND column_name='updated_at'
        """)
        
        if cursor.fetchone():
            print("✅ Coluna updated_at já existe!")
        else:
            print("➕ Adicionando coluna updated_at...")
            
            # Adicionar coluna com valor padrão
            cursor.execute("""
                ALTER TABLE servers 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            
            # Atualizar registros existentes
            cursor.execute("""
                UPDATE servers 
                SET updated_at = created_at 
                WHERE updated_at IS NULL
            """)
            
            conn.commit()
            print("✅ Coluna updated_at adicionada com sucesso!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

if __name__ == "__main__":
    adicionar_coluna_updated_at()
