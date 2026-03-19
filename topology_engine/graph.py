"""
Topology Graph — Coruja Monitor v3.0
Modela hierarquia de infraestrutura: Switch → Servidor → Serviço → Aplicação
"""
import logging
from typing import Optional

import networkx as nx

from core.spec.models import TopologyNode
from core.spec.enums import NodeType

logger = logging.getLogger(__name__)


class TopologyGraph:
    """
    Grafo dirigido de topologia de infraestrutura.
    Aresta parent → child representa relação hierárquica.
    """

    def __init__(self):
        self._graph: nx.DiGraph = nx.DiGraph()
        # {node_id: TopologyNode}
        self._nodes: dict[str, TopologyNode] = {}

    # ------------------------------------------------------------------
    # Mutação
    # ------------------------------------------------------------------

    def add_node(self, node: TopologyNode) -> None:
        """Adiciona ou atualiza nó no grafo."""
        node_id = str(node.id)
        self._nodes[node_id] = node
        self._graph.add_node(node_id, type=node.type, metadata=node.metadata)

        # Conectar ao pai se informado
        if node.parent_id:
            parent_id = str(node.parent_id)
            if parent_id in self._nodes:
                self._graph.add_edge(parent_id, node_id)
            else:
                logger.warning("TopologyGraph: pai %s não encontrado para nó %s", parent_id, node_id)

        logger.debug("TopologyGraph: nó adicionado %s (%s)", node_id, node.type)

    def add_edge(self, parent_id: str, child_id: str) -> None:
        """Adiciona aresta explícita parent → child."""
        self._graph.add_edge(parent_id, child_id)

    def remove_node(self, node_id: str) -> None:
        """Remove nó e todas as suas arestas."""
        self._nodes.pop(node_id, None)
        if self._graph.has_node(node_id):
            self._graph.remove_node(node_id)

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Optional[TopologyNode]:
        return self._nodes.get(node_id)

    def get_ancestors(self, node_id: str) -> list[str]:
        """Retorna todos os ancestrais (pais, avós, etc.) do nó."""
        if not self._graph.has_node(node_id):
            return []
        return list(nx.ancestors(self._graph, node_id))

    def get_descendants(self, node_id: str) -> list[str]:
        """Retorna todos os descendentes (filhos, netos, etc.) do nó."""
        if not self._graph.has_node(node_id):
            return []
        return list(nx.descendants(self._graph, node_id))

    def get_children(self, node_id: str) -> list[str]:
        """Retorna filhos diretos do nó."""
        if not self._graph.has_node(node_id):
            return []
        return list(self._graph.successors(node_id))

    def get_parents(self, node_id: str) -> list[str]:
        """Retorna pais diretos do nó."""
        if not self._graph.has_node(node_id):
            return []
        return list(self._graph.predecessors(node_id))

    def all_node_ids(self) -> list[str]:
        return list(self._graph.nodes())

    def all_edges(self) -> list[tuple[str, str]]:
        return list(self._graph.edges())

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Retorna grafo em formato compatível com visualização (react-force-graph).
        {nodes: [{id, type, metadata}], edges: [{source, target}]}
        """
        nodes = []
        for node_id, node in self._nodes.items():
            nodes.append({
                "id": node_id,
                "type": node.type if isinstance(node.type, str) else node.type.value,
                "metadata": node.metadata,
                "parent_id": str(node.parent_id) if node.parent_id else None,
            })

        edges = [{"source": src, "target": tgt} for src, tgt in self._graph.edges()]

        return {"nodes": nodes, "edges": edges}

    @classmethod
    def from_dict(cls, data: dict) -> "TopologyGraph":
        """Reconstrói grafo a partir do formato serializado."""
        graph = cls()
        # Primeiro passo: criar todos os nós sem arestas
        for n in data.get("nodes", []):
            node = TopologyNode(
                id=n["id"],
                type=n["type"],
                metadata=n.get("metadata", {}),
                parent_id=n.get("parent_id"),
            )
            # Adicionar sem conectar ao pai ainda
            node_id = str(node.id)
            graph._nodes[node_id] = node
            graph._graph.add_node(node_id, type=node.type, metadata=node.metadata)

        # Segundo passo: adicionar arestas
        for e in data.get("edges", []):
            graph._graph.add_edge(e["source"], e["target"])

        return graph

    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        return self._graph.number_of_edges()
