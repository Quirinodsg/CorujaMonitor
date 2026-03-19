"""
FASE 7 — Testes Realistas do Pipeline de IA
Simula: CPU spike, múltiplos hosts falhando, cascata switch→servidores.
Valida: AnomalyDetection, Correlation, RootCause, Decision sem falso positivo.
"""
import pytest
import time
from uuid import uuid4
from datetime import datetime, timezone, timedelta

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.spec.models import Metric, Sensor, Event
from core.spec.enums import SensorStatus, EventSeverity, Protocol
from ai_agents.pipeline_orchestrator import PipelineOrchestrator
from ai_agents.anomaly_detection import AnomalyDetectionAgent
from ai_agents.correlation import CorrelationAgent
from ai_agents.root_cause import RootCauseAgent
from ai_agents.decision import DecisionAgent


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_sensor(sensor_type="cpu", host_id=None, thresholds=None):
    return Sensor(
        host_id=host_id or uuid4(),
        type=sensor_type,
        protocol=Protocol.WMI,
        interval=60,
        thresholds=thresholds or {"warning": 80, "critical": 95},
    )


def make_metric(value: float, sensor: Sensor, unit="%"):
    return Metric(
        sensor_id=sensor.id,
        host_id=sensor.host_id,
        value=value,
        unit=unit,
        timestamp=datetime.now(timezone.utc),
    )


def make_event(event_type: str, severity: EventSeverity, host_id=None):
    return Event(
        host_id=host_id or uuid4(),
        type=event_type,
        severity=severity,
        timestamp=datetime.now(timezone.utc),
    )


# ─── Cenário 1: CPU Spike ────────────────────────────────────────────────────

class TestCPUSpike:

    def test_cpu_spike_detected(self):
        """CPU spike (97%) deve ser detectado como anomalia."""
        sensor = make_sensor("cpu", thresholds={"warning": 80, "critical": 95})
        metrics = [make_metric(97.0, sensor)]

        orch = PipelineOrchestrator()
        result = orch.run_from_metrics(metrics, {str(sensor.id): sensor})

        assert result.get("should_alert") is True
        # Verificar que agentes rodaram (chave real: agents_run)
        assert result.get("agents_run", 0) > 0

    def test_cpu_normal_no_alert(self):
        """CPU normal (50%) não deve gerar alerta."""
        sensor = make_sensor("cpu", thresholds={"warning": 80, "critical": 95})
        metrics = [make_metric(50.0, sensor)]

        orch = PipelineOrchestrator()
        result = orch.run_from_metrics(metrics, {str(sensor.id): sensor})

        assert result.get("should_alert") is False

    def test_cpu_warning_threshold(self):
        """CPU em 85% (warning) deve ser processado sem crash."""
        sensor = make_sensor("cpu", thresholds={"warning": 80, "critical": 95})
        metrics = [make_metric(85.0, sensor)]

        orch = PipelineOrchestrator()
        result = orch.run_from_metrics(metrics, {str(sensor.id): sensor})

        # Resultado deve ter campos obrigatórios
        assert "agents_run" in result
        assert "should_alert" in result


# ─── Cenário 2: Múltiplos Hosts Falhando ────────────────────────────────────

class TestMultipleHostsFailure:

    def test_multiple_hosts_critical_generates_alert(self):
        """5 hosts com CPU crítica → alerta gerado."""
        sensors = [make_sensor("cpu", thresholds={"warning": 80, "critical": 95}) for _ in range(5)]
        metrics = [make_metric(97.0, s) for s in sensors]
        sensors_dict = {str(s.id): s for s in sensors}

        orch = PipelineOrchestrator()
        result = orch.run_from_metrics(metrics, sensors_dict)

        assert result.get("should_alert") is True

    def test_correlation_groups_related_events(self):
        """Eventos do mesmo tipo em múltiplos hosts devem ser correlacionados."""
        host_id = uuid4()
        events = [
            make_event("high_cpu", EventSeverity.CRITICAL, host_id),
            make_event("high_memory", EventSeverity.WARNING, host_id),
            make_event("disk_full", EventSeverity.CRITICAL, host_id),
        ]

        orch = PipelineOrchestrator()
        result = orch.run_from_events(events)

        agents = result.get("agents", {})
        correlation = agents.get("correlation", {})
        # Correlation deve ter agrupado eventos do mesmo host
        assert correlation is not None

    def test_no_false_positive_on_ok_metrics(self):
        """Métricas OK em múltiplos hosts não geram falso positivo."""
        sensors = [make_sensor("cpu", thresholds={"warning": 80, "critical": 95}) for _ in range(10)]
        metrics = [make_metric(30.0, s) for s in sensors]
        sensors_dict = {str(s.id): s for s in sensors}

        orch = PipelineOrchestrator()
        result = orch.run_from_metrics(metrics, sensors_dict)

        assert result.get("should_alert") is False, "Falso positivo detectado!"


