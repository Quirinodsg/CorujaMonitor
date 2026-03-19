"""
ProbeManager — Distributed Probes Manager — Coruja Monitor v3.0
Módulo standalone (sem dependência de FastAPI) para uso em testes e workers.
"""
import logging
import time
import threading
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from core.spec.models import Host
from core.spec.enums import ProbeStatus

logger = logging.getLogger(__name__)

# Thresholds de heartbeat (segundos)
HEARTBEAT_ONLINE_THRESHOLD = 90
HEARTBEAT_DEGRADED_THRESHOLD = 120
MAX_LOAD = 0.80
FAILOVER_TIMEOUT = 120
RESTORE_TIMEOUT = 300


@dataclass
class ProbeState:
    probe_id: UUID
    name: str
    probe_type: str  # "windows" | "linux" | "snmp"
    subnet: str = ""
    capacity: int = 100
    assigned_hosts: list = field(default_factory=list)
    last_heartbeat: float = field(default_factory=time.time)
    status: str = ProbeStatus.ONLINE.value
    original_hosts: list = field(default_factory=list)

    @property
    def load(self) -> float:
        if self.capacity == 0:
            return 1.0
        return len(self.assigned_hosts) / self.capacity

    @property
    def host_count(self) -> int:
        return len(self.assigned_hosts)


