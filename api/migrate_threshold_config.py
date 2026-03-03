#!/usr/bin/env python3
"""
Migração: Adicionar tabela de configuração de thresholds temporais
Baseado em melhores práticas ITIL para evitar falsos positivos
"""
import sys
from sqlalchemy import create_engine, text
from config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("🔧 Criando tabela threshold_config...")
        
        # Criar tabela de configuração de thresholds
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS threshold_config (
                id SERIAL PRIMARY KEY,
                tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
                
                -- Configurações Temporais (ITIL Best Practices)
                breach_duration_seconds INTEGER DEFAULT 600,  -- 10 minutos padrão
                flapping_window_seconds INTEGER DEFAULT 300,   -- 5 minutos para detectar flapping
                flapping_threshold INTEGER DEFAULT 3,          -- 3 mudanças = flapping
                
                -- Configurações por Tipo de Sensor
                cpu_breach_duration INTEGER DEFAULT 600,       -- 10 min para CPU
                memory_breach_duration INTEGER DEFAULT 900,    -- 15 min para Memória
                disk_breach_duration INTEGER DEFAULT 1800,     -- 30 min para Disco
                ping_breach_duration INTEGER DEFAULT 180,      -- 3 min para Ping (mais crítico)
                service_breach_duration INTEGER DEFAULT 120,   -- 2 min para Serviços
                network_breach_duration INTEGER DEFAULT 600,   -- 10 min para Rede
                
                -- Configurações de Supressão
                suppress_during_maintenance BOOLEAN DEFAULT TRUE,
                suppress_acknowledged BOOLEAN DEFAULT TRUE,
                suppress_flapping BOOLEAN DEFAULT TRUE,
                
                -- Configurações de Escalação
                escalation_enabled BOOLEAN DEFAULT FALSE,
                escalation_time_minutes INTEGER DEFAULT 30,
                escalation_severity VARCHAR(20) DEFAULT 'critical',
                
                -- Auditoria
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                UNIQUE(tenant_id)
            );
        """))
        
        print("✅ Tabela threshold_config criada")
        
        # Criar índices
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_threshold_config_tenant 
            ON threshold_config(tenant_id);
        """))
        
        print("✅ Índices criados")
        
        # Inserir configuração padrão para tenant existente
        conn.execute(text("""
            INSERT INTO threshold_config (tenant_id)
            SELECT id FROM tenants 
            WHERE NOT EXISTS (
                SELECT 1 FROM threshold_config WHERE threshold_config.tenant_id = tenants.id
            );
        """))
        
        print("✅ Configurações padrão inseridas")
        
        # Criar tabela de histórico de breaches para tracking
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sensor_breach_history (
                id SERIAL PRIMARY KEY,
                sensor_id INTEGER REFERENCES sensors(id) ON DELETE CASCADE,
                breach_start TIMESTAMP WITH TIME ZONE NOT NULL,
                breach_end TIMESTAMP WITH TIME ZONE,
                breach_value FLOAT,
                threshold_type VARCHAR(20),  -- 'warning' ou 'critical'
                incident_created BOOLEAN DEFAULT FALSE,
                incident_id INTEGER REFERENCES incidents(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """))
        
        print("✅ Tabela sensor_breach_history criada")
        
        # Criar índices para breach history
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_breach_history_sensor 
            ON sensor_breach_history(sensor_id);
            
            CREATE INDEX IF NOT EXISTS idx_breach_history_start 
            ON sensor_breach_history(breach_start);
            
            CREATE INDEX IF NOT EXISTS idx_breach_history_active 
            ON sensor_breach_history(sensor_id, breach_end) 
            WHERE breach_end IS NULL;
        """))
        
        print("✅ Índices de breach history criados")
        
        conn.commit()
        print("\n🎉 Migração concluída com sucesso!")
        print("\n📋 Configurações Padrão (ITIL Best Practices):")
        print("   • CPU: 10 minutos em breach antes de abrir incidente")
        print("   • Memória: 15 minutos")
        print("   • Disco: 30 minutos")
        print("   • Ping: 3 minutos (mais crítico)")
        print("   • Serviços: 2 minutos")
        print("   • Rede: 10 minutos")
        print("   • Flapping Detection: 3 mudanças em 5 minutos")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        sys.exit(1)