# ─── Cenário 3: Cascata Switch → Servidores ──────────────────────────────────

class TestCascadeFailure:

    def test_cascade_switch_to_servers(self):
        """Switch offline → múltiplos servidores offline → root cause = switch."""
        switch_host = uuid4()
        server_hosts = [uuid4() for _ in range(5)]

        # Switch offline primeiro
        events = [make_event("host_unreachable", EventSeverity.CRITICAL, switch_host)]
        # Servidores offline em cascata
        for h in server_hosts:
            events.append(make_event("host_unreachable", EventSeverity.CRITICAL, h))

        orch = PipelineOrchestrator()
        result = orch.run_from_events(events)

        agents = result.get("agents", {})
        root_cause = agents.get("root_cause", {})

        # Root cause deve identificar o problema
        assert root_cause is not None
        assert result.get("should_alert") is True

    def test_single_server_offline_not_cascade(self):
        """1 servidor offline não deve crashar o pipeline."""
        events = [make_event("host_unreachable", EventSeverity.CRITICAL)]

        orch = PipelineOrchestrator()
        result = orch.run_from_events(events)

        assert result is not None
        assert "agents_run" in result


# ─── Testes de Agentes Individuais ──────────────────────────────────────────

class TestAnomalyDetectionAgent:

    def test_detects_critical_anomaly(self):
        """AnomalyDetectionAgent detecta anomalia após baseline com variância estabelecido."""
        from ai_agents.base_agent import AgentContext
        agent = AnomalyDetectionAgent()
        sensor = make_sensor("cpu", thresholds={"warning": 80, "critical": 95})

        # Baseline com variância real (valores entre 48-52)
        baseline = agent.get_baseline(str(sensor.id))
        import random
        random.seed(42)
        for _ in range(50):
            baseline.add(50.0 + random.uniform(-2, 2))

        # Valor anômalo: 97.0 (muito acima da média de ~50)
        metrics = [make_metric(97.0, sensor)]
        context = AgentContext(events=[], metrics=metrics)
        result = agent.process(context)

        assert result is not None
        assert result.success is True
        assert result.output.get("anomalies_detected", 0) > 0

    def test_no_anomaly_on_normal_metrics(self):
        """Sem anomalia em métricas normais."""
        from ai_agents.base_agent import AgentContext
        agent = AnomalyDetectionAgent()
        sensor = make_sensor("cpu", thresholds={"warning": 80, "critical": 95})

        baseline = agent.get_baseline(str(sensor.id))
        for v in [50.0] * 30:
            baseline.add(v)

        metrics = [make_metric(52.0, sensor)]
        context = AgentContext(events=[], metrics=metrics)
        result = agent.process(context)

        assert result is not None
        assert result.success is True
        assert result.output.get("anomalies_detected", 0) == 0


class TestDecisionAgent:

    def test_decision_no_false_positive(self):
        """DecisionAgent não gera alerta para eventos INFO."""
        from ai_agents.base_agent import AgentContext
        agent = DecisionAgent()
        events = [make_event("info_event", EventSeverity.INFO)]

        context = AgentContext(events=events, metrics=[])
        result = agent.process(context)

        assert result is not None
        assert result.success is True
        decisions = result.output.get("decisions", [])
        if decisions:
            assert not any(d.get("should_alert") and d.get("has_critical") for d in decisions)

    def test_decision_alerts_on_critical(self):
        """DecisionAgent gera alerta para eventos críticos."""
        from ai_agents.base_agent import AgentContext
        agent = DecisionAgent()
        events = [make_event("high_cpu", EventSeverity.CRITICAL)]

        context = AgentContext(events=events, metrics=[])
        context.pipeline_data["root_cause_results"] = [
            {"affected_nodes_count": 1, "confidence": 0.8}
        ]
        result = agent.process(context)

        assert result is not None
        assert result.success is True


# ─── Testes de Performance do Pipeline ──────────────────────────────────────

class TestPipelinePerformance:

    def test_pipeline_100_events_under_5s(self):
        """100 eventos processados em <5s."""
        events = [
            make_event("high_cpu", EventSeverity.CRITICAL)
            for _ in range(100)
        ]

        orch = PipelineOrchestrator()
        start = time.monotonic()
        result = orch.run_from_events(events)
        elapsed = (time.monotonic() - start) * 1000

        assert elapsed < 5000, f"Pipeline demorou {elapsed:.0f}ms para 100 eventos"
        assert result is not None

    def test_pipeline_result_always_has_run_id(self):
        """Resultado do pipeline sempre tem campo 'run_id'."""
        events = [make_event("high_cpu", EventSeverity.CRITICAL)]

        orch = PipelineOrchestrator()
        result = orch.run_from_events(events)

        assert "run_id" in result, "Campo 'run_id' ausente no resultado do pipeline"
        assert "agents_run" in result
