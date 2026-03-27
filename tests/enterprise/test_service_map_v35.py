"""
QA Enterprise — Service Map v3.5
Testa: criação de nós/arestas, propagação de status, raio de impacto,
deduplicação de arestas, serialização, build_from_db (mock).
"""
import sys
import types
import pytest
from unittest.mock import MagicMock, patch

# Garantir que 'models' no sys.modules tem Server, Sensor, Metric
# (pode ter sido injetado como módulo vazio por outros testes)
import types as _types
_models_mod = sys.modules.get("models")
if _models_mod is None:
    _models_mod = _types.ModuleType("models")
    sys.modules["models"] = _models_mod
if not hasattr(_models_mod, "Server"):
    _models_mod.Server = MagicMock()
if not hasattr(_models_mod, "Sensor"):
    _models_mod.Sensor = MagicMock()
if not hasattr(_models_mod, "Metric"):
    _models_mod.Metric = MagicMock()
if "database" not in sys.modules:
    sys.modules["database"] = _types.ModuleType("database")

from topology_engine.service_map import ServiceMap, ServiceNode, ServiceEdge


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_node(node_id: str, name: str = None, node_type: str = "server", status: str = "ok") -> ServiceNode:
    return ServiceNode(node_id=node_id, name=name or node_id, node_type=node_type, status=status)


# ─── 1. ServiceNode ──────────────────────────────────────────────────────────

class TestServiceNode:
    def test_to_dict_has_required_fields(self):
        node = make_node("server-1", "Web Server")
        d = node.to_dict()
        assert d["id"] == "server-1"
        assert d["name"] == "Web Server"
        assert d["type"] == "server"
        assert d["status"] == "ok"
        assert "updated_at" in d

    def test_default_status_is_ok(self):
        node = ServiceNode(node_id="n1", name="n1", node_type="server")
        assert node.status == "ok"

    def test_metadata_defaults_to_empty_dict(self):
        node = make_node("n1")
        assert node.metadata == {}


# ─── 2. ServiceEdge ──────────────────────────────────────────────────────────

class TestServiceEdge:
    def test_to_dict_has_required_fields(self):
        edge = ServiceEdge("src", "tgt", "depends_on", "label")
        d = edge.to_dict()
        assert d["source"] == "src"
        assert d["target"] == "tgt"
        assert d["type"] == "depends_on"
        assert d["label"] == "label"


# ─── 3. ServiceMap — Nós e Arestas ──────────────────────────────────────────

class TestServiceMapGraph:
    def test_add_node_stores_node(self):
        smap = ServiceMap()
        smap.add_node(make_node("server-1"))
        assert "server-1" in smap._nodes

    def test_add_edge_creates_edge(self):
        smap = ServiceMap()
        smap.add_node(make_node("server-1"))
        smap.add_node(make_node("service-1", node_type="service"))
        smap.add_edge("server-1", "service-1", "hosts")
        assert len(smap._edges) == 1
        assert smap._edges[0].source == "server-1"
        assert smap._edges[0].target == "service-1"

    def test_add_edge_deduplication(self):
        """Adicionar a mesma aresta duas vezes não cria duplicata."""
        smap = ServiceMap()
        smap.add_node(make_node("a"))
        smap.add_node(make_node("b"))
        smap.add_edge("a", "b")
        smap.add_edge("a", "b")
        assert len(smap._edges) == 1, "Aresta duplicada não deve ser criada"

    def test_add_edge_different_direction_allowed(self):
        """a→b e b→a são arestas distintas."""
        smap = ServiceMap()
        smap.add_node(make_node("a"))
        smap.add_node(make_node("b"))
        smap.add_edge("a", "b")
        smap.add_edge("b", "a")
        assert len(smap._edges) == 2


# ─── 4. Propagação de Status ─────────────────────────────────────────────────

class TestStatusPropagation:
    def test_critical_propagates_to_dependent(self):
        """Nó crítico propaga warning para dependentes via depends_on."""
        smap = ServiceMap()
        smap.add_node(make_node("db", node_type="database", status="ok"))
        smap.add_node(make_node("app", node_type="app", status="ok"))
        smap.add_edge("db", "app", "depends_on")

        smap.update_status("db", "critical")

        assert smap._nodes["db"].status == "critical"
        assert smap._nodes["app"].status == "warning", \
            "Dependente de nó crítico deve ficar em warning"

    def test_warning_does_not_propagate(self):
        """Status warning não propaga para dependentes."""
        smap = ServiceMap()
        smap.add_node(make_node("db", status="ok"))
        smap.add_node(make_node("app", status="ok"))
        smap.add_edge("db", "app", "depends_on")

        smap.update_status("db", "warning")
        assert smap._nodes["app"].status == "ok", \
            "Warning não deve propagar para dependentes"

    def test_hosts_edge_does_not_propagate(self):
        """Aresta do tipo 'hosts' não propaga status."""
        smap = ServiceMap()
        smap.add_node(make_node("server", status="ok"))
        smap.add_node(make_node("service", status="ok"))
        smap.add_edge("server", "service", "hosts")  # tipo 'hosts', não 'depends_on'

        smap.update_status("server", "critical")
        assert smap._nodes["service"].status == "ok", \
            "Aresta 'hosts' não deve propagar status"

    def test_update_nonexistent_node_is_noop(self):
        """Atualizar nó inexistente não lança exceção."""
        smap = ServiceMap()
        smap.update_status("ghost-node", "critical")  # não deve lançar


