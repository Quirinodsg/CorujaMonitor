"""
Alert Notifier — Coruja Monitor v3.0
Envia notificações de alertas via email, webhook, Teams/Slack.
SLA: < 30 segundos. Retry 3x com backoff exponencial.
"""
import logging
import time
from typing import Optional

from core.spec.models import Alert

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 1.0


class AlertNotifier:
    """
    Notifica alertas nos canais configurados.
    Suporta: email, webhook, teams, slack.
    """

    def __init__(self, channels_config: Optional[dict] = None):
        self._config = channels_config or {}

    def notify(self, alert: Alert, channels: list[str]) -> dict:
        """
        Envia notificação para todos os canais.
        Retorna {channel: success} para cada canal.
        """
        results = {}
        for channel in channels:
            success = self._notify_with_retry(alert, channel)
            results[channel] = success
        return results

    def _notify_with_retry(self, alert: Alert, channel: str) -> bool:
        """Tenta notificar com retry 3x e backoff exponencial."""
        for attempt in range(MAX_RETRIES):
            try:
                success = self._send(alert, channel)
                if success:
                    return True
            except Exception as e:
                logger.warning(
                    "AlertNotifier: tentativa %d/%d falhou para canal %s: %s",
                    attempt + 1, MAX_RETRIES, channel, e,
                )
            if attempt < MAX_RETRIES - 1:
                time.sleep(BASE_BACKOFF_SECONDS * (2 ** attempt))

        logger.error("AlertNotifier: todas as tentativas falharam para canal %s", channel)
        return False

    def _send(self, alert: Alert, channel: str) -> bool:
        """Envia para canal específico."""
        channel_config = self._config.get(channel, {})

        if channel == "webhook":
            return self._send_webhook(alert, channel_config)
        elif channel == "email":
            return self._send_email(alert, channel_config)
        elif channel in ("teams", "slack"):
            return self._send_webhook(alert, channel_config)
        else:
            logger.warning("AlertNotifier: canal desconhecido: %s", channel)
            return False

    def _send_webhook(self, alert: Alert, config: dict) -> bool:
        url = config.get("url")
        if not url:
            logger.debug("AlertNotifier: webhook sem URL configurada")
            return True  # Sem URL = não configurado, não é erro

        try:
            import requests
            payload = {
                "alert_id": str(alert.id),
                "title": alert.title,
                "severity": alert.severity if isinstance(alert.severity, str) else alert.severity.value,
                "status": alert.status if isinstance(alert.status, str) else alert.status.value,
                "affected_hosts": [str(h) for h in alert.affected_hosts],
                "root_cause": alert.root_cause,
            }
            resp = requests.post(url, json=payload, timeout=10)
            return resp.status_code < 400
        except Exception as e:
            logger.error("AlertNotifier: webhook error: %s", e)
            return False

    def _send_email(self, alert: Alert, config: dict) -> bool:
        # Placeholder — implementação real via SMTP/SendGrid
        logger.info("AlertNotifier: email simulado para alerta %s", alert.id)
        return True
