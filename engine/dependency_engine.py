"""
Dependency Engine — Coruja Monitor v3.0
Controla execução condicional de sensores via DAG de dependências.

Regra central: se o sensor pai (ex: Ping) estiver CRITICAL,
todos os sensores filhos (ex: WMI) são suspensos para aquele host.
Isso evita tentativas desnecessárias e lockout de conta AD.
"""
import logging
import time
from typing import Optional

import networkx as nx

from core.spec.enums import SensorStatus

logger = logging.getLogger(__name__)


class DependencyEngine:
    """
    Gerencia um DAG de dependências entre sensores.

    Cache de estado: {host_id: {sensor_id: (SensorStatus, expires_at)}}
    TTL padrão: 30 segundos (sem Redis — compatível com probe Windows).
    """

    def __init__(self, cache_ttl: int = 30):
        self._graph: nx.DiGraph = nx.DiGraph()
        # {host_id: {sensor_id: (status_value, expires_at_monotonic)}}
        self._state_cache: dict[str, dict[str, tuple]] = {}
        self._cache_ttl = cache_ttl

    # ------------------------------------------------------------------
    # Gerenciamento do grafo
    # ------------------------------------------------------------------

    def add_sensor(self, sensor_id: str) -> None:
        """Registra um sensor como nó no grafo (sem dependências)."""
        self._graph.add_node(sensor_id)

    def add_dependency(self, parent_sensor_id: str, child_sensor_id: str) -> None:
        """
        Adiciona aresta parent → child.
        Rejeita se criar ciclo (mantém invariante DAG).
        """
        self._graph.add_edge(parent_sensor_id, child_sensor_id)
        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(parent_sensor_id, child_sensor_id)
            raise ValueError(
                f"Ciclo detectado: adicionar {parent_sensor_id} → {child_sensor_id} "
                f"criaria um ciclo no DAG de dependências."
            )
        logger.debug("Dependência adicionada: %s → %s", parent_sensor_id, child_sensor_id)

    def remove_dependency(self, parent_sensor_id: str, child_sensor_id: str) -> None:
        """Remove aresta do grafo."""
        if self._graph.has_edge(parent_sensor_id, child_sensor_id):
            self._graph.remove_edge(parent_sensor_id, child_sensor_id)

    # ------------------------------------------------------------------
    # Estado de execução
    # ------------------------------------------------------------------

    def update_state(self, sensor_id: str, host_id: str, status: SensorStatus) -> None:
        """
        Atualiza cache de estado com TTL.
        Registra log quando sensor pai muda para CRITICAL (suspensão) ou OK (reativação).
        """
        host_cache = self._state_cache.setdefault(host_id, {})
        old_entry = host_cache.get(sensor_id)
        old_status = old_entry[0] if old_entry else None

        expires_at = time.monotonic() + self._cache_ttl
        status_val = status.value if hasattr(status, "value") else status
        host_cache[sensor_id] = (status_val, expires_at)

        # Log de mudança relevante (pai com filhos)
        if old_status != status_val and list(self._graph.successors(sensor_id)):
            if status_val == SensorStatus.CRITICAL.value:
                logger.warning(
                    "⛔ DependencyEngine: sensor pai %s em host %s → CRITICAL "
                    "— filhos suspensos: %s",
                    sensor_id, host_id,
                    list(self._graph.successors(sensor_id)),
                )
            elif status_val == SensorStatus.OK.value and old_status == SensorStatus.CRITICAL.value:
                logger.info(
                    "✅ DependencyEngine: sensor pai %s em host %s → OK "
                    "— filhos reativados",
                    sensor_id, host_id,
                )

    def _get_cached_status(self, sensor_id: str, host_id: str) -> Optional[str]:
        """Retorna status do cache se não expirado, senão None."""
        host_cache = self._state_cache.get(host_id, {})
        entry = host_cache.get(sensor_id)
        if entry is None:
            return None
        status_val, expires_at = entry
        if time.monotonic() > expires_at:
            del host_cache[sensor_id]
            return None
        return status_val

    def should_execute(self, sensor_id: str, host_id: str) -> bool:
        """
        Retorna True se o sensor pode ser executado.
        False se qualquer ancestral (direto ou indireto) estiver CRITICAL.
        """
        # Verificar todos os ancestrais no DAG
        try:
            ancestors = nx.ancestors(self._graph, sensor_id)
        except nx.NetworkXError:
            # Sensor não está no grafo — pode executar
            return True

        for ancestor_id in ancestors:
            cached = self._get_cached_status(ancestor_id, host_id)
            if cached == SensorStatus.CRITICAL.value:
                logger.debug(
                    "DependencyEngine: sensor %s suspenso (ancestral %s CRITICAL) host=%s",
                    sensor_id, ancestor_id, host_id,
                )
                return False
        return True

    def get_suspended_sensors(self, host_id: str) -> list[str]:
        """Retorna IDs de sensores suspensos para o host (ancestral CRITICAL)."""
        suspended = []
        for node in self._graph.nodes():
            if not self.should_execute(node, host_id):
                suspended.append(node)
        return suspended

    # ------------------------------------------------------------------
    # Status / observabilidade
    # ------------------------------------------------------------------

    def get_graph_status(self) -> dict:
        """
        Retorna estado atual do grafo para endpoint de status.
        Formato: {total_nodes, total_edges, suspended_by_host}
        """
        suspended_by_host: dict[str, list[str]] = {}
        # Coletar todos os host_ids conhecidos no cache
        for host_id in list(self._state_cache.keys()):
            suspended = self.get_suspended_sensors(host_id)
            if suspended:
                suspended_by_host[host_id] = suspended

        return {
            "total_nodes": self._graph.number_of_nodes(),
            "total_edges": self._graph.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(self._graph),
            "suspended_by_host": suspended_by_host,
        }

    def clear_host_cache(self, host_id: str) -> None:
        """Remove cache de estado de um host específico."""
        self._state_cache.pop(host_id, None)
