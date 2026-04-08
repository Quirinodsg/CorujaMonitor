from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configurações de notificação
    notification_config = Column(JSON)  # Configurações de Twilio, Teams, WhatsApp, Telegram
    notification_matrix = Column(JSON)  # Matriz de notificação por sensor_type
    
    users = relationship("User", back_populates="tenant")
    probes = relationship("Probe", back_populates="tenant")
    servers = relationship("Server", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    language = Column(String(10), default="pt-BR")
    
    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # TOTP secret
    mfa_backup_codes = Column(JSON, nullable=True)  # Lista de códigos de backup
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="users")

class Probe(Base):
    __tablename__ = "probes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime(timezone=True))
    version = Column(String(50))
    cpu_percent = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="probes")
    servers = relationship("Server", back_populates="probe")

class Server(Base):
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    probe_id = Column(Integer, ForeignKey("probes.id"), nullable=False)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(50))
    public_ip = Column(String(50))
    os_type = Column(String(50))
    os_version = Column(String(100))
    group_name = Column(String(255))  # Para agrupar por empresa/área
    tags = Column(JSON)  # Para tags como criticidade, área, etc
    
    # Novos campos para classificação e monitoramento
    device_type = Column(String(50), default='server')  # server, switch, router, firewall, printer, etc
    monitoring_protocol = Column(String(20), default='wmi')  # wmi, snmp
    snmp_version = Column(String(10))  # v1, v2c, v3
    snmp_community = Column(String(255))  # Community string para SNMP v1/v2c
    snmp_port = Column(Integer, default=161)  # Porta SNMP
    environment = Column(String(50), default='production')  # production, staging, development, custom
    monitoring_schedule = Column(JSON)  # Horários personalizados para ambiente custom
    
    # Credenciais (novo sistema centralizado)
    credential_id = Column(Integer, ForeignKey("credentials.id"), nullable=True)  # Credencial específica
    use_inherited_credential = Column(Boolean, default=True)  # Usar credencial herdada (grupo/tenant)
    
    # WMI Remote credentials (DEPRECATED - usar credential_id)
    wmi_username = Column(String(255))  # Username for WMI remote access
    wmi_password_encrypted = Column(Text)  # Encrypted password for WMI access
    wmi_domain = Column(String(255))  # Windows domain for WMI authentication
    wmi_enabled = Column(Boolean, default=False)  # Enable WMI remote monitoring
    
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)  # Para reordenação na árvore
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant", back_populates="servers")
    probe = relationship("Probe", back_populates="servers")
    sensors = relationship("Sensor", back_populates="server")

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)  # Opcional para sensores standalone
    probe_id = Column(Integer, ForeignKey("probes.id"), nullable=True)  # Para sensores standalone
    name = Column(String(255), nullable=False)
    sensor_type = Column(String(50), nullable=False)  # cpu, memory, disk, network, service, hyperv, udm
    config = Column(JSON)  # Sensor-specific configuration
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    is_active = Column(Boolean, default=True)
    
    # Protocolo de coleta
    collection_protocol = Column(String(20), default='wmi')  # wmi, snmp
    snmp_oid = Column(String(255))  # OID para sensores SNMP
    
    # Campos de verificação técnica
    verification_status = Column(String(50), default="pending")  # pending, in_analysis, verified, resolved
    is_acknowledged = Column(Boolean, default=False)  # Se foi reconhecido por técnico (suprime alertas)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))  # Quem reconheceu
    acknowledged_at = Column(DateTime(timezone=True))  # Quando foi reconhecido
    last_note = Column(Text)  # Última nota do técnico
    last_note_by = Column(Integer, ForeignKey("users.id"))  # Quem fez a última nota
    last_note_at = Column(DateTime(timezone=True))  # Quando foi feita a última nota
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ── Controle de execução estilo PRTG ─────────────────────────────────
    enabled = Column(Boolean, default=True)          # False = nunca executa
    paused_until = Column(DateTime(timezone=True), nullable=True)  # Pausa temporária
    priority = Column(Integer, default=3)            # 1 (baixa) a 5 (crítica/estrelas PRTG)
    alert_mode = Column(String(20), default='normal')  # normal | silent | metric_only
    cooldown_seconds = Column(Integer, default=300)  # Cooldown por sensor em segundos
    # ─────────────────────────────────────────────────────────────────────
    
    server = relationship("Server", back_populates="sensors")
    probe = relationship("Probe", foreign_keys=[probe_id])
    metrics = relationship("Metric", back_populates="sensor")
    notes = relationship("SensorNote", back_populates="sensor", order_by="desc(SensorNote.created_at)")

