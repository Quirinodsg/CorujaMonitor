"""
Testes das Fases 5-7 — AI Agents
Cobre: Property 8 (anomalia > 3σ), Property 9 (pipeline resiliente),
       Property 10 (remediação >= 85%), Property 11 (feedback outcome),
       Property 12 (root cause confiança >= 0.8)
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from core.spec.models import Event, Metric, TopologyNode
from core.spec.enums import EventSeverity, NodeType, Protocol
from ai_agents.base_agent import AgentContext, AgentResult, BaseAgent
from ai_agents.anomaly_detection import AnomalyDetectionAgent, SensorBaseline
from ai_agents.smart_scheduler import SmartSchedulerAgent
from ai_agents.correlation import CorrelationAgent
from ai_agents.root_cause import RootCauseAgent, RootCauseEngine
from ai_agents.decision import DecisionAgent
from ai_agents.auto_remediation import AutoRemediationAgent
from ai_agents.pipeline import AgentPipeline
from ai_agents.feedback_loop import FeedbackLoop, RemediationAction, ActionResult
from topology_engine.graph import TopologyGraph


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_event(event_type="high_cpu", severity=EventSeverity.CRITICAL, host_id=None):
    return Event(
        host_id=host_id or uuid4(),
        type=event_type,
        severity=severity,
        timestamp=datetime.now(timezone.utc),
    )


def make_metric(value: float, sensor_id=None, host_id=None):
    return Metric(
        sensor_id=sensor_id or uuid4(),
        host_id=host_id or uuid4(),
        value=value,
        unit="%",
        timestamp=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Property 8: Anomalia detectada quando valor desvia > 3σ
# ---------------------------------------------------------------------------

class TestAnomalyDetection:
    def test_baseline_builds_correctly(self):
        baseline = SensorBaseline(window=100)
        for v in range(50, 60):
            baseline.add(float(v))
        assert baseline.mean() is not None
        assert baseline.std() is not None

    def test_normal_value_not_anomaly(self):
        """Valor dentro de 3σ não é anomalia."""
        baseline = SensorBaseline(window=100)
        # Baseline com variância real: média≈50, std≈2
        import random; random.seed(42)
        for _ in range(50):
            baseline.add(50.0 + random.gauss(0, 2))
        # Valor dentro de 1σ — não é anomalia
        is_anom, confidence = baseline.is_anomaly(51.0)
        assert is_anom is False

    def test_anomaly_detected_above_3sigma(self):
        """Property 8: valor > 3σ deve ser detectado como anomalia."""
        baseline = SensorBaseline(window=100)
        # Baseline com variância real: média≈50, std≈2
        import random; random.seed(42)
        for _ in range(50):
            baseline.add(50.0 + random.gauss(0, 2))
        # Valor muito distante (> 3σ): 50 + 4*2 = 58 → z≈4
        is_anom, confidence = baseline.is_anomaly(200.0)
        assert is_anom is True
        assert confidence > 0.0

    def test_anomaly_confidence_positive(self):
        baseline = SensorBaseline(window=100)
        for v in [10.0] * 30 + [11.0] * 20:
            baseline.add(v)
        is_anom, confidence = baseline.is_anomaly(100.0)
        assert is_anom is True
        assert 0.0 < confidence <= 1.0

    def test_insufficient_samples_no_anomaly(self):
        """Com menos de 2 amostras, não há baseline suficiente."""
        baseline = SensorBaseline()
        baseline.add(50.0)
        is_anom, confidence = baseline.is_anomaly(200.0)
        assert is_anom is False

    def test_agent_generates_anomaly_event(self):
        """AnomalyDetectionAgent gera Event(type='anomaly') para valor > 3σ."""
        agent = AnomalyDetectionAgent()
        sensor_id = uuid4()
        host_id = uuid4()

        # Construir baseline com variância real
        import random; random.seed(42)
        baseline = agent.get_baseline(str(sensor_id))
        for _ in range(50):
            baseline.add(50.0 + random.gauss(0, 2))

        # Métrica anômala (muito acima de 3σ)
        metric = make_metric(500.0, sensor_id=sensor_id, host_id=host_id)
        context = AgentContext(metrics=[metric])
        result = agent.process(context)

        assert result.success is True
        assert result.output["anomalies_detected"] >= 1
        anomaly = result.output["anomaly_events"][0]
        assert anomaly["event"].type == "anomaly"
        assert anomaly["confidence"] > 0.0

    def test_agent_no_anomaly_for_normal_value(self):
        agent = AnomalyDetectionAgent()
        sensor_id = uuid4()
        import random; random.seed(42)
        baseline = agent.get_baseline(str(sensor_id))
        for _ in range(50):
            baseline.add(50.0 + random.gauss(0, 2))

        metric = make_metric(51.0, sensor_id=sensor_id)
        context = AgentContext(metrics=[metric])
        result = agent.process(context)

        assert result.success is True
        assert result.output["anomalies_detected"] == 0


# ---------------------------------------------------------------------------
# Property 9: Pipeline continua após falha de agente individual
# ---------------------------------------------------------------------------

class FailingAgent(BaseAgent):
    """Agente que sempre lança exceção."""
    @property
    def name(self):
        return "FailingAgent"

    def process(self, context: AgentContext) -> AgentResult:
        raise RuntimeError("Erro simulado no agente")


class SuccessAgent(BaseAgent):
    """Agente que sempre tem sucesso."""
    def __init__(self, name_suffix=""):
        self._name = f"SuccessAgent{name_suffix}"

    @property
    def name(self):
        return self._name

    def process(self, context: AgentContext) -> AgentResult:
        return AgentResult(agent_name=self.name, success=True, output={"ok": True})


class TestAgentPipeline:
    def test_pipeline_continues_after_failure(self):
        """Property 9: agente K falha → agentes K+1..N continuam."""
        agents = [
            SuccessAgent("1"),
            FailingAgent(),
            SuccessAgent("3"),
        ]
        pipeline = AgentPipeline(agents)
        context = AgentContext()
        results = pipeline.run(context)

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True

    def test_pipeline_all_success(self):
        agents = [SuccessAgent("1"), SuccessAgent("2"), SuccessAgent("3")]
        pipeline = AgentPipeline(agents)
        results = pipeline.run(AgentContext())
        assert all(r.success for r in results)
        assert len(results) == 3

    def test_pipeline_first_agent_fails(self):
        agents = [FailingAgent(), SuccessAgent("2")]
        pipeline = AgentPipeline(agents)
        results = pipeline.run(AgentContext())
        assert len(results) == 2
        assert results[0].success is False
        assert results[1].success is True

    def test_pipeline_all_fail(self):
        agents = [FailingAgent(), FailingAgent()]
        pipeline = AgentPipeline(agents)
        results = pipeline.run(AgentContext())
        assert len(results) == 2
        assert all(r.success is False for r in results)

    def test_pipeline_empty(self):
        pipeline = AgentPipeline([])
        results = pipeline.run(AgentContext())
        assert results == []


# ---------------------------------------------------------------------------
# Property 10: AutoRemediationAgent só executa com confiança >= 85%
# ---------------------------------------------------------------------------

class TestAutoRemediation:
    def test_no_action_below_threshold(self):
        """Property 10: confidence < 0.85 → não executa."""
        agent = AutoRemediationAgent()
        context = AgentContext(
            events=[make_event()],
            pipeline_data={"should_alert": True, "decision_confidence": 0.84},
        )
        result = agent.process(context)
        assert result.success is True
        assert result.output["skipped"] is True
        assert result.output["actions_executed"] == []

    def test_action_executed_at_threshold(self):
        """Property 10: confidence >= 0.85 → executa."""
        agent = AutoRemediationAgent()
        context = AgentContext(
            events=[make_event("high_cpu")],
            pipeline_data={"should_alert": True, "decision_confidence": 0.85},
        )
        result = agent.process(context)
        assert result.success is True
        assert result.output["skipped"] is False
        assert len(result.output["actions_executed"]) >= 1

    def test_no_action_when_decision_says_no(self):
        """Sem aprovação do DecisionAgent → não executa."""
        agent = AutoRemediationAgent()
        context = AgentContext(
            events=[make_event()],
            pipeline_data={"should_alert": False, "decision_confidence": 0.99},
        )
        result = agent.process(context)
        assert result.output["skipped"] is True

    def test_action_above_threshold(self):
        agent = AutoRemediationAgent()
        context = AgentContext(
            events=[make_event("service_down")],
            pipeline_data={"should_alert": True, "decision_confidence": 0.95},
        )
        result = agent.process(context)
        assert result.output["skipped"] is False
        actions = result.output["actions_executed"]
        assert any(a["action"] == "restart_service" for a in actions)


# ---------------------------------------------------------------------------
# Property 11: Feedback Loop classifica outcome por tempo de resolução
# ---------------------------------------------------------------------------

class TestFeedbackLoop:
    def test_positive_outcome_fast_resolution(self):
        """Property 11: < 300s → positive."""
        loop = FeedbackLoop()
        action = RemediationAction(
            agent_name="AutoRemediationAgent",
            action_type="restart_service",
            target_host="srv01",
        )
        action_id = loop.record_action(action)
        loop.record_result(action_id, ActionResult(success=True, resolution_time_seconds=120.0))

        history = loop.get_history()
        assert history[0]["outcome"] == "positive"

    def test_negative_outcome_slow_resolution(self):
        """Property 11: >= 300s → negative."""
        loop = FeedbackLoop()
        action = RemediationAction(
            agent_name="AutoRemediationAgent",
            action_type="restart_service",
            target_host="srv01",
        )
        action_id = loop.record_action(action)
        loop.record_result(action_id, ActionResult(success=False, resolution_time_seconds=600.0))

        history = loop.get_history()
        assert history[0]["outcome"] == "negative"

    def test_boundary_exactly_300s_is_negative(self):
        """Exatamente 300s → negative (>= 300)."""
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="A", action_type="test", target_host="h1")
        action_id = loop.record_action(action)
        loop.record_result(action_id, ActionResult(success=True, resolution_time_seconds=300.0))
        assert loop.get_history()[0]["outcome"] == "negative"

    def test_metrics_calculation(self):
        loop = FeedbackLoop()
        for i in range(3):
            action = RemediationAction(agent_name="A", action_type="test", target_host=f"h{i}")
            aid = loop.record_action(action)
            loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=100.0))

        metrics = loop.get_metrics()
        assert metrics.actions_total == 3
        assert metrics.actions_successful == 3
        assert metrics.mean_resolution_time_seconds == 100.0
        assert metrics.false_positive_rate == 0.0

    def test_weight_increases_on_positive(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="A", action_type="restart_service", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=True, resolution_time_seconds=50.0))
        assert loop.get_action_weight("restart_service") > 1.0

    def test_weight_decreases_on_negative(self):
        loop = FeedbackLoop()
        action = RemediationAction(agent_name="A", action_type="restart_service", target_host="h1")
        aid = loop.record_action(action)
        loop.record_result(aid, ActionResult(success=False, resolution_time_seconds=500.0))
        assert loop.get_action_weight("restart_service") < 1.0


# ---------------------------------------------------------------------------
# Property 12: RootCause identifica nó pai com confiança >= 0.8
# ---------------------------------------------------------------------------

class TestRootCauseEngine:
    def _make_topology_with_switch(self):
        """Switch → srv1, srv2, srv3."""
        g = TopologyGraph()
        switch = TopologyNode(type=NodeType.SWITCH)
        srv1 = TopologyNode(type=NodeType.SERVER, parent_id=switch.id)
        srv2 = TopologyNode(type=NodeType.SERVER, parent_id=switch.id)
        srv3 = TopologyNode(type=NodeType.SERVER, parent_id=switch.id)
        for node in [switch, srv1, srv2, srv3]:
            g.add_node(node)
        return g, switch, srv1, srv2, srv3

    def test_root_cause_identifies_switch_when_all_servers_down(self):
        """Property 12: N>=2 filhos offline → pai identificado com confidence >= 0.8."""
        g, switch, srv1, srv2, srv3 = self._make_topology_with_switch()
        engine = RootCauseEngine()

        # Todos os 3 servidores offline
        events = [
            make_event("host_unreachable", host_id=srv1.id),
            make_event("host_unreachable", host_id=srv2.id),
            make_event("host_unreachable", host_id=srv3.id),
        ]

        result = engine.analyze(events, g)
        assert result is not None
        assert result.root_node_id == str(switch.id)
        assert result.confidence >= 0.8

    def test_root_cause_two_of_three_servers_down(self):
        """2 de 3 filhos offline → confidence = 2/3 ≈ 0.67 (pode ser < 0.8)."""
        g, switch, srv1, srv2, srv3 = self._make_topology_with_switch()
        engine = RootCauseEngine()

        events = [
            make_event("host_unreachable", host_id=srv1.id),
            make_event("host_unreachable", host_id=srv2.id),
        ]

        result = engine.analyze(events, g)
        assert result is not None
        # Deve identificar o switch como causa raiz
        assert result.root_node_id == str(switch.id)

    def test_root_cause_no_topology(self):
        """Sem topologia: usa host do evento mais antigo."""
        engine = RootCauseEngine()
        events = [make_event(), make_event()]
        result = engine.analyze(events, None)
        assert result is not None
        assert result.confidence == 0.5

    def test_root_cause_empty_events(self):
        engine = RootCauseEngine()
        result = engine.analyze([], None)
        assert result is None

    def test_root_cause_single_event(self):
        engine = RootCauseEngine()
        event = make_event()
        result = engine.analyze([event], None)
        assert result is not None
        assert result.affected_nodes_count == 1


# ---------------------------------------------------------------------------
# Smart Scheduler
# ---------------------------------------------------------------------------

class TestSmartScheduler:
    def test_anomaly_reduces_interval(self):
        agent = SmartSchedulerAgent()
        sensor_id = uuid4()
        event = Event(
            host_id=uuid4(),
            type="anomaly",
            severity=EventSeverity.WARNING,
            timestamp=datetime.now(timezone.utc),
            source_metric_id=sensor_id,
        )
        context = AgentContext(events=[event])
        result = agent.process(context)
        assert result.success is True
        assert agent.get_interval(str(sensor_id)) == 30

    def test_default_interval_without_anomaly(self):
        agent = SmartSchedulerAgent()
        assert agent.get_interval("unknown_sensor") == 60
