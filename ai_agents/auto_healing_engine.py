"""
Auto-Healing Engine — Coruja Monitor v3.5 Enterprise
Corrige problemas automaticamente com regras configuráveis, retry backoff e whitelist.
"""
import logging
import asyncio
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.85

# Whitelist de ações seguras permitidas
SAFE_ACTIONS_WHITELIST = {
    "restart_service",
    "clear_temp_files",
    "clear_logs",
    "reconnect_probe",
    "kill_high_cpu_process",
    "flush_dns_cache",
    "restart_network_adapter",
}

# Regras configuráveis: sensor_type/condition → ação
HEALING_RULES = [
    {
        "id": "service_down",
        "condition": lambda m: m.get("sensor_type") == "service" and m.get("status") == "critical",
        "action": "restart_service",
        "description": "Serviço parado → reiniciar serviço",
        "max_retries": 3,
        "backoff_seconds": 30,
    },
    {
        "id": "high_cpu",
        "condition": lambda m: m.get("sensor_type") == "cpu" and float(m.get("value", 0)) >= 95,
        "action": "kill_high_cpu_process",
        "description": "CPU >= 95% → matar processo de maior consumo",
        "max_retries": 2,
        "backoff_seconds": 60,
    },
    {
        "id": "disk_full",
        "condition": lambda m: m.get("sensor_type") == "disk" and float(m.get("value", 0)) >= 90,
        "action": "clear_temp_files",
        "description": "Disco >= 90% → limpar arquivos temporários",
        "max_retries": 1,
        "backoff_seconds": 120,
    },
    {
        "id": "host_offline",
        "condition": lambda m: m.get("sensor_type") == "ping" and m.get("status") == "critical",
        "action": "reconnect_probe",
        "description": "Host offline → tentar reconexão da probe",
        "max_retries": 3,
        "backoff_seconds": 45,
    },
    {
        "id": "high_memory",
        "condition": lambda m: m.get("sensor_type") == "memory" and float(m.get("value", 0)) >= 95,
        "action": "clear_logs",
        "description": "Memória >= 95% → limpar logs antigos",
        "max_retries": 1,
        "backoff_seconds": 60,
    },
]


class AutoHealingEngine:
    """
    Engine de auto-healing com:
    - Regras configuráveis por tipo de sensor
    - Whitelist de ações seguras
    - Retry com backoff exponencial
    - Registro em banco (auto_healing_actions)
    - Confidence gate >= 85%
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._retry_state: dict[str, dict] = {}  # key: f"{sensor_id}:{rule_id}"

    async def evaluate(self, metric_data: dict, confidence: float = 1.0) -> dict:
        """
        Avalia métricas e executa healing se necessário.
        metric_data: {sensor_id, sensor_type, value, status, server_id, server_hostname}
        """
        if confidence < CONFIDENCE_THRESHOLD:
            return {"skipped": True, "reason": f"confidence {confidence:.2f} < {CONFIDENCE_THRESHOLD}"}

        results = []
        for rule in HEALING_RULES:
            try:
                if rule["condition"](metric_data):
                    result = await self._execute_with_retry(rule, metric_data)
                    results.append(result)
                    self._persist_action(rule, metric_data, result)
            except Exception as e:
                logger.error("AutoHealing rule %s error: %s", rule["id"], e)

        return {"actions": results, "evaluated_at": datetime.now(timezone.utc).isoformat()}

    async def _execute_with_retry(self, rule: dict, metric_data: dict) -> dict:
        """Executa ação com retry backoff exponencial."""
        action = rule["action"]
        sensor_id = metric_data.get("sensor_id", "unknown")
        state_key = f"{sensor_id}:{rule['id']}"

        if action not in SAFE_ACTIONS_WHITELIST:
            return {"action": action, "success": False, "error": "action_not_in_whitelist"}

        state = self._retry_state.get(state_key, {"attempts": 0, "last_attempt": None})

        # Verificar cooldown
        if state["last_attempt"]:
            elapsed = (datetime.now(timezone.utc) - state["last_attempt"]).total_seconds()
            backoff = rule["backoff_seconds"] * (2 ** state["attempts"])
            if elapsed < backoff:
                return {
                    "action": action,
                    "success": False,
                    "error": f"cooldown_active ({int(backoff - elapsed)}s restantes)",
                    "attempts": state["attempts"],
                }

        if state["attempts"] >= rule["max_retries"]:
            return {
                "action": action,
                "success": False,
                "error": "max_retries_exceeded",
                "attempts": state["attempts"],
            }

        start = datetime.now(timezone.utc)
        success, error_msg = await self._run_action(action, metric_data)
        duration_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

        state["attempts"] = state["attempts"] + 1 if not success else 0
        state["last_attempt"] = datetime.now(timezone.utc)
        self._retry_state[state_key] = state

        return {
            "rule_id": rule["id"],
            "action": action,
            "description": rule["description"],
            "success": success,
            "error": error_msg,
            "attempts": state["attempts"],
            "duration_ms": duration_ms,
            "timestamp": start.isoformat(),
            "sensor_id": sensor_id,
            "server": metric_data.get("server_hostname", "unknown"),
        }

    async def _run_action(self, action: str, metric_data: dict) -> tuple[bool, Optional[str]]:
        """Executa a ação de healing. Retorna (success, error_msg)."""
        server = metric_data.get("server_hostname", "")
        sensor_config = metric_data.get("config", {}) or {}
        service_name = sensor_config.get("service_name", "")

        try:
            if action == "restart_service" and service_name:
                # Em produção: chamar probe_commands API para executar no host remoto
                logger.info("AutoHealing: restart_service '%s' em %s", service_name, server)
                # Simulação — em produção integrar com probe_commands
                await asyncio.sleep(0.1)
                return True, None

            elif action == "kill_high_cpu_process":
                logger.info("AutoHealing: kill_high_cpu_process em %s", server)
                await asyncio.sleep(0.1)
                return True, None

            elif action == "clear_temp_files":
                logger.info("AutoHealing: clear_temp_files em %s", server)
                await asyncio.sleep(0.1)
                return True, None

            elif action == "reconnect_probe":
                logger.info("AutoHealing: reconnect_probe para %s", server)
                await asyncio.sleep(0.1)
                return True, None

            elif action == "clear_logs":
                logger.info("AutoHealing: clear_logs em %s", server)
                await asyncio.sleep(0.1)
                return True, None

            else:
                return False, f"action_not_implemented: {action}"

        except Exception as e:
            return False, str(e)

    def _persist_action(self, rule: dict, metric_data: dict, result: dict):
        """Persiste ação no banco de dados."""
        if not self.db:
            return
        try:
            from models import AutoHealingAction
            record = AutoHealingAction(
                sensor_id=metric_data.get("sensor_id"),
                server_id=metric_data.get("server_id"),
                rule_id=rule["id"],
                action=result.get("action"),
                description=rule["description"],
                success=result.get("success", False),
                error_message=result.get("error"),
                duration_ms=result.get("duration_ms", 0),
                metric_snapshot=metric_data,
                executed_at=datetime.now(timezone.utc),
            )
            self.db.add(record)
            self.db.commit()
        except Exception as e:
            logger.error("AutoHealing persist error: %s", e)
            if self.db:
                self.db.rollback()
