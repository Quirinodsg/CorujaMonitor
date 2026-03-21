"""
WMI Event Listener - Subscrições WMI para eventos críticos
Monitora: criação/parada de serviços, falhas de disco, eventos de segurança
Reconexão com backoff exponencial: 5s, 10s, 30s, 60s
"""
import logging
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)

BACKOFF_STEPS = [5, 10, 30, 60]

WMI_QUERIES = {
    "service_change": (
        "SELECT * FROM __InstanceModificationEvent WITHIN 5 "
        "WHERE TargetInstance ISA 'Win32_Service' "
        "AND TargetInstance.State != PreviousInstance.State"
    ),
    "disk_failure": (
        "SELECT * FROM Win32_VolumeChangeEvent WHERE EventType = 3"
    ),
    "security_event": (
        "SELECT * FROM __InstanceCreationEvent WITHIN 5 "
        "WHERE TargetInstance ISA 'Win32_NTLogEvent' "
        "AND TargetInstance.Logfile = 'Security' "
        "AND TargetInstance.EventType = 1"
    ),
}


class WMIEventListener:
    def __init__(self, callback: Callable, host: str = "localhost"):
        self.callback = callback
        self.host = host
        self._running = False
        self._threads = []

    def start(self):
        self._running = True
        for event_type, query in WMI_QUERIES.items():
            t = threading.Thread(
                target=self._listen_loop,
                args=(event_type, query),
                daemon=True,
                name=f"WMIEvent-{event_type}",
            )
            t.start()
            self._threads.append(t)
        logger.info(f"WMIEventListener iniciado para {self.host} ({len(WMI_QUERIES)} subscriptions)")

    def stop(self):
        self._running = False

    def _listen_loop(self, event_type: str, query: str):
        backoff_idx = 0
        while self._running:
            try:
                import wmi
                c = wmi.WMI(computer=self.host)
                watcher = c.watch_for(raw_wql=query)
                backoff_idx = 0  # reset após conexão bem-sucedida
                logger.info(f"WMIEventListener [{event_type}]: aguardando eventos")

                while self._running:
                    try:
                        event = watcher(timeout_ms=5000)
                        if event:
                            self._dispatch(event_type, event)
                    except wmi.x_wmi_timed_out:
                        continue

            except Exception as e:
                if not self._running:
                    break
                delay = BACKOFF_STEPS[min(backoff_idx, len(BACKOFF_STEPS) - 1)]
                logger.warning(f"WMIEventListener [{event_type}] erro: {e} — reconectando em {delay}s")
                backoff_idx += 1
                time.sleep(delay)

    def _dispatch(self, event_type: str, event):
        try:
            result = {
                "sensor_type": "wmi_event",
                "event_type": event_type,
                "host": self.host,
                "status": "critical",
                "value": 1.0,
                "unit": "event",
                "metadata": {},
                "timestamp": time.time(),
            }

            if event_type == "service_change":
                try:
                    target = event.TargetInstance
                    svc_name = getattr(target, "Name", None)
                    svc_state = getattr(target, "State", None)
                    svc_display = getattr(target, "DisplayName", svc_name)

                    is_running = svc_state == "Running"
                    result["value"] = 1.0 if is_running else 0.0
                    result["status"] = "ok" if is_running else "critical"
                    result["event_type"] = "service_recovered" if is_running else "service_down"
                    result["metadata"] = {
                        "service_name": svc_name,
                        "display_name": svc_display,
                        "state": svc_state,
                    }
                    logger.info(
                        f"WMIEvent service_change: {svc_name} → {svc_state} "
                        f"({'recovered' if is_running else 'down'})"
                    )
                except Exception as parse_err:
                    logger.warning(f"WMIEventListener: falha ao parsear TargetInstance: {parse_err}")
                    result["metadata"] = {"raw": str(event)}
            else:
                result["metadata"] = {"raw": str(event)}

            self.callback(result)
        except Exception as e:
            logger.error(f"WMIEventListener dispatch erro: {e}")
