"""
Event Correlator - Correlação de alertas em janela de 5 minutos
Análise de causa raiz baseada em ordem temporal, severidade e dependências
"""
import logging
import time
from collections import defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

CORRELATION_WINDOW = 300  # 5 minutos em segundos
SEVERITY_ORDER = {"critical": 3, "warning": 2, "unknown": 1, "ok": 0}


class EventCorrelator:
    def __init__(self):
        self._events: List[Dict] = []
        self._host_deps: Dict[str, List[str]] = defaultdict(list)

    def add_event(self, event: Dict):
        """Adiciona evento para correlação"""
        event.setdefault("timestamp", time.time())
        self._events.append(event)
        # Limpar eventos fora da janela
        cutoff = time.time() - CORRELATION_WINDOW
        self._events = [e for e in self._events if e["timestamp"] >= cutoff]

    def set_dependency(self, host: str, depends_on: List[str]):
        """Define dependências entre hosts (ex: app depende de db)"""
        self._host_deps[host] = depends_on

    def correlate(self) -> List[Dict]:
        """
        Agrupa eventos relacionados e identifica causa raiz.
        Retorna lista de grupos correlacionados.
        """
        if not self._events:
            return []

        # Agrupar por host
        by_host: Dict[str, List[Dict]] = defaultdict(list)
        for e in self._events:
            by_host[e.get("host", "unknown")].append(e)

        groups = []
        processed_hosts = set()

        for host, events in by_host.items():
            if host in processed_hosts:
                continue

            # Encontrar hosts relacionados (dependências)
            related_hosts = {host}
            for dep in self._host_deps.get(host, []):
                if dep in by_host:
                    related_hosts.add(dep)

            # Coletar todos os eventos do grupo
            group_events = []
            for h in related_hosts:
                group_events.extend(by_host.get(h, []))
                processed_hosts.add(h)

            if not group_events:
                continue

            # Ordenar por timestamp
            group_events.sort(key=lambda e: e["timestamp"])

            # Causa raiz: evento mais antigo com maior severidade
            root_cause = max(
                group_events,
                key=lambda e: (
                    SEVERITY_ORDER.get(e.get("status", "ok"), 0),
                    -e["timestamp"],  # mais antigo primeiro em caso de empate
                )
            )

            groups.append({
                "correlation_id": f"corr_{int(time.time())}_{host}",
                "hosts": list(related_hosts),
                "event_count": len(group_events),
                "root_cause": {
                    "host": root_cause.get("host"),
                    "sensor_type": root_cause.get("sensor_type"),
                    "status": root_cause.get("status"),
                    "timestamp": root_cause.get("timestamp"),
                },
                "first_event": group_events[0]["timestamp"],
                "last_event": group_events[-1]["timestamp"],
                "max_severity": max(
                    SEVERITY_ORDER.get(e.get("status", "ok"), 0)
                    for e in group_events
                ),
                "events": group_events,
            })

        return groups

    def get_root_cause(self, host: str) -> Optional[Dict]:
        """Retorna a causa raiz mais provável para um host específico"""
        groups = self.correlate()
        for g in groups:
            if host in g["hosts"]:
                return g["root_cause"]
        return None
