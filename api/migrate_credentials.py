#!/usr/bin/env python3
"""
Migração: Criar tabela de credenciais centralizadas
Sistema moderno como PRTG/SolarWinds/CheckMK
"""
import sys
import os

# Adicionar path da API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine, SessionLocal
from models import Credential

def migrate():
    print("=" * 70)
    print("🔧 MIGRAÇÃO: Credenciais Centralizadas")
    print("=" * 70)
    print()
    
    with engine.connect() as conn:
        # Criar tabela credentials
        print("📊 Criando tabela 'credentials'...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS credentials (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                
                -- Identificação
                name VARCHAR(255) NOT NULL,
                description TEXT,
                
                -- Tipo de Credencial
                credential_type VARCHAR(20) NOT NULL,
                
                -- Nível de Aplicação (herança)
                level VARCHAR(20) NOT NULL DEFAULT 'tenant',
                group_name VARCHAR(255),
                server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
                
                -- Credenciais WMI
                wmi_username VARCHAR(255),
                wmi_password_encrypted TEXT,
                wmi_domain VARCHAR(255),
                
                -- Credenciais SNMP v1/v2c
                snmp_community VARCHAR(255),
                snmp_port INTEGER DEFAULT 161,
                
                -- Credenciais SNMP v3
                snmp_username VARCHAR(255),
                snmp_auth_protocol VARCHAR(20),
                snmp_auth_password_encrypted TEXT,
                snmp_priv_protocol VARCHAR(20),
                snmp_priv_password_encrypted TEXT,
                snmp_context VARCHAR(255),
                
                -- Credenciais SSH
                ssh_username VARCHAR(255),
                ssh_password_encrypted TEXT,
                ssh_private_key_encrypted TEXT,
                ssh_port INTEGER DEFAULT 22,
                
                -- Configurações
                is_default BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                
                -- Teste de Conectividade
                last_test_at TIMESTAMP WITH TIME ZONE,
                last_test_status VARCHAR(20),
                last_test_message TEXT,
                
                -- Auditoria
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        print("✅ Tabela 'credentials' criada")
        
        # Criar índices
        print("📊 Criando índices...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_credentials_tenant ON credentials(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_credentials_type ON credentials(credential_type);
            CREATE INDEX IF NOT EXISTS idx_credentials_level ON credentials(level);
            CREATE INDEX IF NOT EXISTS idx_credentials_group ON credentials(group_name);
            CREATE INDEX IF NOT EXISTS idx_credentials_server ON credentials(server_id);
            CREATE INDEX IF NOT EXISTS idx_credentials_default ON credentials(is_default);
        """))
        print("✅ Índices criados")
        
        # Adicionar colunas na tabela servers
        print("📊 Adicionando colunas na tabela 'servers'...")
        try:
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN IF NOT EXISTS credential_id INTEGER REFERENCES credentials(id) ON DELETE SET NULL
            """))
            conn.execute(text("""
                ALTER TABLE servers 
                ADD COLUMN IF NOT EXISTS use_inherited_credential BOOLEAN DEFAULT TRUE
            """))
            print("✅ Colunas adicionadas na tabela 'servers'")
        except Exception as e:
            print(f"⚠️ Colunas já existem ou erro: {e}")
        
        conn.commit()
    
    print()
    print("=" * 70)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print()
    print("Próximos passos:")
    print("  1. Criar API: api/routers/credentials.py")
    print("  2. Criar componente React: frontend/src/components/Credentials.js")
    print("  3. Atualizar probe para usar credenciais com herança")
    print()

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
