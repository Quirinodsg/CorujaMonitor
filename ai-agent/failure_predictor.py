"""
Failure Predictor v3.5 — Coruja Monitor Enterprise
Predição proativa de falhas com horizonte 24h.
Usa regressão linear + detecção de tendência por tipo de sensor.
Exemplos: "Disco ficará cheio em 6 horas", "CPU atingirá 95% em 3 horas"
"""
import logging
import threading
import time
from collections import defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

PREDICTION_HORIZON = 86400   # 24h em segundos
MIN_SAMPLES = 30

# Thresholds padrão por tipo de sensor (se não informado)
DEFAULT_THRESHOLDS = {
    "disk": 90.0,
    "cpu": 95.0,
    "memory": 90.0,
    "network": 95.0,
}

# Mensagens de predição humanizadas por tipo
PREDICTION_MESSAGES = {
    "disk": "Disco ficará cheio",
    "cpu": "CPU atingirá nível crítico",
    "memory": "Memória atingirá nível crítico",
    "network": "Rede atingirá saturação",
}


class FailurePredictor:
    """
    Preditor de falhas proativo.
    - Mantém histórico de amostras por host:metric
    - Calcula tendência via regressão linear
    - Prediz quando threshold será atingido (horizonte 24h)
    - Gera alertas preditivos com mensagem humanizada
    """

    def __init__(self):
        self._data: Dict[str, List] = defaultdict(list)
        self._lock = threading.Lock()
        # Cache de predições ativas: {key: prediction_dict}
        self._active_predictions: Dict[str, dict] = {}

    def add_sample(self, host: str, metric: str, value: float, timestamp: float = None):
        """Adiciona amostra de métrica para um host."""
        key = f"{host}:{metric}"
        ts = timestamp or time.time()
        with self._lock:
            self._data[key].append((ts, value))
            # Manter últimas 2016 amostras (7 dias a 5min)
            if len(self._data[key]) > 2016:
                self._data[key] = self._data[key][-2016:]

    def predict(self, host: str, metric: str, threshold: float = None) -> Optional[Dict]:
        """
        Prediz quando o valor vai ultrapassar o threshold.
        Retorna dict com predicted_breach_time, hours_until_breach e mensagem humanizada.
        """
        key = f"{host}:{metric}"
        # Usar threshold padrão por tipo de sensor se não informado
        sensor_type = metric.split("_")[0] if "_" in metric else metric
        if threshold is None:
            threshold = DEFAULT_THRESHOLDS.get(sensor_type, 90.0)

        with self._lock:
            data = list(self._data.get(key, []))

        if len(data) < MIN_SAMPLES:
            return None

        try:
            import numpy as np
            values = np.array([v for _, v in data])
            times  = np.array([t for t, _ in data])

            # Regressão linear para tendência
            coeffs = np.polyfit(times, values, 1)
            slope, intercept = coeffs

            if slope <= 0:
                # Tendência decrescente — sem risco de breach
                self._active_predictions.pop(key, None)
                return None

            # Quando vai atingir o threshold?
            breach_time = (threshold - intercept) / slope
            now = time.time()

            if breach_time <= now or breach_time > now + PREDICTION_HORIZON:
                self._active_predictions.pop(key, None)
                return None

            hours_until = round((breach_time - now) / 3600, 1)

            # Intervalo de confiança (±1 desvio padrão)
            residuals = values - np.polyval(coeffs, times)
            std = float(np.std(residuals))
            predicted_value = float(np.polyval(coeffs, breach_time))

            # Calcular R² para qualidade da predição
            ss_res = float(np.sum(residuals ** 2))
            ss_tot = float(np.sum((values - np.mean(values)) ** 2))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

            # Mensagem humanizada
            base_msg = PREDICTION_MESSAGES.get(sensor_type, f"{metric} atingirá threshold")
            if hours_until < 1:
                time_str = f"{int(hours_until * 60)} minutos"
            else:
                time_str = f"{hours_until:.1f} horas"
            human_message = f"{base_msg} em {time_str} (host: {host})"

            # Severidade baseada no tempo restante
            if hours_until <= 2:
                severity = "critical"
            elif hours_until <= 6:
                severity = "warning"
            else:
                severity = "info"

            prediction = {
                "host": host,
                "metric": metric,
                "sensor_type": sensor_type,
                "predicted_breach_time": breach_time,
                "predicted_breach_iso": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime(breach_time)
                ),
                "hours_until_breach": hours_until,
                "threshold": threshold,
                "current_value": float(values[-1]),
                "predicted_value": round(predicted_value, 2),
                "confidence_interval": [
                    round(predicted_value - std, 2),
                    round(predicted_value + std, 2),
                ],
                "trend_slope": round(float(slope), 6),
                "r_squared": round(r_squared, 3),
                "sample_count": len(data),
                "severity": severity,
                "message": human_message,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            }

            self._active_predictions[key] = prediction
            return prediction

        except Exception as e:
            logger.debug("FailurePredictor predict erro: %s", e)
        return None

    def predict_all(self) -> List[Dict]:
        """Retorna todas as predições ativas (com breach previsto nas próximas 24h)."""
        results = []
        with self._lock:
            keys = list(self._data.keys())

        for key in keys:
            host, metric = key.split(":", 1)
            pred = self.predict(host, metric)
            if pred:
                results.append(pred)

        # Ordenar por urgência (menor tempo primeiro)
        results.sort(key=lambda x: x["hours_until_breach"])
        return results

    def get_active_predictions(self) -> List[Dict]:
        """Retorna cache de predições ativas sem recalcular."""
        return list(self._active_predictions.values())

    def get_host_predictions(self, host: str) -> List[Dict]:
        """Retorna predições para um host específico."""
        return [p for p in self.predict_all() if p["host"] == host]
