"""
Alert Engine — Coruja Monitor v3.0
Orquestra: DuplicateSuppressor → EventGrouper → AlertPrioritizer → AlertNotifier
"""
import logging
import time
from datetime import datetime, timezone
from collections import defaultdict
from typing import Optional

from core.spec.models import Event, Alert
from core.spec.enums import EventSeverity, AlertStatus
from alert_engine.suppressor import DuplicateSuppressor
from alert_engine.grouper import EventGrouper
from alert_engine.prioritizer import AlertPrioritizer
from alert_engine.notifier import AlertNotifier

logger = logging.getLogger(__name__)

# Flood protection: > 100 eventos/minuto do mesmo host
FLOOD_THRESHOLD = 100
FLOOD_WINDOW_SECONDS = 60

# Janelas de manutenção: {host_id: (start, end)}
MaintenanceWindows = dict[str, tuple[datetime, datetime]]


class AlertEngine:
    """
    Motor de alertas inteligentes.
    - Suprime duplicados (TTL 5min)
    - Agrupa eventos (janela 5min)
    - Prioriza automaticamente
    - Notifica canais configurados
    - Flood protection (> 100 eventos/min → 1 alerta)
    - Janelas de manutenção
    """

    def __init__(
        self,
        suppressor: Optional[DuplicateSuppressor] = None,
        grouper: Optional[EventGrouper] = None,
        prioritizer: Optional[AlertPrioritizer] = None,
        notifier: Optional[AlertNotifier] = None,
        notification_channels: Optional[list[str]] = None,
    ):
        self._suppressor = suppressor or DuplicateSuppressor()
        self._grouper = grouper or EventGrouper()
        self._prioritizer = prioritizer or AlertPrioritizer()
        self._notifier = notifier or AlertNotifier()
        self._channels = notification_channels or []

        # Janelas de manutenção: {host_id: (start_dt, end_dt)}
        self._maintenance_windows: MaintenanceWindows = {}

        # Métricas
        self._metrics = {
            "alerts_total": 0,
            "alerts_suppressed": 0,
            "alerts_grouped": 0,
            "alerts_flood_protected": 0,
        }

        # Flood tracking: {host_id: [timestamps]}
        self._flood_tracker: dict[str, list[float]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Processamento principal
    # ------------------------------------------------------------------

    def process_events(self, events: list[Event]) -> list[Alert]:
        """
        Processa lista de eventos e retorna alertas gerados.
        """
        if not events:
            return []

        # 1. Filtrar eventos de hosts em manutenção
        active_events = self._filter_maintenance(events)
        suppressed_by_maintenance = len(events) - len(active_events)
        if suppressed_by_maintenance:
            logger.info("AlertEngine: %d eventos suprimidos (manutenção)", suppressed_by_maintenance)

        if not active_events:
            return []

        # 2. Verificar flood protection por host
        flood_alerts = self._check_flood(active_events)
        if flood_alerts:
            self._metrics["alerts_flood_protected"] += len(flood_alerts)
            return flood_alerts

        # 3. Suprimir duplicados
        non_duplicate_events = []
        for event in active_events:
            if self._suppressor.is_duplicate(event):
                self._metrics["alerts_suppressed"] += 1
                logger.debug("AlertEngine: evento duplicado suprimido: %s", event.type)
            else:
                non_duplicate_events.append(event)
                self._suppressor.mark_seen(event)

        if not non_duplicate_events:
            return []

        # 4. Agrupar eventos
        groups = self._grouper.group(non_duplicate_events)
        if len(groups) < len(non_duplicate_events):
            self._metrics["alerts_grouped"] += len(non_duplicate_events) - len(groups)

        # 5. Criar alertas por grupo
        alerts = []
        for group in groups:
            alert = self._create_alert(group)
            if alert:
                alerts.append(alert)
                self._metrics["alerts_total"] += 1

        # 6. Notificar
        if self._channels:
            for alert in alerts:
                self._notifier.notify(alert, self._channels)

        return alerts

    def _filter_maintenance(self, events: list[Event]) -> list[Event]:
        """Remove eventos de hosts em janela de manutenção ativa."""
        now = datetime.now(timezone.utc)
        active = []
        for event in events:
            host_id = str(event.host_id)
            window = self._maintenance_windows.get(host_id)
            if window and window[0] <= now <= window[1]:
                continue
            active.append(event)
        return active

    def _check_flood(self, events: list[Event]) -> list[Alert]:
        """
        Detecta flood (> 100 eventos/min do mesmo host).
        Retorna lista com 1 alerta de alta prioridade se flood detectado.
        Property 16: > 100 eventos → 1 alerta de alta prioridade.
        """
        now = time.monotonic()
        flood_alerts = []

        # Contar eventos por host
        by_host: dict[str, list[Event]] = defaultdict(list)
        for event in events:
            by_host[str(event.host_id)].append(event)

        for host_id, host_events in by_host.items():
            # Limpar timestamps antigos
            self._flood_tracker[host_id] = [
                t for t in self._flood_tracker[host_id]
                if now - t < FLOOD_WINDOW_SECONDS
            ]
            # Adicionar novos
            self._flood_tracker[host_id].extend([now] * len(host_events))

            if len(self._flood_tracker[host_id]) > FLOOD_THRESHOLD:
                logger.warning(
                    "AlertEngine: FLOOD PROTECTION ativado para host %s (%d eventos/min)",
                    host_id, len(self._flood_tracker[host_id]),
                )
                # Criar 1 alerta consolidado de alta prioridade
                alert = Alert(
                    title=f"FLOOD: {len(host_events)} eventos em 1 minuto",
                    severity=EventSeverity.CRITICAL,
                    status=AlertStatus.OPEN,
                    affected_hosts=[host_events[0].host_id],
                    event_ids=[e.id for e in host_events],
                    root_cause="flood_protection",
                )
                flood_alerts.append(alert)
                # Limpar tracker para evitar alertas repetidos
                self._flood_tracker[host_id] = []

        return flood_alerts

    def _create_alert(self, events: list[Event]) -> Optional[Alert]:
        """Cria Alert a partir de um grupo de eventos."""
        if not events:
            return None

        # Determinar severidade máxima do grupo
        severity_order = {
            EventSeverity.CRITICAL.value: 3,
            EventSeverity.WARNING.value: 2,
            EventSeverity.INFO.value: 1,
        }
        max_severity = max(
            events,
            key=lambda e: severity_order.get(
                e.severity if isinstance(e.severity, str) else e.severity.value, 0
            ),
        ).severity

        # Hosts únicos afetados
        affected_hosts = list({e.host_id for e in events})

        # Título baseado no tipo de evento mais frequente
        event_types = [e.type for e in events]
        most_common_type = max(set(event_types), key=event_types.count)

        alert = Alert(
            title=f"{most_common_type} ({len(events)} eventos)",
            severity=max_severity,
            status=AlertStatus.OPEN,
            affected_hosts=affected_hosts,
            event_ids=[e.id for e in events],
        )

        logger.info(
            "AlertEngine: alerta criado %s (severity=%s, hosts=%d)",
            alert.id, alert.severity, len(affected_hosts),
        )
        return alert

    # ------------------------------------------------------------------
    # Janelas de manutenção
    # ------------------------------------------------------------------

    def set_maintenance_window(self, host_id: str, start: datetime, end: datetime) -> None:
        """Configura janela de manutenção para um host."""
        self._maintenance_windows[host_id] = (start, end)
        logger.info("AlertEngine: manutenção configurada para %s: %s → %s", host_id, start, end)

    def clear_maintenance_window(self, host_id: str) -> None:
        """Remove janela de manutenção."""
        self._maintenance_windows.pop(host_id, None)

    # ------------------------------------------------------------------
    # Métricas
    # ------------------------------------------------------------------

    def get_metrics(self) -> dict:
        return dict(self._metrics)
