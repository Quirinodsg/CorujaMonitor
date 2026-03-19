"""
Impact Calculator — Coruja Monitor v3.0
Calcula blast radius (raio de impacto) de qualquer nó na topologia.
"""
import logging
from dataclasses import dataclass, field

from core.spec.enums import NodeType
from topology_engine.graph import TopologyGraph

logger = logging.getLogger(__name__)


@dataclass
class BlastRadius:
    node_id: str
    affected_hosts: list[str] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)
    affected_applications: list[str] = field(default_factory=list)
    total_impact: int = 0


class ImpactCalculator:
    """
    Calcula o impacto de falha de um nó na topologia.
    total_impact = número total de descendentes afetados.
    """

    def __init__(self, graph: TopologyGraph):
        self._graph = graph

    def blast_radius(self, node_id: str) -> BlastRadius:
        """
        Retorna BlastRadius do nó: todos os descendentes classificados por tipo.
        total_impact == len(descendants) — Property 5.
        """
        descendants = self._graph.get_descendants(node_id)

        hosts, services, applications = [], [], []
        for desc_id in descendants:
            node = self._graph.get_node(desc_id)
            if node is None:
                continue
            node_type = node.type if isinstance(node.type, str) else node.type.value
            if node_type == NodeType.SERVER.value:
                hosts.append(desc_id)
            elif node_type == NodeType.SERVICE.value:
                services.append(desc_id)
            elif node_type == NodeType.APPLICATION.value:
                applications.append(desc_id)
            else:
                # SWITCH ou desconhecido — conta no total
                hosts.append(desc_id)

        result = BlastRadius(
            node_id=node_id,
            affected_hosts=hosts,
            affected_services=services,
            affected_applications=applications,
            total_impact=len(descendants),
        )
        logger.debug(
            "BlastRadius(%s): %d hosts, %d services, %d apps, total=%d",
            node_id, len(hosts), len(services), len(applications), len(descendants),
        )
        return result

    def propagate_impact(self, node_id: str, status: str) -> dict[str, str]:
        """
        Propaga status 'impacted' para todos os descendentes.
        Retorna {node_id: status} para todos os afetados.
        """
        descendants = self._graph.get_descendants(node_id)
        return {desc: status for desc in descendants}
