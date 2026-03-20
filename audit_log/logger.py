"""
Audit Log — Coruja Monitor v3.5 Enterprise
Registra ações de usuários, IA e mudanças no sistema.
Integrado ao modelo AuditLog existente em models.py.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logger de auditoria centralizado.
    Persiste no banco via modelo AuditLog existente.
    Fallback: log em arquivo se banco indisponível.
    """

    # Categorias de ação
    ACTION_LOGIN = "user.login"
    ACTION_LOGOUT = "user.logout"
    ACTION_SENSOR_PAUSE = "sensor.pause"
    ACTION_SENSOR_RESUME = "sensor.resume"
    ACTION_SENSOR_CREATE = "sensor.create"
    ACTION_SENSOR_DELETE = "sensor.delete"
    ACTION_SERVER_CREATE = "server.create"
    ACTION_SERVER_DELETE = "server.delete"
    ACTION_INCIDENT_ACK = "incident.acknowledge"
    ACTION_INCIDENT_RESOLVE = "incident.resolve"
    ACTION_AI_REMEDIATION = "ai.remediation"
    ACTION_AI_HEALING = "ai.healing"
    ACTION_AI_PREDICTION = "ai.prediction"
    ACTION_CONFIG_CHANGE = "config.change"
    ACTION_THRESHOLD_CHANGE = "threshold.change"
    ACTION_USER_CREATE = "user.create"
    ACTION_USER_DELETE = "user.delete"
    ACTION_SYSTEM_RESET = "system.reset"

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def log(
        self,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[dict] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> bool:
        """Registra entrada de auditoria."""
        try:
            if self.db:
                from models import AuditLog
                entry = AuditLog(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details or {},
                    ip_address=ip_address,
                )
                self.db.add(entry)
                self.db.commit()
            else:
                # Fallback para log estruturado
                logger.info(
                    "AUDIT | action=%s resource=%s/%s user=%s tenant=%s details=%s",
                    action, resource_type, resource_id, user_id, tenant_id, details,
                )
            return True
        except Exception as e:
            logger.error("AuditLogger.log error: %s", e)
            if self.db:
                try:
                    self.db.rollback()
                except Exception:
                    pass
            return False

    def log_ai_action(
        self,
        action: str,
        details: dict,
        tenant_id: Optional[int] = None,
    ) -> bool:
        """Registra ação da IA (remediação, predição, healing)."""
        return self.log(
            action=action,
            resource_type="ai_agent",
            details=details,
            tenant_id=tenant_id,
            user_id=None,  # IA não tem user_id
        )


# Instância global (sem DB — usa log estruturado como fallback)
_global_audit = AuditLogger()


def get_audit_logger(db: Optional[Session] = None) -> AuditLogger:
    """Factory — retorna logger com DB se disponível."""
    if db:
        return AuditLogger(db=db)
    return _global_audit