class Metric(Base):
    __tablename__ = "metrics"
    __table_args__ = (
        Index('idx_metrics_sensor_timestamp', 'sensor_id', 'timestamp'),
        Index('idx_metrics_timestamp', 'timestamp'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    status = Column(String(20))  # ok, warning, critical
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    extra_metadata = Column("metadata", JSON)

    sensor = relationship("Sensor", back_populates="metrics")


class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    severity = Column(String(20), nullable=False)  # warning, critical
    status = Column(String(20), default="open")  # open, acknowledged, resolved, auto_resolved
    title = Column(String(500), nullable=False)
    description = Column(Text)
    root_cause = Column(Text)
    ai_analysis = Column(JSON)
    remediation_attempted = Column(Boolean, default=False, nullable=False)
    remediation_successful = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Acknowledgement fields
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledgement_notes = Column(Text)
    resolution_notes = Column(Text)
    
    sensor = relationship("Sensor")
    remediation_logs = relationship("RemediationLog", back_populates="incident")

class RemediationLog(Base):
    __tablename__ = "remediation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    action_type = Column(String(100), nullable=False)
    action_description = Column(Text)
    before_state = Column(JSON)
    after_state = Column(JSON)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    incident = relationship("Incident", back_populates="remediation_logs")

class AIAnalysisLog(Base):
    __tablename__ = "ai_analysis_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    analysis_type = Column(String(100), nullable=False)  # root_cause, anomaly, recommendation
    input_data = Column(JSON)
    output_data = Column(JSON)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    availability_percentage = Column(Float)
    total_incidents = Column(Integer)
    auto_resolved_incidents = Column(Integer)
    sla_compliance = Column(Float)
    report_data = Column(JSON)
    ai_summary = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_monthly_report_tenant_period', 'tenant_id', 'year', 'month'),
    )

class MaintenanceWindow(Base):
    __tablename__ = "maintenance_windows"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)  # NULL = toda empresa
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_maintenance_window_tenant', 'tenant_id'),
        Index('idx_maintenance_window_server', 'server_id'),
        Index('idx_maintenance_window_time', 'start_time', 'end_time'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SensorNote(Base):
    __tablename__ = "sensor_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # pending, in_analysis, verified, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sensor = relationship("Sensor", back_populates="notes")
    user = relationship("User")


class KnowledgeBaseEntry(Base):
    """
    Knowledge Base - Armazena problemas conhecidos e suas soluções
    A IA aprende com as resoluções dos técnicos
    """
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Identificação do Problema
    problem_signature = Column(String(500), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    
    # Descrição do Problema
    problem_title = Column(String(500), nullable=False)
    problem_description = Column(Text, nullable=False)
    symptoms = Column(JSON)
    
    # Causa Raiz
    root_cause = Column(Text, nullable=False)
    root_cause_confidence = Column(Float, default=0.0)
    
    # Solução
    solution_description = Column(Text, nullable=False)
    solution_steps = Column(JSON, nullable=False)
    solution_commands = Column(JSON)
    
    # Metadados de Aprendizado
    learned_from_incident_id = Column(Integer, ForeignKey("incidents.id"))
    learned_from_user_id = Column(Integer, ForeignKey("users.id"))
    times_matched = Column(Integer, default=0)
    times_successful = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Auto-Resolução
    auto_resolution_enabled = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    risk_level = Column(String(20), default="medium")
    
    # Contexto Adicional
    affected_os = Column(JSON)
    affected_versions = Column(JSON)
    prerequisites = Column(JSON)
    rollback_steps = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_matched_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_kb_tenant_sensor', 'tenant_id', 'sensor_type'),
        Index('idx_kb_signature', 'problem_signature'),
        Index('idx_kb_success_rate', 'success_rate'),
    )


class AutoResolutionConfig(Base):
    """
    Configuração de Auto-Resolução por Tenant
    """
    __tablename__ = "auto_resolution_config"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    
    # Configurações Globais
    auto_resolution_enabled = Column(Boolean, default=False)
    require_approval_for_critical = Column(Boolean, default=True)
    min_confidence_threshold = Column(Float, default=0.80)
    min_success_rate_threshold = Column(Float, default=0.85)
    
    # Configurações por Tipo de Sensor
    cpu_auto_resolve = Column(Boolean, default=False)
    cpu_max_risk_level = Column(String(20), default="low")
    
    memory_auto_resolve = Column(Boolean, default=False)
    memory_max_risk_level = Column(String(20), default="low")
    
    disk_auto_resolve = Column(Boolean, default=True)
    disk_max_risk_level = Column(String(20), default="medium")
    
    service_auto_resolve = Column(Boolean, default=False)
    service_max_risk_level = Column(String(20), default="low")
    
    network_auto_resolve = Column(Boolean, default=False)
    network_max_risk_level = Column(String(20), default="low")
    
    # Horários Permitidos
    allowed_hours_start = Column(Integer, default=0)
    allowed_hours_end = Column(Integer, default=23)
    allowed_days = Column(JSON)
    
    # Notificações
    notify_before_execution = Column(Boolean, default=True)
    notify_after_execution = Column(Boolean, default=True)
    notification_channels = Column(JSON)
    
    # Limites de Segurança
    max_executions_per_hour = Column(Integer, default=5)
    max_executions_per_day = Column(Integer, default=20)
    cooldown_minutes = Column(Integer, default=30)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ResolutionAttempt(Base):
    """
    Log de tentativas de resolução automática
    """
    __tablename__ = "resolution_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    
    # Detalhes da Tentativa
    problem_signature = Column(String(500), nullable=False)
    solution_applied = Column(Text, nullable=False)
    commands_executed = Column(JSON)
    
    # Resultado
    status = Column(String(50), nullable=False)
    success = Column(Boolean)
    error_message = Column(Text)
    execution_time_seconds = Column(Float)
    
    # Estado Antes/Depois
    state_before = Column(JSON)
    state_after = Column(JSON)
    
    # Aprovação
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    
    # Feedback do Técnico
    technician_feedback = Column(Text)
    feedback_rating = Column(Integer)
    feedback_by = Column(Integer, ForeignKey("users.id"))
    feedback_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_resolution_tenant_incident', 'tenant_id', 'incident_id'),
        Index('idx_resolution_status', 'status'),
        Index('idx_resolution_created', 'created_at'),
    )


