"""
Alert Engine — Coruja Monitor v3.5 Enterprise
Smart Alerting: cooldown por alerta, agrupamento inteligente, supressão topológica.
Orquestra: DuplicateSuppressor → CooldownFilter → TopologySupressor → EventGrouper → AlertPrioritizer → AlertNotifier
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

# Smart Alerting: cooldown padrão por tipo de alerta (segundos)
DEFAULT_COOLDOWN_SECONDS = 300  # 5 minutos

# Janelas de manutenção: {host_id: (start, end)}
MaintenanceWindows = dict[str, tuple[datetime, datetime]]


class AlertEngine:
    """
    Motor de alertas inteligentes v3.5 Enterprise.
    - Suprime duplicados (TTL 5min)
    - Cooldown por tipo de alerta (5min padrão, configurável)
    - Agrupamento inteligente por host/tipo
    - Supressão topológica (switch caiu → não alertar filhos)
    - Supressão por DependencyEngine (ping CRITICAL → suprimir filhos)
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
        cooldown_seconds: int = DEFAULT_COOLDOWN_SECONDS,
        dependency_engine=None,
        redis_client=None,
    ):
        self._suppressor = suppressor or DuplicateSuppressor()
        self._grouper = grouper or EventGrouper()
        self._prioritizer = prioritizer or AlertPrioritizer()
        self._notifier = notifier or AlertNotifier()
        self._channels = notification_channels or []
        self._cooldown_seconds = cooldown_seconds
        self._dependency_engine = dependency_engine
        self._redis = redis_client

        # Janelas de manutenção: {host_id: (start_dt, end_dt)}
        self._maintenance_windows: MaintenanceWindows = {}

        # Métricas
        self._metrics = {
            "alerts_total": 0,
            "alerts_suppressed": 0,
            "alerts_grouped": 0,
            "alerts_flood_protected": 0,
            "alerts_cooldown_suppressed": 0,
            "alerts_topology_suppressed": 0,
        }

        # Flood tracking: {host_id: [timestamps]}
        self._flood_tracker: dict[str, list[float]] = defaultdict(list)

        # Cooldown tracking: {alert_key: last_fired_timestamp}
        # alert_key = f"{host_id}:{event_type}"
        self._cooldown_tracker: dict[str, float] = {}

        # Topologia: {host_id: parent_host_id} — carregado externamente
        # Se parent está em falha, filhos são suprimidos
        self._topology_parents: dict[str, str] = {}
        self._failed_hosts: set[str] = set()

    # ------------------------------------------------------------------
    # Processamento principal
    # ------------------------------------------------------------------

    def process_events(self, events: list[Event]) -> list[Alert]:
        """
        Processa lista de eventos e retorna alertas gerados.
        Pipeline: manutenção → flood → cooldown → topologia → duplicados → agrupamento → alertas
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

        # 3. Cooldown por tipo de alerta (anti-spam)
        post_cooldown = self._apply_cooldown(active_events)

        # 4. Supressão topológica (switch caiu → suprimir filhos)
        post_topology = self._apply_topology_suppression(post_cooldown)

        # 4b. Supressão por DependencyEngine (ping CRITICAL → suprimir filhos)
        post_topology = self._apply_dependency_suppression(post_topology)

        if not post_topology:
            return []

        # 5. Suprimir duplicados
        non_duplicate_events = []
        for event in post_topology:
            if self._suppressor.is_duplicate(event):
                self._metrics["alerts_suppressed"] += 1
                logger.debug("AlertEngine: evento duplicado suprimido: %s", event.type)
            else:
                non_duplicate_events.append(event)
                self._suppressor.mark_seen(event)

        if not non_duplicate_events:
            return []

        # 6. Agrupar eventos
        groups = self._grouper.group(non_duplicate_events)
        if len(groups) < len(non_duplicate_events):
            self._metrics["alerts_grouped"] += len(non_duplicate_events) - len(groups)

        # 7. Criar alertas por grupo
        alerts = []
        for group in groups:
            alert = self._create_alert(group)
            if alert:
                alerts.append(alert)
                self._metrics["alerts_total"] += 1
                # Registrar no cooldown tracker
                for ev in group:
                    key = f"{ev.host_id}:{ev.type}"
                    self._cooldown_tracker[key] = time.monotonic()
                # Marcar host como falho para supressão topológica
                for ev in group:
                    sev = ev.severity if isinstance(ev.severity, str) else ev.severity.value
                    if sev == EventSeverity.CRITICAL.value:
                        self._failed_hosts.add(str(ev.host_id))

        # 8. Notificar
        if self._channels:
            for alert in alerts:
                self._notifier.notify(alert, self._channels)

        return alerts

    def _apply_cooldown(self, events: list[Event]) -> list[Event]:
        """
        Filtra eventos que ainda estão em cooldown.
        Cooldown por chave host_id:event_type — evita spam do mesmo alerta.
        """
        now = time.monotonic()
        passed = []
        for event in events:
            key = f"{event.host_id}:{event.type}"
            last_fired = self._cooldown_tracker.get(key)
            if last_fired and (now - last_fired) < self._cooldown_seconds:
                self._metrics["alerts_cooldown_suppressed"] += 1
                logger.debug(
                    "AlertEngine: cooldown ativo para %s (%.0fs restantes)",
                    key, self._cooldown_seconds - (now - last_fired),
                )
            else:
                passed.append(event)
        return passed

    def _apply_dependency_suppression(self, events: list[Event]) -> list[Event]:
        """
        Supressão via DependencyEngine: se sensor pai (ping) está CRITICAL,
        suprimir eventos de sensores filhos do mesmo host.
        Fail-open: se DependencyEngine não tem cache para o host, permite.
        """
        if not self._dependency_engine:
            return events
        passed = []
        for event in events:
            host_id = str(event.host_id)
            sensor_id = str(getattr(event, 'sensor_id', event.host_id))
            try:
                if not self._dependency_engine.should_execute(sensor_id, host_id):
                    self._metrics["alerts_topology_suppressed"] += 1
                    logger.info(
                        "AlertEngine: supressão por DependencyEngine — sensor %s host %s suprimido",
                        sensor_id, host_id,
                    )
                else:
                    passed.append(event)
            except Exception as e:
                # Fail-open: exceção no DependencyEngine não bloqueia o alerta
                logger.warning("AlertEngine: DependencyEngine erro (fail-open): %s", e)
                passed.append(event)
        return passed

    def _apply_topology_suppression(self, events: list[Event]) -> list[Event]:
        """
        Supressão topológica: se o pai (switch/router) está em falha,
        suprimir alertas dos filhos (servidores conectados a ele).
        Evita cascata de alertas quando infraestrutura de rede cai.
        """
        if not self._topology_parents or not self._failed_hosts:
            return events

        passed = []
        for event in events:
            host_id = str(event.host_id)
            parent_id = self._topology_parents.get(host_id)
            if parent_id and parent_id in self._failed_hosts:
                self._metrics["alerts_topology_suppressed"] += 1
                logger.info(
                    "AlertEngine: supressão topológica — host %s suprimido (pai %s em falha)",
                    host_id, parent_id,
                )
            else:
                passed.append(event)
        return passed

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
    # Topologia (Smart Alerting)
    # ------------------------------------------------------------------

    def set_topology(self, parent_map: dict[str, str]) -> None:
        """
        Define mapa de topologia para supressão.
        parent_map: {child_host_id: parent_host_id}
        Ex: {"server-01": "switch-core", "server-02": "switch-core"}
        """
        self._topology_parents = parent_map
        logger.info("AlertEngine: topologia atualizada (%d relações)", len(parent_map))

    def mark_host_failed(self, host_id: str) -> None:
        """Marca host como em falha (ativa supressão dos filhos)."""
        self._failed_hosts.add(host_id)

    def mark_host_recovered(self, host_id: str) -> None:
        """Remove host da lista de falhas."""
        self._failed_hosts.discard(host_id)

    def set_cooldown(self, seconds: int) -> None:
        """Configura cooldown global em segundos."""
        self._cooldown_seconds = seconds

    # ------------------------------------------------------------------
    # Métricas
    # ------------------------------------------------------------------

    def get_metrics(self) -> dict:
        return dict(self._metrics)
