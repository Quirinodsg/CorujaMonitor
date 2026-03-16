"""
Root Cause Engine — análise de causa raiz baseada em correlação de eventos.

Lógica:
  1. Agrupa eventos por janela de tempo (5 min)
  2. Identifica evento mais severo como candidato a causa raiz
  3. Detecta padrões: switch offline → hosts dependentes offline
  4. Gera hipóteses rankeadas por confiança

Algoritmo inspirado em Dynatrace Davis e Datadog Watchdog.
"""
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

CORRELATION_WINDOW_SEC = 300  # 5 minutos
MIN_EVENTS_FOR_ANALYSIS = 2

SEVERITY_SCORE = {
    "critical": 10,
    "error": 7,
    "warning": 4,
    "info": 1,
}

INFRASTRUCTURE_PATTERNS = {
    "switch_offline": ["host_offline", "ping_failed", "snmp_timeout"],
    "network_degraded": ["high_latency", "packet_loss", "tcp_timeout"],
    "storage_failure": ["disk_full", "io_error", "disk_offline"],
    "resource_exhaustion": ["cpu_critical", "memory_critical", "swap_critical"],
}


@dataclass
class RCAEvent:
    host: str
    event_type: str
    severity: str
    timestamp: float
    message: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def score(self) -> int:
        return SEVERITY_SCORE.get(self.severity, 1)


@dataclass
class RCAHypothesis:
    root_cause_host: str
    root_cause_event: str
    confidence: float  # 0.0 - 1.0
    affected_hosts: List[str]
    affected_events: List[str]
    pattern: str
    explanation: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "root_cause_host": self.root_cause_host,
            "root_cause_event": self.root_cause_event,
            "confidence": round(self.confidence, 2),
            "affected_hosts": self.affected_hosts,
            "affected_events": self.affected_events,
            "pattern": self.pattern,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
        }


class RootCauseEngine:
    """
    Analisa eventos e identifica causa raiz.

    Uso:
        engine = RootCauseEngine()
        engine.add_event(RCAEvent(host="switch1", event_type="switch_offline", ...))
        engine.add_event(RCAEvent(host="srv1", event_type="host_offline", ...))
        hypotheses = engine.analyze()
    """

    def __init__(self, correlation_window: float = CORRELATION_WINDOW_SEC):
        self._window = correlation_window
        self._events: List[RCAEvent] = []

    def add_event(self, event: RCAEvent):
        self._events.append(event)
        # Manter apenas eventos dentro da janela
        cutoff = time.time() - self._window
        self._events = [e for e in self._events if e.timestamp >= cutoff]

    def add_events(self, events: List[RCAEvent]):
        for e in events:
            self.add_event(e)

    def analyze(self) -> List[RCAHypothesis]:
        """Retorna lista de hipóteses de causa raiz, ordenadas por confiança."""
        if len(self._events) < MIN_EVENTS_FOR_ANALYSIS:
            return []

        hypotheses = []

        # 1. Detectar padrões de infraestrutura
        hypotheses.extend(self._detect_infrastructure_patterns())

        # 2. Detectar cascata (host com mais eventos = causa raiz)
        hypotheses.extend(self._detect_cascade())

        # 3. Ordenar por confiança
        hypotheses.sort(key=lambda h: h.confidence, reverse=True)

        # Deduplicar por root_cause_host
        seen = set()
        unique = []
        for h in hypotheses:
            key = (h.root_cause_host, h.root_cause_event)
            if key not in seen:
                seen.add(key)
                unique.append(h)

        return unique[:5]  # top 5 hipóteses

    def _detect_infrastructure_patterns(self) -> List[RCAHypothesis]:
        hypotheses = []

        for pattern_name, trigger_events in INFRASTRUCTURE_PATTERNS.items():
            # Encontrar eventos que correspondem ao padrão
            triggers = [e for e in self._events if e.event_type in trigger_events]
            if not triggers:
                continue

            # Evento mais severo como causa raiz
            root = max(triggers, key=lambda e: e.score)

            # Hosts afetados após o evento raiz
            affected = [
                e.host for e in self._events
                if e.host != root.host and e.timestamp >= root.timestamp
            ]

            if not affected:
                continue

            confidence = min(0.95, 0.5 + len(affected) * 0.1)

            hypotheses.append(RCAHypothesis(
                root_cause_host=root.host,
                root_cause_event=root.event_type,
                confidence=confidence,
                affected_hosts=list(set(affected)),
                affected_events=list(set(e.event_type for e in self._events if e.host in affected)),
                pattern=pattern_name,
                explanation=(
                    f"Padrão '{pattern_name}' detectado: {root.host} ({root.event_type}) "
                    f"pode ter causado falhas em {len(set(affected))} host(s) dependente(s)."
                ),
            ))

        return hypotheses

    def _detect_cascade(self) -> List[RCAHypothesis]:
        """Detecta cascata: host com evento mais antigo e mais severo."""
        if not self._events:
            return []

        # Agrupar por host
        by_host: Dict[str, List[RCAEvent]] = defaultdict(list)
        for e in self._events:
            by_host[e.host].append(e)

        if len(by_host) < 2:
            return []

        # Host com evento mais antigo e mais severo
        host_scores = {
            host: (min(e.timestamp for e in evts), sum(e.score for e in evts))
            for host, evts in by_host.items()
        }

        root_host = min(host_scores, key=lambda h: host_scores[h][0])
        root_events = by_host[root_host]
        root_event = max(root_events, key=lambda e: e.score)

        affected = [h for h in by_host if h != root_host]
        confidence = min(0.85, 0.4 + len(affected) * 0.08)

        return [RCAHypothesis(
            root_cause_host=root_host,
            root_cause_event=root_event.event_type,
            confidence=confidence,
            affected_hosts=affected,
            affected_events=list(set(
                e.event_type for h in affected for e in by_host[h]
            )),
            pattern="cascade",
            explanation=(
                f"Cascata detectada: {root_host} foi o primeiro a falhar "
                f"({root_event.event_type}), seguido por {len(affected)} host(s)."
            ),
        )]

    def clear(self):
        self._events.clear()

    def event_count(self) -> int:
        return len(self._events)