class LearningSession(Base):
    """
    Sessão de Aprendizado - Quando técnico resolve um incidente
    """
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dados Capturados
    problem_description = Column(Text, nullable=False)
    root_cause_identified = Column(Text)
    solution_applied = Column(Text, nullable=False)
    resolution_steps = Column(JSON)
    commands_used = Column(JSON)
    
    # Contexto
    sensor_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    resolution_time_minutes = Column(Integer)
    
    # Aprendizado
    added_to_knowledge_base = Column(Boolean, default=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    confidence_score = Column(Float)
    
    # Feedback
    was_successful = Column(Boolean)
    technician_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    learned_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_learning_tenant', 'tenant_id'),
        Index('idx_learning_incident', 'incident_id'),
        Index('idx_learning_created', 'created_at'),
    )



class ThresholdConfig(Base):
    """Configuração de thresholds temporais baseada em ITIL"""
    __tablename__ = "threshold_config"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    
    # Configurações Temporais (ITIL Best Practices)
    breach_duration_seconds = Column(Integer, default=600)  # 10 minutos padrão
    flapping_window_seconds = Column(Integer, default=300)  # 5 minutos para detectar flapping
    flapping_threshold = Column(Integer, default=3)  # 3 mudanças = flapping
    
    # Configurações por Tipo de Sensor
    cpu_breach_duration = Column(Integer, default=600)  # 10 min para CPU
    memory_breach_duration = Column(Integer, default=900)  # 15 min para Memória
    disk_breach_duration = Column(Integer, default=1800)  # 30 min para Disco
    ping_breach_duration = Column(Integer, default=180)  # 3 min para Ping (mais crítico)
    service_breach_duration = Column(Integer, default=120)  # 2 min para Serviços
    network_breach_duration = Column(Integer, default=600)  # 10 min para Rede
    
    # Configurações de Supressão
    suppress_during_maintenance = Column(Boolean, default=True)
    suppress_acknowledged = Column(Boolean, default=True)
    suppress_flapping = Column(Boolean, default=True)
    
    # Configurações de Escalação
    escalation_enabled = Column(Boolean, default=False)
    escalation_time_minutes = Column(Integer, default=30)
    escalation_severity = Column(String(20), default='critical')
    
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SensorBreachHistory(Base):
    """Histórico de breaches para tracking temporal"""
    __tablename__ = "sensor_breach_history"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    breach_start = Column(DateTime(timezone=True), nullable=False)
    breach_end = Column(DateTime(timezone=True))
    breach_value = Column(Float)
    threshold_type = Column(String(20))  # 'warning' ou 'critical'
    incident_created = Column(Boolean, default=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_breach_history_sensor', 'sensor_id'),
        Index('idx_breach_history_start', 'breach_start'),
        Index('idx_breach_history_active', 'sensor_id', 'breach_end'),
    )

