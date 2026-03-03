"""
Migration: Add custom_reports table
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://coruja:coruja123@localhost/coruja")
engine = create_engine(DATABASE_URL)

# Executar SQL diretamente
with engine.connect() as conn:
    # Criar tabela custom_reports
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_reports (
            id SERIAL PRIMARY KEY,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            report_type VARCHAR(50) NOT NULL,
            filters JSON,
            columns JSON,
            sort_by VARCHAR(100),
            sort_order VARCHAR(10) DEFAULT 'desc',
            is_public BOOLEAN DEFAULT FALSE,
            is_favorite BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE,
            last_generated_at TIMESTAMP WITH TIME ZONE
        );
    """)
    
    # Criar índices
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_reports_tenant 
        ON custom_reports(tenant_id);
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_reports_user 
        ON custom_reports(user_id);
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_custom_reports_type 
        ON custom_reports(report_type);
    """)
    
    conn.commit()
    print("✅ Tabela custom_reports criada com sucesso!")

print("✅ Migração concluída!")
