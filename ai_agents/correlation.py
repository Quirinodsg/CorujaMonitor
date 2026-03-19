"""
Correlation Agent — Coruja Monitor v3.0
Correlaciona eventos relacionados em janela de 5 minutos.
Encapsula ai-agent/event_correlator.py existente.
"""
import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from core.spec.models import Event
from ai_agents.base_agent import BaseAgent, AgentContext, AgentResult

logger = logging.getLogger(__name__)

CORRELATION_WINDOW_MINUTES = 5


class CorrelationAgent(BaseAgent):
    """
    Agrupa eventos relacionados dentro de janela de 5 minutos.
    Critério: mesmo host OU hosts do mesmo grupo topológico.
    """

    def process(self, context: AgentContext) -> AgentResult:
        try:
            events = list(context.events)
            if not events:
                return AgentResult(
                    agent_name=self.name, success=True,
                    output={"correlated_groups": []},
                )

            # Agrupar por host_id dentro da janela de tempo
            groups = self._correlate_by_host_and_time(events)

            # Tentar correlacionar por topologia se disponível
            if context.topology:
                groups = self._merge_topology_groups(groups, context.topology)

            serializable_groups = [
                {
                    "group_id": i,
                    "event_ids": [str(e.id) for e in group],
                    "host_ids": list({str(e.host_id) for e in group}),
                    "event_count": len(group),
                    "time_span_seconds": self._time_span(group),
                }
                for i, group in enumerate(groups)
            ]

            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "correlated_groups": serializable_groups,
                    "total_groups": len(groups),
                    "_groups_raw": groups,  # para uso interno do pipeline
                },
            )
        except Exception as e:
            logger.error("CorrelationAgent error: %s", e)
            return AgentResult(agent_name=self.name, success=False, error=str(e))

    def _correlate_by_host_and_time(self, events: list[Event]) -> list[list[Event]]:
        """Agrupa eventos do mesmo host dentro da janela de 5 minutos."""
        # Ordenar por timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # Agrupar por host
        by_host: dict[str, list[Event]] = defaultdict(list)
        for event in sorted_events:
            by_host[str(event.host_id)].append(event)

        groups = []
        for host_id, host_events in by_host.items():
            # Janela deslizante de 5 minutos
            window_groups = self._sliding_window_groups(host_events)
            groups.extend(window_groups)

        return groups

    def _sliding_window_groups(self, events: list[Event]) -> list[list[Event]]:
        """Divide eventos em grupos onde todos estão dentro de 5 minutos entre si."""
        if not events:
            return []

        groups = []
        current_group = [events[0]]

        for event in events[1:]:
            window_start = current_group[0].timestamp
            if (event.timestamp - window_start) <= timedelta(minutes=CORRELATION_WINDOW_MINUTES):
                current_group.append(event)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [event]

        if current_group:
            groups.append(current_group)

        return groups

    def _merge_topology_groups(self, groups: list[list[Event]], topology) -> list[list[Event]]:
        """
        Mescla grupos de hosts que compartilham ancestral comum na topologia.
        Se dois grupos têm hosts com ancestral comum, são fundidos em um único grupo.
        """
        if not groups or len(groups) < 2:
            return groups

        # Mapear host_id → set de ancestrais
        host_ancestors: dict[str, set] = {}
        for group in groups:
            for event in group:
                host_id = str(event.host_id)
                if host_id not in host_ancestors:
                    ancestors = set(topology.get_ancestors(host_id))
                    ancestors.add(host_id)  # incluir o próprio nó
                    host_ancestors[host_id] = ancestors

        # Union-Find para mesclar grupos com ancestral comum
        parent = list(range(len(groups)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for i in range(len(groups)):
            hosts_i = {str(e.host_id) for e in groups[i]}
            ancestors_i = set()
            for h in hosts_i:
                ancestors_i |= host_ancestors.get(h, {h})

            for j in range(i + 1, len(groups)):
                hosts_j = {str(e.host_id) for e in groups[j]}
                ancestors_j = set()
                for h in hosts_j:
                    ancestors_j |= host_ancestors.get(h, {h})

                # Mesclar se compartilham ancestral comum (excluindo raiz genérica)
                if ancestors_i & ancestors_j:
                    union(i, j)

        # Reagrupar
        merged: dict[int, list] = {}
        for i, group in enumerate(groups):
            root = find(i)
            if root not in merged:
                merged[root] = []
            merged[root].extend(group)

        return list(merged.values())

    def _time_span(self, events: list[Event]) -> float:
        """Retorna span de tempo em segundos entre primeiro e último evento."""
        if len(events) < 2:
            return 0.0
        timestamps = [e.timestamp for e in events]
        return (max(timestamps) - min(timestamps)).total_seconds()