class CustomReport(Base):
    __tablename__ = "custom_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)  # incidents, servers, availability, performance, errors
    filters = Column(JSON)  # Filtros aplicados: período, servidores, severidade, tags, etc
    columns = Column(JSON)  # Colunas a serem exibidas
    sort_by = Column(String(100))  # Campo para ordenação
    sort_order = Column(String(10), default='desc')  # asc ou desc
    is_public = Column(Boolean, default=False)  # Visível para outros usuários do tenant
    is_favorite = Column(Boolean, default=False)  # Marcado como favorito
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_generated_at = Column(DateTime(timezone=True))  # Última vez que foi gerado
    
    __table_args__ = (
        Index('idx_custom_reports_tenant', 'tenant_id'),
        Index('idx_custom_reports_user', 'user_id'),
        Index('idx_custom_reports_type', 'report_type'),
    )


class KubernetesCluster(Base):
    """Configuração de clusters Kubernetes para monitoramento"""
    __tablename__ = "kubernetes_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    probe_id = Column(Integer, ForeignKey("probes.id"), nullable=True)  # Probe responsável pela coleta
    
    # Informações básicas
    cluster_name = Column(String(255), nullable=False)
    cluster_type = Column(String(50), nullable=False)  # vanilla, aks, eks, gke, openshift
    api_endpoint = Column(String(500), nullable=False)
    
    # Autenticação
    auth_method = Column(String(50), nullable=False)  # kubeconfig, service_account, token
    kubeconfig_content = Column(Text)  # Conteúdo do kubeconfig (criptografado)
    service_account_token = Column(Text)  # Token do service account (criptografado)
    ca_cert = Column(Text)  # Certificado CA (opcional)
    
    # Configuração de monitoramento
    monitor_all_namespaces = Column(Boolean, default=True)
    namespaces = Column(JSON)  # Lista de namespaces específicos se não monitorar todos
    selected_resources = Column(JSON)  # Lista de tipos de recursos: nodes, pods, deployments, etc
    
    # Intervalo de coleta
    collection_interval = Column(Integer, default=60)  # Segundos
    
    # Status
    is_active = Column(Boolean, default=True)
    last_connection_test = Column(DateTime(timezone=True))
    connection_status = Column(String(50))  # connected, error, untested
    connection_error = Column(Text)  # Último erro de conexão
    
    # Métricas agregadas
    total_nodes = Column(Integer, default=0)
    total_pods = Column(Integer, default=0)
    total_deployments = Column(Integer, default=0)
    cluster_cpu_usage = Column(Float, default=0.0)  # Percentual
    cluster_memory_usage = Column(Float, default=0.0)  # Percentual
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_collected_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_k8s_clusters_tenant', 'tenant_id'),
        Index('idx_k8s_clusters_probe', 'probe_id'),
        Index('idx_k8s_clusters_active', 'is_active'),
    )


