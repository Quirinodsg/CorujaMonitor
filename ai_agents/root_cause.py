"""
Root Cause Agent — Coruja Monitor v3.0
Usa topologia para identificar causa raiz de grupos de eventos correlacionados.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

from core.spec.models import Event
from core.spec.enums import EventSeverity
from topology_engine.graph import TopologyGraph
from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class RootCauseResult:
    root_node_id: str
    confidence: float
    affected_nodes: list[str] = field(default_factory=list)
    affected_nodes_count: int = 0
    estimated_impact: dict = field(default_factory=dict)
    reasoning: str = ""


class RootCauseEngine:
    """
    Analisa grupos de eventos e identifica causa raiz via topologia.

    Algoritmo:
    1. Agrupar eventos por nó pai (via topology.get_ancestors)
    2. Ordenar por timestamp (mais antigo primeiro)
    3. Nó pai com mais descendentes afetados = causa raiz candidata
    4. confidence = affected_descendants / total_descendants
    """

    def analyze(self, events: list[Event], topology: Optional[TopologyGraph]) -> Optional[RootCauseResult]:
        if not events:
            return None

        if topology is None:
            # Sem topologia: usar host do evento mais antigo como causa raiz
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            oldest = sorted_events[0]
            # Extrair descrição útil do evento
            desc = getattr(oldest, 'description', None) or str(oldest.host_id)
            event_type = getattr(oldest, 'type', 'unknown')
            return RootCauseResult(
                root_node_id=str(oldest.host_id),
                confidence=0.5,
                affected_nodes=[str(e.host_id) for e in events],
                affected_nodes_count=len(events),
                reasoning=f"Análise baseada em {len(events)} evento(s): {desc}",
            )

        affected_host_ids = {str(e.host_id) for e in events}

        # Para cada host afetado, encontrar ancestrais
        ancestor_score: dict[str, int] = {}
        for host_id in affected_host_ids:
            ancestors = topology.get_ancestors(host_id)
            for ancestor in ancestors:
                ancestor_score[ancestor] = ancestor_score.get(ancestor, 0) + 1

        if not ancestor_score:
            # Sem ancestrais comuns — usar host do evento mais antigo
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            oldest = sorted_events[0]
            desc = getattr(oldest, 'description', None) or str(oldest.host_id)
            return RootCauseResult(
                root_node_id=str(oldest.host_id),
                confidence=0.5,
                affected_nodes=list(affected_host_ids),
                affected_nodes_count=len(affected_host_ids),
                reasoning=f"Análise baseada em {len(events)} evento(s): {desc}",
            )

        # Nó com maior score = mais descendentes afetados
        root_node_id = max(ancestor_score, key=lambda k: ancestor_score[k])
        affected_count = ancestor_score[root_node_id]

        # Calcular confiança: afetados / total de descendentes do nó raiz
        total_descendants = len(topology.get_descendants(root_node_id))
        confidence = affected_count / total_descendants if total_descendants > 0 else 0.5

        # Impacto estimado
        descendants = topology.get_descendants(root_node_id)
        services = []
        applications = []
        for desc_id in descendants:
            node = topology.get_node(desc_id)
            if node:
                node_type = node.type if isinstance(node.type, str) else node.type.value
                if node_type == "service":
                    services.append(desc_id)
                elif node_type == "application":
                    applications.append(desc_id)

        return RootCauseResult(
            root_node_id=root_node_id,
            confidence=confidence,
            affected_nodes=list(affected_host_ids),
            affected_nodes_count=len(affected_host_ids),
            estimated_impact={"services": services, "applications": applications},
            reasoning=(
                f"Nó {root_node_id} tem {affected_count}/{total_descendants} "
                f"descendentes afetados (confidence={confidence:.2f})"
            ),
        )


class RootCauseAgent(BaseAgent):
    """Agente que usa RootCauseEngine para identificar causa raiz."""

    def __init__(self):
        self._engine = RootCauseEngine()

    def process(self, context: AgentContext) -> AgentResult:
        try:
            # Pegar grupos correlacionados do agente anterior
            groups_raw = context.pipeline_data.get("correlation_groups", [context.events])

            results = []
            for group in groups_raw:
                if not group:
                    continue
                result = self._engine.analyze(group, context.topology)
                if result:
                    results.append({
                        "root_node_id": result.root_node_id,
                        "confidence": result.confidence,
                        "affected_nodes_count": result.affected_nodes_count,
                        "affected_nodes": result.affected_nodes,
                        "estimated_impact": result.estimated_impact,
                        "reasoning": result.reasoning,
                    })

            return AgentResult(
                agent_name=self.name,
                success=True,
                output={"root_cause_results": results},
            )
        except Exception as e:
            logger.error("RootCauseAgent error: %s", e)
            return AgentResult(agent_name=self.name, success=False, error=str(e))
