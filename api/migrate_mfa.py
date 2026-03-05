"""
Migração: Adicionar campos MFA ao modelo User
"""

from sqlalchemy import text
from database import engine

def migrate():
    """Adiciona campos MFA à tabela users"""
    
    with engine.connect() as conn:
        # Verificar se colunas já existem
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('mfa_enabled', 'mfa_secret', 'mfa_backup_codes')
        """))
        
        existing_columns = [row[0] for row in result]
        
        # Adicionar mfa_enabled
        if 'mfa_enabled' not in existing_columns:
            print("Adicionando coluna mfa_enabled...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN mfa_enabled BOOLEAN DEFAULT FALSE
            """))
            conn.commit()
            print("✓ Coluna mfa_enabled adicionada")
        else:
            print("✓ Coluna mfa_enabled já existe")
        
        # Adicionar mfa_secret
        if 'mfa_secret' not in existing_columns:
            print("Adicionando coluna mfa_secret...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN mfa_secret VARCHAR(255)
            """))
            conn.commit()
            print("✓ Coluna mfa_secret adicionada")
        else:
            print("✓ Coluna mfa_secret já existe")
        
        # Adicionar mfa_backup_codes
        if 'mfa_backup_codes' not in existing_columns:
            print("Adicionando coluna mfa_backup_codes...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN mfa_backup_codes JSON
            """))
            conn.commit()
            print("✓ Coluna mfa_backup_codes adicionada")
        else:
            print("✓ Coluna mfa_backup_codes já existe")
        
        print("\n✅ Migração MFA concluída com sucesso!")

if __name__ == "__main__":
    migrate()
