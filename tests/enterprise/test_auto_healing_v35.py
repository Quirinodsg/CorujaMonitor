"""
QA Enterprise — Auto-Healing Engine v3.5
Testa: confidence gate, whitelist, regras por tipo, backoff, retry limit,
cooldown, persistência (mock), evaluate completo.
"""
import sys
import types as _types
import asyncio
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone, timedelta

# Injetar mock de 'models' e 'database' para evitar import de api/config.py (Pydantic v2)
_mock_models_module = _types.ModuleType("models")
_mock_models_module.AutoHealingAction = MagicMock
if "models" not in sys.modules:
    sys.modules["models"] = _mock_models_module
if "database" not in sys.modules:
    sys.modules["database"] = _types.ModuleType("database")

from ai_agents.auto_healing_engine import (
    AutoHealingEngine,
    CONFIDENCE_THRESHOLD,
    SAFE_ACTIONS_WHITELIST,
    HEALING_RULES,
)


# ─── Helpers ────────────────────────────────────────────────────────────────

def run(coro):
    """Executa coroutine em loop síncrono."""
    return asyncio.get_event_loop().run_until_complete(coro)


def make_metric(sensor_type: str, value: float = 50.0, status: str = "ok",
                sensor_id: int = 1, server_id: int = 1,
                config: dict = None) -> dict:
    return {
        "sensor_id": sensor_id,
        "server_id": server_id,
        "sensor_type": sensor_type,
        "value": value,
        "status": status,
        "server_hostname": f"server-{server_id}",
        "config": config or {},
    }


# ─── 1. Confidence Gate ──────────────────────────────────────────────────────

class TestConfidenceGate:
    def test_below_threshold_skips(self):
        """confidence < 0.85 → skipped=True, nenhuma ação executada."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(
            make_metric("service", 100.0, "critical"),
            confidence=0.84,
        ))
        assert result["skipped"] is True
        assert "confidence" in result["reason"]

    def test_at_threshold_executes(self):
        """confidence == 0.85 → deve executar."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(
            make_metric("service", 100.0, "critical", config={"service_name": "nginx"}),
            confidence=0.85,
        ))
        assert result.get("skipped") is not True

    def test_above_threshold_executes(self):
        """confidence > 0.85 → deve executar."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(
            make_metric("disk", 95.0, "critical"),
            confidence=1.0,
        ))
        assert result.get("skipped") is not True

    def test_zero_confidence_skips(self):
        engine = AutoHealingEngine()
        result = run(engine.evaluate(make_metric("cpu", 99.0), confidence=0.0))
        assert result["skipped"] is True

    def test_confidence_threshold_value(self):
        """CONFIDENCE_THRESHOLD deve ser 0.85."""
        assert CONFIDENCE_THRESHOLD == 0.85


# ─── 2. Whitelist de Ações ───────────────────────────────────────────────────

class TestWhitelist:
    def test_whitelist_contains_expected_actions(self):
        expected = {
            "restart_service", "clear_temp_files", "clear_logs",
            "reconnect_probe", "kill_high_cpu_process",
        }
        assert expected.issubset(SAFE_ACTIONS_WHITELIST), \
            f"Ações faltando na whitelist: {expected - SAFE_ACTIONS_WHITELIST}"

    def test_action_not_in_whitelist_returns_error(self):
        """Ação fora da whitelist retorna error sem executar."""
        engine = AutoHealingEngine()
        # Injetar regra com ação não permitida
        fake_rule = {
            "id": "test_unsafe",
            "action": "rm_rf_root",  # não está na whitelist
            "description": "unsafe action",
            "max_retries": 1,
            "backoff_seconds": 0,
        }
        result = run(engine._execute_with_retry(fake_rule, make_metric("cpu", 99.0)))
        assert result["success"] is False
        assert "whitelist" in result["error"]


# ─── 3. Regras por Tipo de Sensor ────────────────────────────────────────────

class TestHealingRules:
    def test_service_down_rule_triggers(self):
        """sensor_type=service + status=critical → regra service_down ativa."""
        rule = next(r for r in HEALING_RULES if r["id"] == "service_down")
        metric = make_metric("service", 0.0, "critical")
        assert rule["condition"](metric) is True

    def test_service_down_rule_not_triggers_on_ok(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "service_down")
        metric = make_metric("service", 0.0, "ok")
        assert rule["condition"](metric) is False

    def test_high_cpu_rule_triggers_at_95(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "high_cpu")
        assert rule["condition"](make_metric("cpu", 95.0)) is True

    def test_high_cpu_rule_not_triggers_below_95(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "high_cpu")
        assert rule["condition"](make_metric("cpu", 94.9)) is False

    def test_disk_full_rule_triggers_at_90(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        assert rule["condition"](make_metric("disk", 90.0)) is True

    def test_disk_full_rule_not_triggers_below_90(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        assert rule["condition"](make_metric("disk", 89.9)) is False

    def test_host_offline_rule_triggers(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "host_offline")
        assert rule["condition"](make_metric("ping", 0.0, "critical")) is True

    def test_high_memory_rule_triggers_at_95(self):
        rule = next(r for r in HEALING_RULES if r["id"] == "high_memory")
        assert rule["condition"](make_metric("memory", 95.0)) is True

    def test_all_rules_have_required_fields(self):
        """Todas as regras devem ter os campos obrigatórios."""
        required = {"id", "condition", "action", "description", "max_retries", "backoff_seconds"}
        for rule in HEALING_RULES:
            missing = required - set(rule.keys())
            assert not missing, f"Regra {rule.get('id')} faltando campos: {missing}"


# ─── 4. Backoff Exponencial ──────────────────────────────────────────────────

class TestBackoffRetry:
    def test_cooldown_active_after_first_attempt(self):
        """Após primeira tentativa, cooldown ativo impede segunda imediata."""
        engine = AutoHealingEngine()
        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        metric = make_metric("disk", 95.0, "critical", sensor_id=99)

        # Primeira execução
        result1 = run(engine._execute_with_retry(rule, metric))
        # Segunda execução imediata — deve estar em cooldown
        result2 = run(engine._execute_with_retry(rule, metric))

        assert "cooldown_active" in result2.get("error", ""), \
            f"Segunda tentativa deveria estar em cooldown, obtido: {result2}"

    def test_max_retries_exceeded(self):
        """Após max_retries tentativas, retorna max_retries_exceeded."""
        engine = AutoHealingEngine()
        rule = {
            "id": "test_retry",
            "action": "clear_temp_files",
            "description": "test",
            "max_retries": 0,  # zero retries
            "backoff_seconds": 0,
        }
        metric = make_metric("disk", 95.0, sensor_id=42)
        # Forçar estado com attempts já no limite
        engine._retry_state["42:test_retry"] = {
            "attempts": 0,  # já no limite (max_retries=0)
            "last_attempt": None,
        }
        result = run(engine._execute_with_retry(rule, metric))
        assert result["error"] == "max_retries_exceeded"

    def test_backoff_doubles_with_attempts(self):
        """Backoff exponencial: backoff_seconds * 2^attempts."""
        engine = AutoHealingEngine()
        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        metric = make_metric("disk", 95.0, sensor_id=77)

        # Simular 2 tentativas anteriores
        engine._retry_state["77:disk_full"] = {
            "attempts": 2,
            "last_attempt": datetime.now(timezone.utc),  # agora = cooldown ativo
        }
        result = run(engine._execute_with_retry(rule, metric))
        # backoff = 120 * 2^2 = 480s — deve estar em cooldown
        assert "cooldown_active" in result.get("error", ""), \
            "Backoff exponencial deve estar ativo"


# ─── 5. evaluate() — Integração ──────────────────────────────────────────────

class TestEvaluateIntegration:
    def test_evaluate_returns_actions_list(self):
        """evaluate() retorna dict com 'actions' e 'evaluated_at'."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(make_metric("disk", 95.0), confidence=1.0))
        assert "actions" in result
        assert "evaluated_at" in result
        assert isinstance(result["actions"], list)

    def test_evaluate_disk_full_triggers_action(self):
        """Disco >= 90% com confidence >= 0.85 → ação clear_temp_files."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(make_metric("disk", 92.0), confidence=1.0))
        actions = result["actions"]
        action_names = [a.get("action") for a in actions]
        assert "clear_temp_files" in action_names, \
            f"clear_temp_files esperado, obtido: {action_names}"

    def test_evaluate_ok_sensor_no_actions(self):
        """Sensor OK não deve disparar nenhuma ação."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(make_metric("cpu", 30.0, "ok"), confidence=1.0))
        assert len(result["actions"]) == 0, \
            "Sensor OK não deve gerar ações de healing"

    def test_evaluate_multiple_rules_can_trigger(self):
        """Métrica que satisfaz múltiplas regras dispara múltiplas ações."""
        engine = AutoHealingEngine()
        # cpu >= 95 E memory >= 95 em métricas separadas
        result_cpu = run(engine.evaluate(make_metric("cpu", 99.0), confidence=1.0))
        result_mem = run(engine.evaluate(make_metric("memory", 99.0, sensor_id=2), confidence=1.0))
        assert len(result_cpu["actions"]) >= 1
        assert len(result_mem["actions"]) >= 1

    def test_evaluate_result_has_success_field(self):
        """Cada ação no resultado deve ter campo 'success'."""
        engine = AutoHealingEngine()
        result = run(engine.evaluate(make_metric("disk", 95.0), confidence=1.0))
        for action in result["actions"]:
            assert "success" in action, f"Ação sem campo 'success': {action}"


