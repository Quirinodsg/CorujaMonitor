"""
QA Enterprise — Audit Log v3.5
Testa: log com DB, fallback sem DB, log_ai_action, constantes de ação,
get_audit_logger factory, rollback em erro.
"""
import sys
import pytest
import logging
from unittest.mock import MagicMock, patch, call

# Injetar mock de 'models' e 'database' para evitar import de api/config.py (Pydantic v2)
# Deve ser feito ANTES do import dos módulos do projeto
import types
_mock_models_module = types.ModuleType("models")
_mock_models_module.AuditLog = MagicMock
if "models" not in sys.modules:
    sys.modules["models"] = _mock_models_module
if "database" not in sys.modules:
    sys.modules["database"] = types.ModuleType("database")

from audit_log.logger import AuditLogger, get_audit_logger


# ─── 1. Constantes de Ação ───────────────────────────────────────────────────

class TestActionConstants:
    def test_all_action_constants_defined(self):
        """Todas as constantes de ação devem estar definidas."""
        expected = [
            "ACTION_LOGIN", "ACTION_LOGOUT", "ACTION_SENSOR_PAUSE",
            "ACTION_SENSOR_RESUME", "ACTION_SENSOR_CREATE", "ACTION_SENSOR_DELETE",
            "ACTION_SERVER_CREATE", "ACTION_SERVER_DELETE", "ACTION_INCIDENT_ACK",
            "ACTION_INCIDENT_RESOLVE", "ACTION_AI_REMEDIATION", "ACTION_AI_HEALING",
            "ACTION_AI_PREDICTION", "ACTION_CONFIG_CHANGE", "ACTION_THRESHOLD_CHANGE",
            "ACTION_USER_CREATE", "ACTION_USER_DELETE", "ACTION_SYSTEM_RESET",
        ]
        for const in expected:
            assert hasattr(AuditLogger, const), f"Constante faltando: {const}"

    def test_action_values_are_dot_notation(self):
        """Valores de ação devem usar notação dot (ex: user.login)."""
        assert "." in AuditLogger.ACTION_LOGIN
        assert "." in AuditLogger.ACTION_AI_REMEDIATION
        assert "." in AuditLogger.ACTION_SYSTEM_RESET

    def test_action_values_unique(self):
        """Todos os valores de ação devem ser únicos."""
        actions = [
            AuditLogger.ACTION_LOGIN, AuditLogger.ACTION_LOGOUT,
            AuditLogger.ACTION_SENSOR_PAUSE, AuditLogger.ACTION_SENSOR_RESUME,
            AuditLogger.ACTION_SENSOR_CREATE, AuditLogger.ACTION_SENSOR_DELETE,
            AuditLogger.ACTION_AI_REMEDIATION, AuditLogger.ACTION_AI_HEALING,
            AuditLogger.ACTION_AI_PREDICTION, AuditLogger.ACTION_SYSTEM_RESET,
        ]
        assert len(actions) == len(set(actions)), "Valores de ação duplicados detectados"


# ─── 2. log() com DB ─────────────────────────────────────────────────────────

class TestLogWithDb:
    def _make_mock_db(self):
        return MagicMock()

    def test_log_calls_db_add_and_commit(self):
        """log() com DB deve chamar db.add() e db.commit()."""
        mock_db = self._make_mock_db()
        logger = AuditLogger(db=mock_db)

        mock_audit_log_cls = MagicMock()
        mock_audit_log_cls.return_value = MagicMock()
        sys.modules["models"].AuditLog = mock_audit_log_cls

        result = logger.log(
            action="user.login",
            resource_type="user",
            resource_id=1,
            details={"ip": "192.168.1.1"},
            user_id=42,
            tenant_id=1,
            ip_address="192.168.1.1",
        )
        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_log_creates_audit_log_with_correct_fields(self):
        """AuditLog criado com os campos corretos."""
        mock_db = self._make_mock_db()
        logger = AuditLogger(db=mock_db)

        mock_audit_log_cls = MagicMock()
        mock_audit_log_cls.return_value = MagicMock()
        sys.modules["models"].AuditLog = mock_audit_log_cls

        logger.log(
            action="sensor.pause",
            resource_type="sensor",
            resource_id=99,
            user_id=5,
            tenant_id=2,
            ip_address="10.0.0.1",
        )
        call_kwargs = mock_audit_log_cls.call_args[1]
        assert call_kwargs["action"] == "sensor.pause"
        assert call_kwargs["resource_type"] == "sensor"
        assert call_kwargs["resource_id"] == 99
        assert call_kwargs["user_id"] == 5
        assert call_kwargs["tenant_id"] == 2
        assert call_kwargs["ip_address"] == "10.0.0.1"

    def test_log_returns_false_on_db_error(self):
        """log() retorna False se db.commit() lança exceção."""
        mock_db = self._make_mock_db()
        mock_db.commit.side_effect = Exception("Connection lost")
        logger = AuditLogger(db=mock_db)
        sys.modules["models"].AuditLog = MagicMock(return_value=MagicMock())
        result = logger.log(action="user.login")
        assert result is False

    def test_log_rollback_on_db_error(self):
        """log() faz rollback quando db.commit() falha."""
        mock_db = self._make_mock_db()
        mock_db.commit.side_effect = Exception("DB error")
        logger = AuditLogger(db=mock_db)
        sys.modules["models"].AuditLog = MagicMock(return_value=MagicMock())
        logger.log(action="user.login")
        mock_db.rollback.assert_called_once()

    def test_log_details_defaults_to_empty_dict(self):
        """details=None deve ser convertido para {} no AuditLog."""
        mock_db = self._make_mock_db()
        logger = AuditLogger(db=mock_db)

        mock_audit_log_cls = MagicMock()
        mock_audit_log_cls.return_value = MagicMock()
        sys.modules["models"].AuditLog = mock_audit_log_cls

        logger.log(action="user.login", details=None)
        call_kwargs = mock_audit_log_cls.call_args[1]
        assert call_kwargs["details"] == {}


