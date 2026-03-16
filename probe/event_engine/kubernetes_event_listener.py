"""
Kubernetes Event Listener - Consome stream de eventos da API K8s
Monitora: OOMKilling, BackOff, Failed, Evicted
Reconexão com backoff exponencial: 5s, 10s, 30s, 60s
"""
import logging
import threading
import time
from typing import Callable

logger = logging.getLogger(__name__)

BACKOFF_STEPS = [5, 10, 30, 60]
WATCHED_REASONS = {"OOMKilling", "BackOff", "Failed", "Evicted"}


class KubernetesEventListener:
    def __init__(self, callback: Callable):
        self.callback = callback
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="K8sEventListener"
        )
        self._thread.start()
        logger.info("KubernetesEventListener iniciado")

    def stop(self):
        self._running = False

    def _listen_loop(self):
        backoff_idx = 0
        while self._running:
            try:
                from kubernetes import client as k8s_client, config as k8s_config, watch
                try:
                    k8s_config.load_incluster_config()
                except Exception:
                    k8s_config.load_kube_config()

                v1 = k8s_client.CoreV1Api()
                w = watch.Watch()
                backoff_idx = 0
                logger.info("KubernetesEventListener: conectado ao cluster")

                for event in w.stream(v1.list_event_for_all_namespaces, timeout_seconds=60):
                    if not self._running:
                        w.stop()
                        break
                    obj = event.get("object")
                    if obj and obj.reason in WATCHED_REASONS:
                        self._dispatch(obj)

            except Exception as e:
                if not self._running:
                    break
                delay = BACKOFF_STEPS[min(backoff_idx, len(BACKOFF_STEPS) - 1)]
                logger.warning(f"KubernetesEventListener erro: {e} — reconectando em {delay}s")
                backoff_idx += 1
                time.sleep(delay)

    def _dispatch(self, obj):
        try:
            result = {
                "sensor_type": "kubernetes_event",
                "event_type": obj.reason,
                "host": getattr(obj.involved_object, "name", "unknown"),
                "status": "critical",
                "value": 1.0,
                "unit": "event",
                "metadata": {
                    "namespace": obj.metadata.namespace,
                    "message": obj.message,
                    "reason": obj.reason,
                },
                "timestamp": time.time(),
            }
            self.callback(result)
        except Exception as e:
            logger.error(f"KubernetesEventListener dispatch erro: {e}")