# ─── 6. Persistência (mock) ──────────────────────────────────────────────────

class TestPersistence:
    def test_persist_action_called_with_db(self):
        """_persist_action() chama db.add() e db.commit() quando db disponível."""
        mock_db = MagicMock()
        engine = AutoHealingEngine(db=mock_db)

        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        metric = make_metric("disk", 95.0)
        result = {"action": "clear_temp_files", "success": True, "error": None, "duration_ms": 10}

        mock_action_cls = MagicMock(return_value=MagicMock())
        sys.modules["models"].AutoHealingAction = mock_action_cls
        engine._persist_action(rule, metric, result)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_persist_action_no_db_no_crash(self):
        """_persist_action() sem db não lança exceção."""
        engine = AutoHealingEngine(db=None)
        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        metric = make_metric("disk", 95.0)
        result = {"action": "clear_temp_files", "success": True, "error": None, "duration_ms": 10}
        engine._persist_action(rule, metric, result)  # não deve lançar

    def test_persist_action_rollback_on_error(self):
        """_persist_action() faz rollback se db.commit() lança exceção."""
        mock_db = MagicMock()
        mock_db.commit.side_effect = Exception("DB error")
        engine = AutoHealingEngine(db=mock_db)

        rule = next(r for r in HEALING_RULES if r["id"] == "disk_full")
        metric = make_metric("disk", 95.0)
        result = {"action": "clear_temp_files", "success": True, "error": None, "duration_ms": 10}

        sys.modules["models"].AutoHealingAction = MagicMock(return_value=MagicMock())
        engine._persist_action(rule, metric, result)
        mock_db.rollback.assert_called_once()