# ─── 5. Raio de Impacto ──────────────────────────────────────────────────────

class TestImpactRadius:
    def test_direct_impact(self):
        """Falha em A impacta B diretamente."""
        smap = ServiceMap()
        smap.add_node(make_node("A"))
        smap.add_node(make_node("B"))
        smap.add_edge("A", "B")
        impacted = smap.get_impact_radius("A")
        assert "B" in impacted

    def test_transitive_impact(self):
        """Falha em A impacta B e C (A→B→C)."""
        smap = ServiceMap()
        for n in ["A", "B", "C"]:
            smap.add_node(make_node(n))
        smap.add_edge("A", "B")
        smap.add_edge("B", "C")
        impacted = smap.get_impact_radius("A")
        assert "B" in impacted
        assert "C" in impacted

    def test_no_impact_isolated_node(self):
        """Nó sem dependentes tem raio de impacto vazio."""
        smap = ServiceMap()
        smap.add_node(make_node("isolated"))
        impacted = smap.get_impact_radius("isolated")
        assert impacted == []

    def test_circular_dependency_no_infinite_loop(self):
        """Dependência circular não causa loop infinito."""
        smap = ServiceMap()
        for n in ["A", "B", "C"]:
            smap.add_node(make_node(n))
        smap.add_edge("A", "B")
        smap.add_edge("B", "C")
        smap.add_edge("C", "A")  # ciclo
        impacted = smap.get_impact_radius("A")
        # Não deve travar — resultado pode variar mas deve terminar
        assert isinstance(impacted, list)

    def test_impact_radius_nonexistent_node(self):
        """Raio de impacto de nó inexistente retorna lista vazia."""
        smap = ServiceMap()
        impacted = smap.get_impact_radius("ghost")
        assert impacted == []


# ─── 6. Serialização to_dict ─────────────────────────────────────────────────

class TestSerialization:
    def test_to_dict_structure(self):
        """to_dict() retorna estrutura correta para react-force-graph."""
        smap = ServiceMap()
        smap.add_node(make_node("server-1", status="ok"))
        smap.add_node(make_node("service-1", node_type="service", status="critical"))
        smap.add_edge("server-1", "service-1", "hosts")

        d = smap.to_dict()
        assert "nodes" in d
        assert "edges" in d
        assert "stats" in d
        assert "generated_at" in d
        assert d["stats"]["total_nodes"] == 2
        assert d["stats"]["total_edges"] == 1

    def test_stats_status_counts(self):
        """stats.status conta corretamente por status."""
        smap = ServiceMap()
        smap.add_node(make_node("n1", status="ok"))
        smap.add_node(make_node("n2", status="ok"))
        smap.add_node(make_node("n3", status="critical"))
        smap.add_node(make_node("n4", status="warning"))

        d = smap.to_dict()
        assert d["stats"]["status"]["ok"] == 2
        assert d["stats"]["status"]["critical"] == 1
        assert d["stats"]["status"]["warning"] == 1

    def test_empty_map_serializes(self):
        """ServiceMap vazio serializa sem erros."""
        smap = ServiceMap()
        d = smap.to_dict()
        assert d["nodes"] == []
        assert d["edges"] == []
        assert d["stats"]["total_nodes"] == 0


# ─── 7. build_from_db (mock) ─────────────────────────────────────────────────

class TestBuildFromDb:
    def test_build_from_db_with_empty_db(self):
        """build_from_db com banco vazio retorna ServiceMap vazio sem erros."""
        mock_db = MagicMock()
        # Simular query vazia: db.query(Server).filter(...).all() → []
        mock_db.query.return_value.filter.return_value.all.return_value = []

        smap = ServiceMap.build_from_db(mock_db)
        assert isinstance(smap, ServiceMap)
        assert len(smap._nodes) == 0
        assert len(smap._edges) == 0

    def test_build_from_db_creates_server_nodes(self):
        """build_from_db cria nós para cada servidor ativo."""
        mock_db = MagicMock()

        mock_server = MagicMock()
        mock_server.id = 1
        mock_server.hostname = "web-server-01"
        mock_server.device_type = "server"
        mock_server.ip_address = "192.168.1.10"
        mock_server.os_type = "Windows"
        mock_server.group_name = "Production"
        mock_server.probe_id = 1

        call_count = [0]

        def query_side_effect(model):
            q = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                # Primeira chamada: servidores
                q.filter.return_value.all.return_value = [mock_server]
            else:
                # Demais chamadas: sensores e métricas
                q.filter.return_value.all.return_value = []
                q.filter.return_value.order_by.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = query_side_effect

        smap = ServiceMap.build_from_db(mock_db)
        assert "server-1" in smap._nodes
        assert smap._nodes["server-1"].name == "web-server-01"