class KubernetesResource(Base):
    """Recursos Kubernetes descobertos (nodes, pods, deployments, etc)"""
    __tablename__ = "kubernetes_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id"), nullable=False)
    
    # Identificação do recurso
    resource_type = Column(String(50), nullable=False)  # node, pod, deployment, daemonset, statefulset, service, ingress, pv
    resource_name = Column(String(255), nullable=False)
    namespace = Column(String(255))  # Null para recursos cluster-level (nodes, pv)
    uid = Column(String(255))  # UID único do Kubernetes
    
    # Metadados
    labels = Column(JSON)  # Labels do recurso
    annotations = Column(JSON)  # Annotations do recurso
    
    # Status atual
    status = Column(String(50))  # Running, Pending, Failed, etc
    phase = Column(String(50))  # Para pods
    ready = Column(Boolean, default=False)
    
    # Métricas específicas por tipo
    metrics = Column(JSON)  # Métricas específicas do recurso
    
    # Para Nodes
    node_cpu_capacity = Column(Float)  # Cores
    node_memory_capacity = Column(Float)  # Bytes
    node_cpu_usage = Column(Float)  # Percentual
    node_memory_usage = Column(Float)  # Percentual
    node_pod_count = Column(Integer)
    node_pod_capacity = Column(Integer)
    
    # Para Pods
    pod_cpu_usage = Column(Float)  # Millicores
    pod_memory_usage = Column(Float)  # Bytes
    pod_restart_count = Column(Integer, default=0)
    pod_node_name = Column(String(255))  # Node onde o pod está rodando
    
    # Para Deployments/DaemonSets/StatefulSets
    desired_replicas = Column(Integer)
    ready_replicas = Column(Integer)
    available_replicas = Column(Integer)
    updated_replicas = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_k8s_resources_cluster', 'cluster_id'),
        Index('idx_k8s_resources_type', 'resource_type'),
        Index('idx_k8s_resources_namespace', 'namespace'),
        Index('idx_k8s_resources_status', 'status'),
        Index('idx_k8s_resources_uid', 'uid'),
    )


class KubernetesMetric(Base):
    """Métricas históricas de recursos Kubernetes"""
    __tablename__ = "kubernetes_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("kubernetes_resources.id"), nullable=False)
    
    # Métricas
    cpu_usage = Column(Float)  # Millicores ou percentual
    memory_usage = Column(Float)  # Bytes ou percentual
    network_rx_bytes = Column(Float)
    network_tx_bytes = Column(Float)
    disk_usage = Column(Float)  # Percentual
    
    # Status
    status = Column(String(50))
    ready = Column(Boolean)
    restart_count = Column(Integer)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_k8s_metrics_resource', 'resource_id'),
        Index('idx_k8s_metrics_timestamp', 'timestamp'),
    )


class KubernetesAlert(Base):
    """Alertas de Kubernetes"""
    __tablename__ = "kubernetes_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("kubernetes_resources.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Tipo e severidade
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    
    # Detalhes
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_name = Column(String(255), nullable=True)
    namespace = Column(String(255), nullable=True)
    
    # Métricas
    current_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), default="active", index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(Integer, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Metadados
    alert_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_k8s_alerts_cluster', 'cluster_id'),
        Index('idx_k8s_alerts_status', 'status'),
        Index('idx_k8s_alerts_severity', 'severity'),
        Index('idx_k8s_alerts_created', 'created_at'),
    )


