"""
Pipeline Orchestrator — Coruja Monitor v3.0

Orquestra o pipeline completo end-to-end:
  métricas/eventos → AnomalyDetection → Correlation → RootCause → Decision → AutoRemediation

Responsabilidades:
  1. Receber métricas brutas ou eventos já processados
  2. Executar pipeline sequencial via AgentPipeline
  3. Persistir log de cada agente em ai_agent_logs
  4. Persistir alertas inteligentes em intelligent_alerts
  5. Persistir ações de remediação em ai_feedback_actions
"""
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import text

from ai_agents.base_agent import AgentContext
from ai_agents.pipeline import AgentPipeline
from ai_agents.anomaly_detection import AnomalyDetectionAgent
from ai_agents.correlation import CorrelationAgent
from ai_agents.root_cause import RootCauseAgent
from ai_agents.decision import DecisionAgent
from ai_agents.auto_remediation import AutoRemediationAgent
from core.spec.models import Metric, Event
from core.spec.enums import EventSeverity, SensorStatus

logger = logging.getLogger(__name__)


def _safe_json(obj):
    """Serializa objeto para dict JSON-safe."""
    try:
        if obj is None:
            return None
        if isinstance(obj, (bool, int, float, str)):
            return obj
        if hasattr(obj, "model_dump"):  # Pydantic v2
            return _safe_json(obj.model_dump())
        if hasattr(obj, "dict"):  # Pydantic v1
            return _safe_json(obj.dict())
        if hasattr(obj, "__dict__"):
            return {k: _safe_json(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
        if isinstance(obj, (list, tuple)):
            return [_safe_json(i) for i in obj]
        if isinstance(obj, dict):
            return {str(k): _safe_json(v) for k, v in obj.items()}
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "value"):  # Enum
            return obj.value
        return str(obj)
    except Exception:
        return str(obj)


class PipelineOrchestrator:
    """
    Orquestra o pipeline de agentes v3 end-to-end.

    Uso:
        orch = PipelineOrchestrator(db_conn=conn)
        orch.run_from_metrics(metrics, sensors)
        orch.run_from_events(events)
    """

    def __init__(self, db_conn=None, topology=None, feedback_history=None):
        self._db = db_conn
        self._topology = topology
        self._feedback_history = feedback_history or []

        # Instanciar agentes
        self._pipeline = AgentPipeline([
            AnomalyDetectionAgent(),
            CorrelationAgent(),
            RootCauseAgent(),
            DecisionAgent(),
            AutoRemediationAgent(),
        ])

    # ─── Entry points ────────────────────────────────────────────────────────

    def run_from_metrics(self, metrics: list[Metric], sensors: dict = None) -> dict:
        """
        Ponto de entrada: lista de Metric.
        Converte métricas em eventos via threshold simples antes de rodar o pipeline.
        sensors: {sensor_id: Sensor} para thresholds
        """
        events = self._metrics_to_events(metrics, sensors or {})
        return self.run_from_events(events, metrics=metrics)

    def run_from_events(self, events: list[Event], metrics: list[Metric] = None) -> dict:
        """
        Ponto de entrada: lista de Event já processados.
        """
        run_id = str(uuid4())
        logger.info("PipelineOrchestrator: run_id=%s events=%d", run_id, len(events))

        context = AgentContext(
            events=events,
            metrics=metrics or [],
            topology=self._topology,
            feedback_history=self._feedback_history,
            pipeline_data={"run_id": run_id},
        )

        results = self._pipeline.run(context)

        # Persistir logs de cada agente
        for result in results:
            self._log_agent(run_id, result)

        # Persistir alerta inteligente se DecisionAgent aprovou
        alert_id = None
        should_alert = context.pipeline_data.get("should_alert", False)
        if should_alert:
            alert_id = self._persist_intelligent_alert(run_id, context, results)

        # Persistir ações de remediação
        for result in results:
            if "AutoRemediation" in result.agent_name and result.success:
                actions = result.output.get("actions_executed", [])
                for action in actions:
                    self._persist_feedback_action(run_id, action)

        summary = {
            "run_id": run_id,
            "events_processed": len(events),
            "agents_run": len(results),
            "agents_success": sum(1 for r in results if r.success),
            "should_alert": should_alert,
            "alert_id": alert_id,
            "results": [
                {
                    "agent": r.agent_name,
                    "success": r.success,
                    "output_keys": list(r.output.keys()) if r.output else [],
                    "error": r.error,
                }
                for r in results
            ],
        }
        logger.info("PipelineOrchestrator: run_id=%s concluído — alert=%s", run_id, should_alert)
        return summary

    # ─── Conversão métricas → eventos ────────────────────────────────────────

    def _metrics_to_events(self, metrics: list[Metric], sensors: dict) -> list[Event]:
        """
        Converte métricas em eventos usando thresholds dos sensores.
        Gera evento para qualquer métrica com status warning ou critical.
        """
        events = []
        for metric in metrics:
            sensor = sensors.get(str(metric.sensor_id))
            thresholds = sensor.thresholds if sensor else {}
            sensor_type = sensor.type if sensor else "unknown"

            # Determinar status
            status = self._evaluate_status(metric.value, thresholds)
            if status in (SensorStatus.WARNING, SensorStatus.CRITICAL):
                severity = (
                    EventSeverity.CRITICAL
                    if status == SensorStatus.CRITICAL
                    else EventSeverity.WARNING
                )
                event = Event(
                    host_id=metric.host_id,
                    type=f"high_{sensor_type}" if sensor_type != "unknown" else "threshold_breach",
                    severity=severity,
                    timestamp=metric.timestamp,
                    source_metric_id=metric.sensor_id,
                    description=(
                        f"{sensor_type} = {metric.value}{metric.unit} "
                        f"(status: {status.value})"
                    ),
                )
                events.append(event)
        return events

    def _evaluate_status(self, value: float, thresholds: dict) -> SensorStatus:
        if not thresholds:
            return SensorStatus.OK
        critical = thresholds.get("critical")
        warning = thresholds.get("warning")
        lower = thresholds.get("lower", False)
        if lower:
            if critical is not None and value <= critical:
                return SensorStatus.CRITICAL
            if warning is not None and value <= warning:
                return SensorStatus.WARNING
        else:
            if critical is not None and value >= critical:
                return SensorStatus.CRITICAL
            if warning is not None and value >= warning:
                return SensorStatus.WARNING
        return SensorStatus.OK

    # ─── Persistência ────────────────────────────────────────────────────────

    def _log_agent(self, run_id: str, result) -> None:
        """Persiste execução do agente em ai_agent_logs."""
        if self._db is None:
            return
        try:
            # Sanitizar output — remover objetos não-serializáveis (ex: Event Pydantic)
            output = _safe_json(result.output) if result.output else {}
            # Garantir que é serializável
            output_str = json.dumps(output)

            self._db.execute(
                text("""
                INSERT INTO ai_agent_logs
                    (run_id, agent_name, input, output, status, error, timestamp)
                VALUES
                    (:run_id, :agent_name, CAST(:input AS jsonb), CAST(:output AS jsonb), :status, :error, NOW())
                """),
                {
                    "run_id": run_id,
                    "agent_name": result.agent_name,
                    "input": "{}",
                    "output": output_str,
                    "status": "success" if result.success else "error",
                    "error": result.error,
                },
            )
            self._db.commit()
        except Exception as e:
            logger.error("PipelineOrchestrator: falha ao logar agente %s: %s", result.agent_name, e)
            try:
                self._db.rollback()
            except Exception:
                pass

    def _persist_intelligent_alert(self, run_id: str, context: AgentContext, results) -> Optional[str]:
        """Persiste alerta inteligente em intelligent_alerts."""
        if self._db is None:
            return None
        try:
            rc_results = context.pipeline_data.get("root_cause_results", [])
            root_cause_text = None
            confidence = context.pipeline_data.get("decision_confidence", 0.5)
            affected_hosts = []

            if rc_results:
                rc = rc_results[0]
                root_cause_text = rc.get("reasoning") or rc.get("root_node_id")
                confidence = rc.get("confidence", confidence)
                affected_hosts = rc.get("affected_nodes", [])

            # Determinar severidade máxima dos eventos
            severity = "warning"
            for event in context.events:
                sev = event.severity if isinstance(event.severity, str) else event.severity.value
                if sev == "critical":
                    severity = "critical"
                    break

            event_count = len(context.events)
            title = f"Pipeline v3: {event_count} evento(s) correlacionado(s)"
            if root_cause_text:
                # Usar a descrição do evento mais recente como título se disponível
                if context.events:
                    sorted_ev = sorted(context.events, key=lambda e: e.timestamp, reverse=True)
                    ev_desc = getattr(sorted_ev[0], 'description', None)
                    if ev_desc:
                        title = ev_desc[:120]
                    else:
                        title = f"Causa raiz: {root_cause_text[:80]}"
                else:
                    title = f"Causa raiz: {root_cause_text[:80]}"

            row = self._db.execute(
                text("""
                INSERT INTO intelligent_alerts
                    (title, severity, status, root_cause, affected_hosts, confidence, event_ids)
                VALUES
                    (:title, :severity, 'open', :root_cause,
                     CAST(:affected_hosts AS uuid[]), :confidence, CAST(:event_ids AS uuid[]))
                RETURNING id
                """),
                {
                    "title": title,
                    "severity": severity,
                    "root_cause": root_cause_text or f"run_id={run_id}",
                    "affected_hosts": "{}",
                    "confidence": confidence,
                    "event_ids": "{}",
                },
            ).fetchone()
            self._db.commit()
            alert_id = str(row.id) if row else None
            logger.info("PipelineOrchestrator: alerta inteligente criado %s", alert_id)
            return alert_id
        except Exception as e:
            logger.error("PipelineOrchestrator: falha ao persistir alerta: %s", e)
            try:
                self._db.rollback()
            except Exception:
                pass
            return None

    def _persist_feedback_action(self, run_id: str, action: dict) -> None:
        """Persiste ação de remediação em ai_feedback_actions."""
        if self._db is None:
            return
        try:
            self._db.execute(
                text("""
                INSERT INTO ai_feedback_actions
                    (agent_name, action_type, target_host, timestamp, result, outcome, metadata)
                VALUES
                    (:agent_name, :action_type, :target_host, NOW(), :result, 'pending', CAST(:meta AS jsonb))
                """),
                {
                    "agent_name": "AutoRemediationAgent",
                    "action_type": action.get("action", "unknown"),
                    "target_host": action.get("host_id", "unknown"),
                    "result": action.get("result", "pending"),
                    "meta": json.dumps({"run_id": run_id, **action}),
                },
            )
            self._db.commit()
        except Exception as e:
            logger.error("PipelineOrchestrator: falha ao persistir ação: %s", e)
            try:
                self._db.rollback()
            except Exception:
                pass
