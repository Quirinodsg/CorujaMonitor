"""
Testes da Fase 3 — Topology Engine
Cobre: Property 5 (blast radius = descendentes), Property 6 (round-trip persistência)
"""
import pytest
from uuid import uuid4

from core.spec.models import TopologyNode
from core.spec.enums import NodeType
from topology_engine.graph import TopologyGraph
from topology_engine.impact import ImpactCalculator, BlastRadius


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_graph():
    """Switch → 2 Servidores → 2 Serviços cada."""
    g = TopologyGraph()
    switch = TopologyNode(type=NodeType.SWITCH)
    srv1 = TopologyNode(type=NodeType.SERVER, parent_id=switch.id)
    srv2 = TopologyNode(type=NodeType.SERVER, parent_id=switch.id)
    svc1 = TopologyNode(type=NodeType.SERVICE, parent_id=srv1.id)
    svc2 = TopologyNode(type=NodeType.SERVICE, parent_id=srv1.id)
    svc3 = TopologyNode(type=NodeType.SERVICE, parent_id=srv2.id)
    app1 = TopologyNode(type=NodeType.APPLICATION, parent_id=svc1.id)

    for node in [switch, srv1, srv2, svc1, svc2, svc3, app1]:
        g.add_node(node)

    return g, switch, srv1, srv2, svc1, svc2, svc3, app1


# ---------------------------------------------------------------------------
# Property 5: Blast radius inclui todos os descendentes
# ---------------------------------------------------------------------------

class TestBlastRadius:
    def test_switch_blast_radius_equals_all_descendants(self, simple_graph):
        g, switch, srv1, srv2, svc1, svc2, svc3, app1 = simple_graph
        calc = ImpactCalculator(g)
        br = calc.blast_radius(str(switch.id))
        # Switch tem 6 descendentes: srv1, srv2, svc1, svc2, svc3, app1
        assert br.total_impact == 6
        # total_impact deve ser igual ao número de descendentes no grafo
        descendants = g.get_descendants(str(switch.id))
        assert br.total_impact == len(descendants)

    def test_server_blast_radius(self, simple_graph):
        g, switch, srv1, srv2, svc1, svc2, svc3, app1 = simple_graph
        calc = ImpactCalculator(g)
        br = calc.blast_radius(str(srv1.id))
        # srv1 tem 3 descendentes: svc1, svc2, app1
        assert br.total_impact == 3
        descendants = g.get_descendants(str(srv1.id))
        assert br.total_impact == len(descendants)

    def test_leaf_node_blast_radius_zero(self, simple_graph):
        g, switch, srv1, srv2, svc1, svc2, svc3, app1 = simple_graph
        calc = ImpactCalculator(g)
        br = calc.blast_radius(str(app1.id))
        assert br.total_impact == 0
        assert br.affected_hosts == []
        assert br.affected_services == []
        assert br.affected_applications == []

    def test_blast_radius_classifies_by_type(self, simple_graph):
        g, switch, srv1, srv2, svc1, svc2, svc3, app1 = simple_graph
        calc = ImpactCalculator(g)
        br = calc.blast_radius(str(switch.id))
        # 2 servidores, 3 serviços, 1 aplicação
        assert len(br.affected_hosts) == 2
        assert len(br.affected_services) == 3
        assert len(br.affected_applications) == 1

    def test_nonexistent_node_blast_radius(self):
        g = TopologyGraph()
        calc = ImpactCalculator(g)
        br = calc.blast_radius("nonexistent-id")
        assert br.total_impact == 0

    def test_propagate_impact(self, simple_graph):
        g, switch, *_ = simple_graph
        calc = ImpactCalculator(g)
        impacted = calc.propagate_impact(str(switch.id), "impacted")
        assert len(impacted) == 6
        for status in impacted.values():
            assert status == "impacted"


# ---------------------------------------------------------------------------
# Property 6: Round-trip de persistência do grafo
# ---------------------------------------------------------------------------

class TestGraphPersistence:
    def test_roundtrip_preserves_node_count(self, simple_graph):
        g, *_ = simple_graph
        data = g.to_dict()
        restored = TopologyGraph.from_dict(data)
        assert restored.node_count() == g.node_count()

    def test_roundtrip_preserves_edge_count(self, simple_graph):
        g, *_ = simple_graph
        data = g.to_dict()
        restored = TopologyGraph.from_dict(data)
        assert restored.edge_count() == g.edge_count()

    def test_roundtrip_preserves_relationships(self, simple_graph):
        g, switch, srv1, srv2, *_ = simple_graph
        data = g.to_dict()
        restored = TopologyGraph.from_dict(data)
        # Verificar que switch ainda tem srv1 e srv2 como filhos
        switch_id = str(switch.id)
        children = restored.get_children(switch_id)
        assert str(srv1.id) in children
        assert str(srv2.id) in children

    def test_roundtrip_empty_graph(self):
        g = TopologyGraph()
        data = g.to_dict()
        restored = TopologyGraph.from_dict(data)
        assert restored.node_count() == 0
        assert restored.edge_count() == 0

    def test_to_dict_format(self, simple_graph):
        g, *_ = simple_graph
        data = g.to_dict()
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        # Cada nó deve ter id e type
        for node in data["nodes"]:
            assert "id" in node
            assert "type" in node


# ---------------------------------------------------------------------------
# Testes de hierarquia e consultas
# ---------------------------------------------------------------------------

class TestHierarchy:
    def test_get_ancestors(self, simple_graph):
        g, switch, srv1, srv2, svc1, *_ = simple_graph
        ancestors = g.get_ancestors(str(svc1.id))
        assert str(srv1.id) in ancestors
        assert str(switch.id) in ancestors

    def test_get_descendants(self, simple_graph):
        g, switch, srv1, srv2, svc1, svc2, svc3, app1 = simple_graph
        descendants = g.get_descendants(str(switch.id))
        assert str(srv1.id) in descendants
        assert str(svc1.id) in descendants
        assert str(app1.id) in descendants

    def test_get_children_direct_only(self, simple_graph):
        g, switch, srv1, srv2, *_ = simple_graph
        children = g.get_children(str(switch.id))
        assert str(srv1.id) in children
        assert str(srv2.id) in children
        # Netos não devem aparecer como filhos diretos
        assert len(children) == 2

    def test_remove_node(self, simple_graph):
        g, switch, srv1, *_ = simple_graph
        initial_count = g.node_count()
        g.remove_node(str(srv1.id))
        assert g.node_count() == initial_count - 1
        assert g.get_node(str(srv1.id)) is None

    def test_add_edge_explicit(self):
        g = TopologyGraph()
        n1 = TopologyNode(type=NodeType.SWITCH)
        n2 = TopologyNode(type=NodeType.SERVER)
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(str(n1.id), str(n2.id))
        assert str(n2.id) in g.get_children(str(n1.id))
