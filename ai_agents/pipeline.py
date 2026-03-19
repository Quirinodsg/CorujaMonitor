"""
Agent Pipeline — Coruja Monitor v3.0
Orquestra agentes sequencialmente com fallback por agente.
Property 9: se agente K falhar, agentes K+1..N continuam executando.
"""
import logging
import time
from collections import deque

from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

# Circuit breaker: agente com > 50% falhas nas últimas 10 execuções
CIRCUIT_BREAKER_WINDOW = 10
CIRCUIT_BREAKER_THRESHOLD = 0.5
CIRCUIT_OPEN_SECONDS = 300  # 5 minutos


class CircuitBreaker:
    def __init__(self, window: int = CIRCUIT_BREAKER_WINDOW):
        self._results: deque[bool] = deque(maxlen=window)
        self._open_until: float = 0.0

    def record(self, success: bool) -> None:
        self._results.append(success)

    def is_open(self) -> bool:
        if time.monotonic() < self._open_until:
            return True
        if len(self._results) < CIRCUIT_BREAKER_WINDOW:
            return False
        failure_rate = self._results.count(False) / len(self._results)
        if failure_rate > CIRCUIT_BREAKER_THRESHOLD:
            self._open_until = time.monotonic() + CIRCUIT_OPEN_SECONDS
            return True
        return False

    def reset(self) -> None:
        self._results.clear()
        self._open_until = 0.0


class AgentPipeline:
    """
    Orquestra agentes em pipeline sequencial.
    Ordem padrão: AnomalyDetection → Correlation → RootCause → Decision → AutoRemediation

    Property 9: falha em agente K não interrompe agentes K+1..N.
    """

    def __init__(self, agents: list[BaseAgent]):
        self._agents = agents
        self._circuit_breakers: dict[str, CircuitBreaker] = {
            agent.name: CircuitBreaker() for agent in agents
        }

    def run(self, context: AgentContext) -> list[AgentResult]:
        """
        Executa todos os agentes sequencialmente.
        Propaga dados entre agentes via context.pipeline_data.
        Retorna lista com N resultados (um por agente).
        """
        results: list[AgentResult] = []

        for agent in self._agents:
            cb = self._circuit_breakers[agent.name]

            if cb.is_open():
                logger.warning("AgentPipeline: circuit breaker OPEN para %s — pulando", agent.name)
                results.append(AgentResult(
                    agent_name=agent.name,
                    success=False,
                    error="circuit_breaker_open",
                ))
                continue

            try:
                result = agent.process(context)
                cb.record(result.success)
                results.append(result)

                # Propagar dados para próximos agentes
                self._propagate(result, context)

            except Exception as e:
                logger.error("AgentPipeline: agente %s lançou exceção: %s", agent.name, e)
                cb.record(False)
                results.append(AgentResult(
                    agent_name=agent.name,
                    success=False,
                    error=str(e),
                ))
                # Property 9: continua com próximos agentes

        return results

    def _propagate(self, result: AgentResult, context: AgentContext) -> None:
        """Propaga output do agente para pipeline_data do contexto."""
        if not result.success:
            return

        output = result.output
        agent_name = result.agent_name

        if "CorrelationAgent" in agent_name:
            groups_raw = output.get("_groups_raw", [])
            context.pipeline_data["correlation_groups"] = groups_raw

        elif "RootCauseAgent" in agent_name:
            context.pipeline_data["root_cause_results"] = output.get("root_cause_results", [])

        elif "DecisionAgent" in agent_name:
            context.pipeline_data["should_alert"] = output.get("should_alert", False)
            context.pipeline_data["decision_confidence"] = output.get("confidence", 0.0)
