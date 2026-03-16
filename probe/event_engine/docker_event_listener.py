"""
Docker Event Listener - Consome stream de eventos da Docker API
Monitora: die, oom, health_status
Reconexão com backoff exponencial: 5s, 10s, 30s, 60s
"""
import logging
import threading
import time
from typing import Callable

logger = logging.getLogger(__name__)

BACKOFF_STEPS = [5, 10, 30, 60]
WATCHED_EVENTS = {"die", "oom", "health_status"}


class DockerEventListener:
    def __init__(self, callback: Callable):
        self.callback = callback
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="DockerEventListener"
        )
        self._thread.start()
        logger.info("DockerEventListener iniciado")

    def stop(self):
        self._running = False

    def _listen_loop(self):
        backoff_idx = 0
        while self._running:
            try:
                import docker
                client = docker.from_env()
                backoff_idx = 0
                logger.info("DockerEventListener: conectado ao Docker daemon")

                for event in client.events(decode=True, filters={"type": "container"}):
                    if not self._running:
                        break
                    action = event.get("Action", "")
                    if action in WATCHED_EVENTS:
                        self._dispatch(event)

            except Exception as e:
                if not self._running:
                    break
                delay = BACKOFF_STEPS[min(backoff_idx, len(BACKOFF_STEPS) - 1)]
                logger.warning(f"DockerEventListener erro: {e} — reconectando em {delay}s")
                backoff_idx += 1
                time.sleep(delay)

    def _dispatch(self, event: dict):
        try:
            action = event.get("Action", "unknown")
            container = event.get("Actor", {}).get("Attributes", {}).get("name", "unknown")
            result = {
                "sensor_type": "docker_event",
                "event_type": action,
                "host": container,
                "status": "critical" if action in ("die", "oom") else "warning",
                "value": 1.0,
                "unit": "event",
                "metadata": event,
                "timestamp": time.time(),
            }
            self.callback(result)
        except Exception as e:
            logger.error(f"DockerEventListener dispatch erro: {e}")