# ─── 3. log() sem DB (fallback) ──────────────────────────────────────────────

class TestLogWithoutDb:
    def test_log_without_db_returns_true(self):
        """log() sem DB usa fallback de log e retorna True."""
        logger = AuditLogger(db=None)
        result = logger.log(action="user.login", user_id=1)
        assert result is True

    def test_log_without_db_writes_to_logger(self, caplog):
        """log() sem DB escreve no logger Python."""
        logger = AuditLogger(db=None)
        with caplog.at_level(logging.INFO, logger="audit_log.logger"):
            logger.log(action="sensor.pause", resource_type="sensor", resource_id=5)
        assert "sensor.pause" in caplog.text

    def test_log_without_db_no_exception(self):
        """log() sem DB nunca lança exceção."""
        logger = AuditLogger(db=None)
        # Deve funcionar sem qualquer argumento opcional
        logger.log(action="system.reset")


# ─── 4. log_ai_action() ──────────────────────────────────────────────────────

class TestLogAiAction:
    def test_log_ai_action_sets_resource_type_ai_agent(self):
        """log_ai_action() define resource_type='ai_agent'."""
        mock_db = MagicMock()
        logger = AuditLogger(db=mock_db)

        mock_audit_log_cls = MagicMock()
        mock_audit_log_cls.return_value = MagicMock()
        sys.modules["models"].AuditLog = mock_audit_log_cls

        logger.log_ai_action(
            action=AuditLogger.ACTION_AI_HEALING,
            details={"rule": "disk_full", "success": True},
            tenant_id=1,
        )
        call_kwargs = mock_audit_log_cls.call_args[1]
        assert call_kwargs["resource_type"] == "ai_agent"
        assert call_kwargs["user_id"] is None  # IA não tem user_id

    def test_log_ai_action_without_db(self):
        """log_ai_action() sem DB não lança exceção."""
        logger = AuditLogger(db=None)
        result = logger.log_ai_action(
            action=AuditLogger.ACTION_AI_PREDICTION,
            details={"host": "server-01", "metric": "disk"},
        )
        assert result is True


# ─── 5. get_audit_logger Factory ─────────────────────────────────────────────

class TestGetAuditLoggerFactory:
    def test_with_db_returns_new_instance(self):
        """get_audit_logger(db) retorna nova instância com DB."""
        mock_db = MagicMock()
        logger = get_audit_logger(db=mock_db)
        assert isinstance(logger, AuditLogger)
        assert logger.db is mock_db

    def test_without_db_returns_global_instance(self):
        """get_audit_logger() sem DB retorna instância global."""
        from audit_log.logger import _global_audit
        logger = get_audit_logger()
        assert logger is _global_audit

    def test_factory_returns_audit_logger_type(self):
        """Factory sempre retorna AuditLogger."""
        assert isinstance(get_audit_logger(), AuditLogger)
        assert isinstance(get_audit_logger(db=MagicMock()), AuditLogger)


# ─── 6. Testes de Contrato ───────────────────────────────────────────────────

class TestContract:
    def test_log_signature_accepts_all_optional_params(self):
        """log() aceita todos os parâmetros opcionais sem erro."""
        logger = AuditLogger(db=None)
        # Todos os parâmetros opcionais
        result = logger.log(
            action="config.change",
            resource_type="threshold",
            resource_id=10,
            details={"old": 80, "new": 90},
            user_id=1,
            tenant_id=1,
            ip_address="192.168.1.100",
        )
        assert result is True

    def test_log_minimum_required_params(self):
        """log() funciona com apenas action."""
        logger = AuditLogger(db=None)
        result = logger.log(action="user.login")
        assert result is True

    def test_audit_logger_init_without_db(self):
        """AuditLogger pode ser instanciado sem DB."""
        logger = AuditLogger()
        assert logger.db is None

    def test_audit_logger_init_with_db(self):
        """AuditLogger pode ser instanciado com DB."""
        mock_db = MagicMock()
        logger = AuditLogger(db=mock_db)
        assert logger.db is mock_db
