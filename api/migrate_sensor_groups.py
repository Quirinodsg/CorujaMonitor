"""
Migração: Sistema de Grupos Hierárquicos para Sensores
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        print("🔧 Iniciando migração de grupos de sensores...")
        
        # 1. Criar tabela sensor_groups
        print("1. Criando tabela sensor_groups...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sensor_groups (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                parent_id INTEGER REFERENCES sensor_groups(id) ON DELETE CASCADE,
                description TEXT,
                icon VARCHAR(50) DEFAULT '📁',
                color VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))
        print("   ✓ Tabela sensor_groups criada")
        
        # 2. Criar índices
        print("2. Criando índices...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sensor_groups_tenant 
            ON sensor_groups(tenant_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sensor_groups_parent 
            ON sensor_groups(parent_id)
        """))
        print("   ✓ Índices criados")
        
        # 3. Adicionar coluna group_id em sensors
        print("3. Adicionando coluna group_id em sensors...")
        try:
            conn.execute(text("""
                ALTER TABLE sensors 
                ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES sensor_groups(id)
            """))
            print("   ✓ Coluna group_id adicionada")
        except Exception as e:
            print(f"   ⚠ Coluna group_id já existe ou erro: {e}")
        
        # 4. Criar índice para group_id
        print("4. Criando índice para group_id...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sensors_group 
            ON sensors(group_id)
        """))
        print("   ✓ Índice criado")
        
        # 5. Criar grupos padrão para cada tenant
        print("5. Criando grupos padrão...")
        conn.execute(text("""
            INSERT INTO sensor_groups (tenant_id, name, description, icon, color)
            SELECT 
                id,
                'Sensores Não Agrupados',
                'Sensores sem grupo definido',
                '📦',
                '#999999'
            FROM tenants
            WHERE NOT EXISTS (
                SELECT 1 FROM sensor_groups 
                WHERE sensor_groups.tenant_id = tenants.id
            )
        """))
        print("   ✓ Grupos padrão criados")
        
        conn.commit()
        
        print("\n✅ Migração concluída com sucesso!")
        print("\nAgora você pode:")
        print("- Criar grupos hierárquicos")
        print("- Organizar sensores em grupos")
        print("- Mover grupos e sensores")

if __name__ == "__main__":
    migrate()
