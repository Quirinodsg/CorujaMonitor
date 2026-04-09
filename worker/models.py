# Shared models for worker
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    notification_config = Column(JSON)  # Configuração de notificações (TOPdesk, Teams, Email, etc)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    role = Column(String(50), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Probe(Base):
    __tablename__ = "probes"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String(255), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    last_heartbeat = Column(DateTime)
    version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    probe_id = Column(Integer, ForeignKey("probes.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(50))
    public_ip = Column(String(50))
    os_type = Column(String(100))
    os_version = Column(String(100))
    group_name = Column(String(255))
    tags = Column(JSON)
    device_type = Column(String(50), default="server")
    monitoring_protocol = Column(String(20), default="wmi")
    snmp_version = Column(String(10))
    snmp_community = Column(String(100))
    snmp_port = Column(Integer)
    environment = Column(String(50), default="production")
    monitoring_schedule = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)
    probe_id = Column(Integer, ForeignKey("probes.id"), nullable=True)
    sensor_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    config = Column(JSON)
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    threshold_custom = Column(Boolean, default=False)  # True = personalizado, não sobrescrever com padrão
    is_active = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    paused_until = Column(DateTime, nullable=True)
    alert_mode = Column(String(20), default='normal')
    priority = Column(Integer, default=3)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    verification_status = Column(String(50))
    last_note = Column(Text)
    last_note_by = Column(Integer, ForeignKey("users.id"))
    last_note_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    status = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    severity = Column(String(50), nullable=False)
    status = Column(String(50), default="open")
    title = Column(String(500), nullable=False)
    description = Column(Text)
    root_cause = Column(Text)
    ai_analysis = Column(JSON)
    remediation_attempted = Column(Boolean, default=False)
    remediation_successful = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)

class RemediationLog(Base):
    __tablename__ = "remediation_logs"
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    action_type = Column(String(100), nullable=False)
    action_description = Column(Text)
    before_state = Column(JSON)
    after_state = Column(JSON)
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)

class SensorNote(Base):
    __tablename__ = "sensor_notes"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    note = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    report_type = Column(String(50), nullable=False)
    report_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class MaintenanceWindow(Base):
    __tablename__ = "maintenance_windows"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=True)  # NULL = toda empresa
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