class KubernetesAlertRule(Base):
    """Regras de Alerta para Kubernetes"""
    __tablename__ = "kubernetes_alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Configuração da regra
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Condições
    resource_type = Column(String(50), nullable=True)
    metric_name = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)
    threshold = Column(Float, nullable=False)
    duration = Column(Integer, default=60)
    
    # Filtros
    namespace_filter = Column(String(255), nullable=True)
    label_filter = Column(JSON, default={})
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Notificações
    notify_email = Column(Boolean, default=True)
    notify_webhook = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_k8s_alert_rules_tenant', 'tenant_id'),
        Index('idx_k8s_alert_rules_active', 'is_active'),
    )


class Credential(Base):
    """
    Credenciais Centralizadas para WMI/SNMP/SSH
    Sistema moderno como PRTG/SolarWinds/CheckMK
    Suporta herança: Servidor → Grupo → Empresa (Tenant)
    """
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Identificação
    name = Column(String(255), nullable=False)  # "Domínio Principal", "SNMP Switches", etc
    description = Column(Text)
    
    # Tipo de Credencial
    credential_type = Column(String(20), nullable=False, index=True)  # wmi, snmp_v1, snmp_v2c, snmp_v3, ssh
    
    # Nível de Aplicação (herança)
    level = Column(String(20), nullable=False, default='tenant', index=True)  # tenant, group, server
    group_name = Column(String(255), nullable=True, index=True)  # Se level=group
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True, index=True)  # Se level=server
    
    # Credenciais WMI
    wmi_username = Column(String(255))
    wmi_password_encrypted = Column(Text)
    wmi_domain = Column(String(255))
    
    # Credenciais SNMP v1/v2c
    snmp_community = Column(String(255))
    snmp_port = Column(Integer, default=161)
    
    # Credenciais SNMP v3
    snmp_username = Column(String(255))
    snmp_auth_protocol = Column(String(20))  # MD5, SHA, SHA224, SHA256, SHA384, SHA512
    snmp_auth_password_encrypted = Column(Text)
    snmp_priv_protocol = Column(String(20))  # DES, 3DES, AES, AES192, AES256
    snmp_priv_password_encrypted = Column(Text)
    snmp_context = Column(String(255))
    
    # Credenciais SSH
    ssh_username = Column(String(255))
    ssh_password_encrypted = Column(Text)
    ssh_private_key_encrypted = Column(Text)
    ssh_port = Column(Integer, default=22)
    
    # Configurações
    is_default = Column(Boolean, default=False)  # Credencial padrão para o nível
    is_active = Column(Boolean, default=True)
    
    # Teste de Conectividade
    last_test_at = Column(DateTime(timezone=True))
    last_test_status = Column(String(20))  # success, failed, untested
    last_test_message = Column(Text)
    
    # Auditoria
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_credentials_tenant', 'tenant_id'),
        Index('idx_credentials_type', 'credential_type'),
        Index('idx_credentials_level', 'level'),
        Index('idx_credentials_group', 'group_name'),
        Index('idx_credentials_server', 'server_id'),
        Index('idx_credentials_default', 'is_default'),
        {'extend_existing': True}
    )


class AuthenticationConfig(Base):
    """
    Configuração de Autenticação Enterprise
    Suporta LDAP, SAML, OAuth2, Azure AD, Google, Okta, MFA, etc.
    """
    __tablename__ = "authentication_config"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True)
    
    # LDAP / Active Directory
    ldap_config = Column(JSON, default={})
    
    # SAML 2.0
    saml_config = Column(JSON, default={})
    
    # OAuth2 / OpenID Connect
    oauth2_config = Column(JSON, default={})
    
    # Azure AD (Entra ID)
    azure_ad_config = Column(JSON, default={})
    
    # Google Workspace
    google_config = Column(JSON, default={})
    
    # Okta
    okta_config = Column(JSON, default={})
    
    # MFA / 2FA
    mfa_config = Column(JSON, default={})
    
    # Password Policy
    password_policy = Column(JSON, default={})
    
    # Session Management
    session_config = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_auth_config_tenant', 'tenant_id'),
    )


