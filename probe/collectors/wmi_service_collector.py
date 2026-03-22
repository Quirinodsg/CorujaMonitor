"""
WMI Service Collector — coleta todos os serviços com StartMode=Auto da máquina local.
Usa wmi nativo (disponível apenas em Windows).
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class WMIServiceCollector:
    """Coleta serviços Windows (StartMode=Auto) via WMI local."""

    def collect(self) -> List[Dict[str, Any]]:
        try:
            import wmi
            c = wmi.WMI()
            services = c.Win32_Service(StartMode="Auto")
        except Exception as e:
            logger.warning(f"WMIServiceCollector: WMI não disponível — {e}")
            return self._fallback_collect()

        metrics = []
        for svc in services:
            try:
                is_running = svc.State == "Running"
                metrics.append({
                    "type": "service",
                    "name": f"Service {svc.Name}",
                    "value": 1 if is_running else 0,
                    "unit": "state",
                    "status": "ok" if is_running else "critical",
                    "metadata": {
                        "service_name": svc.Name,
                        "display_name": svc.DisplayName,
                        "state": svc.State,
                        "start_mode": svc.StartMode,
                        "collection_method": "wmi_local",
                    },
                })
            except Exception:
                continue

        logger.info(f"WMIServiceCollector: {len(metrics)} serviços coletados")
        return metrics

    def _fallback_collect(self) -> List[Dict[str, Any]]:
        """Fallback via subprocess sc query (sem WMI)"""
        import subprocess
        metrics = []
        try:
            result = subprocess.run(
                ["sc", "query", "type=", "service", "state=", "all"],
                capture_output=True, text=True, timeout=10
            )
            current_name = None
            current_state = None
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("SERVICE_NAME:"):
                    current_name = line.split(":", 1)[1].strip()
                elif line.startswith("STATE") and current_name:
                    current_state = "Running" if "RUNNING" in line else "Stopped"
                    is_running = current_state == "Running"
                    metrics.append({
                        "type": "service",
                        "name": f"Service {current_name}",
                        "value": 1 if is_running else 0,
                        "unit": "state",
                        "status": "ok" if is_running else "critical",
                        "metadata": {
                            "service_name": current_name,
                            "display_name": current_name,
                            "state": current_state,
                            "start_mode": "Auto",
                            "collection_method": "sc_query",
                        },
                    })
                    current_name = None
        except Exception as e:
            logger.error(f"WMIServiceCollector fallback error: {e}")
        return metrics
