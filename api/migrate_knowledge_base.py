"""
Migration: Add Knowledge Base and Auto-Resolution Configuration
Creates tables for AI learning from technician resolutions
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from config import settings
import sys

Base = declarative_base()

class KnowledgeBaseEntry(Base):
    """
    Knowledge Base - Armazena problemas conhecidos e suas soluções
    A IA aprende com as resoluções dos técnicos
    """
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Identificação do Problema
    problem_signature = Column(String(500), nullable=False, index=True)  # Assinatura única do problema
    sensor_type = Column(String(50), nullable=False, index=True)  # cpu, memory, disk, service, etc
    severity = Column(String(20), nullable=False)  # warning, critical
    
    # Descrição do Problema
    problem_title = Column(String(500), nullable=False)
    problem_description = Column(Text, nullable=False)
    symptoms = Column(JSON)  # Lista de sintomas observados
    
    # Causa Raiz
    root_cause = Column(Text, nullable=False)
    root_cause_confidence = Column(Float, default=0.0)  # 0.0 a 1.0
    
    # Solução
    solution_description = Column(Text, nullable=False)
    solution_steps = Column(JSON, nullable=False)  # Lista de passos para resolver
    solution_commands = Column(JSON)  # Comandos PowerShell/Bash para executar
    
    # Metadados de Aprendizado
    learned_from_incident_id = Column(Integer, ForeignKey("incidents.id"))  # Incidente original
    learned_from_user_id = Column(Integer, ForeignKey("users.id"))  # Técnico que resolveu
    times_matched = Column(Integer, default=0)  # Quantas vezes foi identificado
    times_successful = Column(Integer, default=0)  # Quantas vezes a solução funcionou
    success_rate = Column(Float, default=0.0)  # Taxa de sucesso (0.0 a 1.0)
    
    # Auto-Resolução
    auto_resolution_enabled = Column(Boolean, default=False)  # Se pode ser resolvido automaticamente
    requires_approval = Column(Boolean, default=True)  # Se requer aprovação antes de executar
    risk_level = Column(String(20), default="medium")  # low, medium, high
    
    # Contexto Adicional
    affected_os = Column(JSON)  # Lista de sistemas operacionais afetados
    affected_versions = Column(JSON)  # Versões específicas afetadas
    prerequisites = Column(JSON)  # Pré-requisitos para aplicar a solução
    rollback_steps = Column(JSON)  # Passos para reverter se der errado
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_matched_at = Column(DateTime(timezone=True))  # Última vez que foi identificado
    
    # Índices para busca rápida
    __table_args__ = (
        Index('idx_kb_tenant_sensor', 'tenant_id', 'sensor_type'),
        Index('idx_kb_signature', 'problem_signature'),
        Index('idx_kb_success_rate', 'success_rate'),
    )


class AutoResolutionConfig(Base):
    """
    Configuração de Auto-Resolução por Tenant
    Admin escolhe quais tipos de problemas a IA pode resolver automaticamente
    """
    __tablename__ = "auto_resolution_config"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    
    # Configurações Globais
    auto_resolution_enabled = Column(Boolean, default=False)  # Master switch
    require_approval_for_critical = Column(Boolean, default=True)  # Sempre pedir aprovação para críticos
    min_confidence_threshold = Column(Float, default=0.80)  # Confiança mínima para auto-resolver (0.0 a 1.0)
    min_success_rate_threshold = Column(Float, default=0.85)  # Taxa de sucesso mínima (0.0 a 1.0)
    
    # Configurações por Tipo de Sensor
    cpu_auto_resolve = Column(Boolean, default=False)
    cpu_max_risk_level = Column(String(20), default="low")  # low, medium, high
    
    memory_auto_resolve = Column(Boolean, default=False)
    memory_max_risk_level = Column(String(20), default="low")
    
    disk_auto_resolve = Column(Boolean, default=True)  # Geralmente seguro limpar disco
    disk_max_risk_level = Column(String(20), default="medium")
    
    service_auto_resolve = Column(Boolean, default=False)  # Reiniciar serviços pode ser arriscado
    service_max_risk_level = Column(String(20), default="low")
    
    network_auto_resolve = Column(Boolean, default=False)
    network_max_risk_level = Column(String(20), default="low")
    
    # Horários Permitidos para Auto-Resolução
    allowed_hours_start = Column(Integer, default=0)  # 0-23
    allowed_hours_end = Column(Integer, default=23)  # 0-23
    allowed_days = Column(JSON, default=list)  # [0,1,2,3,4,5,6] (0=domingo)
    
    # Notificações
    notify_before_execution = Column(Boolean, default=True)
    notify_after_execution = Column(Boolean, default=True)
    notification_channels = Column(JSON, default=list)  # ['email', 'teams', 'telegram']
    
    # Limites de Segurança
    max_executions_per_hour = Column(Integer, default=5)  # Máximo de auto-resoluções por hora
    max_executions_per_day = Column(Integer, default=20)  # Máximo por dia
    cooldown_minutes = Column(Integer, default=30)  # Tempo de espera entre execuções no mesmo servidor
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ResolutionAttempt(Base):
    """
    Log de tentativas de resolução automática
    Rastreia todas as execuções da IA
    """
    __tablename__ = "resolution_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    
    # Detalhes da Tentativa
    problem_signature = Column(String(500), nullable=False)
    solution_applied = Column(Text, nullable=False)
    commands_executed = Column(JSON)  # Lista de comandos executados
    
    # Resultado
    status = Column(String(50), nullable=False)  # pending, executing, success, failed, rolled_back
    success = Column(Boolean)
    error_message = Column(Text)
    execution_time_seconds = Column(Float)
    
    # Estado Antes/Depois
    state_before = Column(JSON)  # Estado do sistema antes
    state_after = Column(JSON)  # Estado do sistema depois
    
    # Aprovação (se necessário)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    
    # Feedback do Técnico
    technician_feedback = Column(Text)  # Feedback sobre se a resolução foi boa
    feedback_rating = Column(Integer)  # 1-5 estrelas
    feedback_by = Column(Integer, ForeignKey("users.id"))
    feedback_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Índices
    __table_args__ = (
        Index('idx_resolution_tenant_incident', 'tenant_id', 'incident_id'),
        Index('idx_resolution_status', 'status'),
        Index('idx_resolution_created', 'created_at'),
    )


class LearningSession(Base):
    """
    Sessão de Aprendizado - Quando técnico resolve um incidente
    A IA captura a resolução e aprende com ela
    """
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Técnico que resolveu
    
    # Dados Capturados
    problem_description = Column(Text, nullable=False)
    root_cause_identified = Column(Text)
    solution_applied = Column(Text, nullable=False)
    resolution_steps = Column(JSON)  # Passos que o técnico seguiu
    commands_used = Column(JSON)  # Comandos que o técnico executou
    
    # Contexto
    sensor_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    resolution_time_minutes = Column(Integer)  # Tempo que levou para resolver
    
    # Aprendizado
    added_to_knowledge_base = Column(Boolean, default=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    confidence_score = Column(Float)  # Confiança da IA na solução (0.0 a 1.0)
    
    # Feedback
    was_successful = Column(Boolean)
    technician_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    learned_at = Column(DateTime(timezone=True))  # Quando foi adicionado à KB
    
    # Índices
    __table_args__ = (
        Index('idx_learning_tenant', 'tenant_id'),
        Index('idx_learning_incident', 'incident_id'),
        Index('idx_learning_created', 'created_at'),
    )


def run_migration():
    """Execute migration"""
    print("🔄 Starting Knowledge Base migration...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # Create tables
        print("📊 Creating knowledge_base table...")
        KnowledgeBaseEntry.__table__.create(engine, checkfirst=True)
        
        print("⚙️  Creating auto_resolution_config table...")
        AutoResolutionConfig.__table__.create(engine, checkfirst=True)
        
        print("📝 Creating resolution_attempts table...")
        ResolutionAttempt.__table__.create(engine, checkfirst=True)
        
        print("🎓 Creating learning_sessions table...")
        LearningSession.__table__.create(engine, checkfirst=True)
        
        print("✅ Migration completed successfully!")
        print("\n📚 Knowledge Base System Ready:")
        print("   - AI can now learn from technician resolutions")
        print("   - Auto-resolution can be configured per tenant")
        print("   - All resolution attempts are logged")
        print("   - Learning sessions capture problem-solving patterns")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