class AutoHealingAction(Base):
    """Registro de ações de auto-healing executadas pelo AutoHealingEngine."""
    __tablename__ = "auto_healing_actions"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    rule_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    description = Column(Text)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    duration_ms = Column(Integer, default=0)
    metric_snapshot = Column(JSON)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_healing_sensor', 'sensor_id'),
        Index('idx_healing_executed', 'executed_at'),
        Index('idx_healing_success', 'success'),
    )


class PredictionSample(Base):
    """
    Histórico de amostras para o FailurePredictor.
    Persiste dados entre restarts do container.
    """
    __tablename__ = "prediction_samples"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)

    sensor = relationship("Sensor")

    __table_args__ = (
        Index('idx_prediction_samples_sensor_ts', 'sensor_id', 'timestamp'),
    )


class DefaultSensorProfile(Base):
    """
    Perfis padrão de sensores por tipo de ativo (v3.5 Enterprise Hardening).
    Aplicados automaticamente ao criar novos servidores.
    """
    __tablename__ = "default_sensor_profiles"

    id                 = Column(Integer, primary_key=True, index=True)
    asset_type         = Column(String(50), nullable=False)   # VM | physical_server | network_device
    sensor_type        = Column(String(50), nullable=False)   # cpu | memory | disk | network_in | ...
    enabled            = Column(Boolean, default=True)
    alert_mode         = Column(String(20), default='normal') # normal | silent | metric_only
    threshold_warning  = Column(Float, nullable=True)
    threshold_critical = Column(Float, nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('asset_type', 'sensor_type', name='uq_profile_asset_sensor'),
        Index('idx_default_profiles_asset_type', 'asset_type'),
    )


# ── Hyper-V Observability Dashboard ──────────────────────────────────────────
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class HyperVHost(Base):
    __tablename__ = "hyperv_hosts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=False)
    total_cpus = Column(Integer, nullable=False)
    total_memory_gb = Column(Float, nullable=False)
    total_storage_gb = Column(Float, nullable=False)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    storage_percent = Column(Float)
    vm_count = Column(Integer, default=0)
    running_vm_count = Column(Integer, default=0)
    status = Column(String(20), default="unknown")
    health_score = Column(Float, default=0)
    wmi_latency_ms = Column(Float)
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    bios_version = Column(String(255))
    os_version = Column(String(255))
    processor_name = Column(String(255))
    processor_sockets = Column(Integer)
    cores_per_socket = Column(Integer)
    last_seen = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vms = relationship("HyperVVM", back_populates="host")


class HyperVVM(Base):
    __tablename__ = "hyperv_vms"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host_id = Column(PG_UUID(as_uuid=True), ForeignKey("hyperv_hosts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    state = Column(String(20), nullable=False)
    vcpus = Column(Integer)
    memory_mb = Column(Integer)
    memory_demand_mb = Column(Integer)
    disk_bytes = Column(Float)
    disk_max_bytes = Column(Float)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    uptime_seconds = Column(Float)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    host = relationship("HyperVHost", back_populates="vms")


class HyperVMetric(Base):
    __tablename__ = "hyperv_metrics"
    __table_args__ = (
        Index('idx_hyperv_metrics_host_ts', 'host_id', 'timestamp'),
        Index('idx_hyperv_metrics_vm_ts', 'vm_id', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(PG_UUID(as_uuid=True), ForeignKey("hyperv_hosts.id"), nullable=False)
    vm_id = Column(PG_UUID(as_uuid=True), ForeignKey("hyperv_vms.id"), nullable=True)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)


class HyperVFinOpsRecommendation(Base):
    __tablename__ = "hyperv_finops_recommendations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vm_id = Column(PG_UUID(as_uuid=True), ForeignKey("hyperv_vms.id"))
    host_id = Column(PG_UUID(as_uuid=True), ForeignKey("hyperv_hosts.id"))
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    suggested_action = Column(Text, nullable=False)
    estimated_savings = Column(Float)
    confidence = Column(Float)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
