"""
Event Grouper — Coruja Monitor v3.0
Agrupa eventos do mesmo host em janela de 5 minutos.
"""
from datetime import timedelta
from collections import defaultdict

from core.spec.models import Event

GROUPING_WINDOW_MINUTES = 5


class EventGrouper:
    """
    Agrupa eventos relacionados:
    - Mesmo host
    - Dentro de janela de 5 minutos
    """

    def group(self, events: list[Event]) -> list[list[Event]]:
        """
        Retorna lista de grupos de eventos.
        Cada grupo contém eventos do mesmo host dentro de 5 minutos.
        """
        if not events:
            return []

        # Ordenar por timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # Agrupar por host
        by_host: dict[str, list[Event]] = defaultdict(list)
        for event in sorted_events:
            by_host[str(event.host_id)].append(event)

        groups = []
        for host_id, host_events in by_host.items():
            host_groups = self._window_groups(host_events)
            groups.extend(host_groups)

        return groups

    def _window_groups(self, events: list[Event]) -> list[list[Event]]:
        """Divide eventos em grupos dentro da janela de 5 minutos."""
        if not events:
            return []

        groups = []
        current = [events[0]]

        for event in events[1:]:
            if (event.timestamp - current[0].timestamp) <= timedelta(minutes=GROUPING_WINDOW_MINUTES):
                current.append(event)
            else:
                groups.append(current)
                current = [event]

        groups.append(current)
        return groups