class ProbeManager:
    """
    Gerencia distribuição de hosts entre ProbeNodes.
    Thread-safe via lock interno.
    """

    def __init__(self):
        self._probes: dict[UUID, ProbeState] = {}
        self._host_to_probe: dict[UUID, UUID] = {}
        self._lock = threading.RLock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False

    def register_probe(self, probe_id: UUID, name: str, probe_type: str,
                       subnet: str = "", capacity: int = 100) -> ProbeState:
        with self._lock:
            state = ProbeState(
                probe_id=probe_id,
                name=name,
                probe_type=probe_type,
                subnet=subnet,
                capacity=capacity,
            )
            self._probes[probe_id] = state
            logger.info(f"ProbeManager: probe registrada {name} ({probe_id})")
            return state

    def heartbeat(self, probe_id: UUID):
        with self._lock:
            if probe_id in self._probes:
                self._probes[probe_id].last_heartbeat = time.time()
                self._probes[probe_id].status = ProbeStatus.ONLINE.value

    def assign_host(self, host: Host) -> Optional[UUID]:
        """
        Atribui host a uma probe via weighted round-robin.
        Preferência: mesma subnet, load < 80%.
        """
        with self._lock:
            host_id = host.id
            if host_id in self._host_to_probe:
                return self._host_to_probe[host_id]

            probe = self._select_probe(host)
            if probe is None:
                logger.warning(f"ProbeManager: nenhuma probe disponível para host {host_id}")
                return None

            probe.assigned_hosts.append(host_id)
            self._host_to_probe[host_id] = probe.probe_id
            return probe.probe_id

    def _select_probe(self, host: Host) -> Optional[ProbeState]:
        host_ip = str(host.ip_address) if host.ip_address else ""
        host_subnet = ".".join(host_ip.split(".")[:3]) if host_ip else ""

        available = [
            p for p in self._probes.values()
            if p.status != ProbeStatus.OFFLINE.value and p.load < MAX_LOAD
        ]
        if not available:
            return None

        subnet_match = [p for p in available if p.subnet and host_subnet.startswith(p.subnet)]
        candidates = subnet_match if subnet_match else available
        return min(candidates, key=lambda p: p.load)

    def unassign_host(self, host_id: UUID):
        with self._lock:
            probe_id = self._host_to_probe.pop(host_id, None)
            if probe_id and probe_id in self._probes:
                probe = self._probes[probe_id]
                if host_id in probe.assigned_hosts:
                    probe.assigned_hosts.remove(host_id)

    def handle_probe_offline(self, probe_id: UUID):
        with self._lock:
            if probe_id not in self._probes:
                return

            probe = self._probes[probe_id]
            probe.status = ProbeStatus.OFFLINE.value
            hosts_to_migrate = list(probe.assigned_hosts)
            probe.original_hosts = list(hosts_to_migrate)
            probe.assigned_hosts.clear()

            logger.warning(f"ProbeManager: probe {probe.name} offline, migrando {len(hosts_to_migrate)} hosts")

            migrated = 0
            for host_id in hosts_to_migrate:
                self._host_to_probe.pop(host_id, None)
                alt = self._select_probe_for_failover(probe.probe_type, probe_id)
                if alt:
                    alt.assigned_hosts.append(host_id)
                    self._host_to_probe[host_id] = alt.probe_id
                    migrated += 1

            logger.info(f"ProbeManager: failover concluído — {migrated}/{len(hosts_to_migrate)} migrados")

    def _select_probe_for_failover(self, probe_type: str, exclude_id: UUID) -> Optional[ProbeState]:
        candidates = [
            p for p in self._probes.values()
            if p.probe_id != exclude_id
            and p.status != ProbeStatus.OFFLINE.value
            and p.load < MAX_LOAD
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda p: p.load)

    def restore_probe(self, probe_id: UUID):
        with self._lock:
            if probe_id not in self._probes:
                return

            probe = self._probes[probe_id]
            probe.status = ProbeStatus.ONLINE.value
            probe.last_heartbeat = time.time()
            hosts_to_restore = list(probe.original_hosts)
            probe.original_hosts.clear()

        for host_id in hosts_to_restore:
            with self._lock:
                current_probe_id = self._host_to_probe.get(host_id)
                if current_probe_id and current_probe_id != probe_id:
                    temp_probe = self._probes.get(current_probe_id)
                    if temp_probe and host_id in temp_probe.assigned_hosts:
                        temp_probe.assigned_hosts.remove(host_id)
                probe.assigned_hosts.append(host_id)
                self._host_to_probe[host_id] = probe_id

        logger.info(f"ProbeManager: probe {probe.name} restaurada com {len(hosts_to_restore)} hosts")

    def update_probe_statuses(self):
        now = time.time()
        with self._lock:
            for probe in self._probes.values():
                elapsed = now - probe.last_heartbeat
                if elapsed < HEARTBEAT_ONLINE_THRESHOLD:
                    probe.status = ProbeStatus.ONLINE.value
                elif elapsed < HEARTBEAT_DEGRADED_THRESHOLD:
                    probe.status = ProbeStatus.DEGRADED.value
                else:
                    if probe.status != ProbeStatus.OFFLINE.value:
                        probe.status = ProbeStatus.OFFLINE.value
                        threading.Thread(
                            target=self.handle_probe_offline,
                            args=(probe.probe_id,),
                            daemon=True,
                        ).start()

    def start_monitor(self, interval: float = 30.0):
        if self._running:
            return
        self._running = True

        def _loop():
            while self._running:
                try:
                    self.update_probe_statuses()
                except Exception as e:
                    logger.error(f"ProbeManager monitor: {e}")
                time.sleep(interval)

        self._monitor_thread = threading.Thread(target=_loop, daemon=True, name="ProbeMonitor")
        self._monitor_thread.start()

    def stop_monitor(self):
        self._running = False

    def get_status(self) -> dict:
        with self._lock:
            return {
                "probes": [
                    {
                        "probe_id": str(p.probe_id),
                        "name": p.name,
                        "type": p.probe_type,
                        "status": p.status,
                        "hosts_monitored": p.host_count,
                        "capacity": p.capacity,
                        "load": round(p.load, 3),
                        "last_heartbeat_seconds_ago": round(time.time() - p.last_heartbeat, 1),
                    }
                    for p in self._probes.values()
                ],
                "total_hosts_assigned": len(self._host_to_probe),
                "total_probes": len(self._probes),
            }

    def get_host_probe(self, host_id: UUID) -> Optional[UUID]:
        with self._lock:
            return self._host_to_probe.get(host_id)

    def invariant_check(self) -> bool:
        """Verifica que cada host está atribuído a exatamente uma probe ativa."""
        with self._lock:
            for host_id, probe_id in self._host_to_probe.items():
                probe = self._probes.get(probe_id)
                if probe is None:
                    return False
                if host_id not in probe.assigned_hosts:
                    return False
                if probe.status == ProbeStatus.OFFLINE.value:
                    return False
            return True
