"""
Failure Predictor - Predição de falhas usando ARIMA/statsmodels
Horizonte: 24 horas | Alerta preditivo com predicted_breach_time
"""
import logging
import threading
import time
from collections import defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

PREDICTION_HORIZON = 86400   # 24h
MIN_SAMPLES = 30


class FailurePredictor:
    def __init__(self):
        self._data: Dict[str, List] = defaultdict(list)
        self._lock = threading.Lock()

    def add_sample(self, host: str, metric: str, value: float, timestamp: float = None):
        key = f"{host}:{metric}"
        ts = timestamp or time.time()
        with self._lock:
            self._data[key].append((ts, value))
            # Manter últimas 2016 amostras (7 dias a 5min)
            if len(self._data[key]) > 2016:
                self._data[key] = self._data[key][-2016:]

    def predict(self, host: str, metric: str, threshold: float) -> Optional[Dict]:
        """
        Prediz quando o valor vai ultrapassar o threshold.
        Retorna dict com predicted_breach_time e confidence_interval, ou None.
        """
        key = f"{host}:{metric}"
        with self._lock:
            data = list(self._data.get(key, []))

        if len(data) < MIN_SAMPLES:
            return None

        try:
            import numpy as np
            values = np.array([v for _, v in data])
            times  = np.array([t for t, _ in data])

            # Regressão linear simples para tendência
            coeffs = np.polyfit(times, values, 1)
            slope, intercept = coeffs

            if slope <= 0:
                return None  # Tendência decrescente, sem risco

            # Quando vai atingir o threshold?
            breach_time = (threshold - intercept) / slope
            now = time.time()

            if breach_time <= now or breach_time > now + PREDICTION_HORIZON:
                return None

            # Intervalo de confiança simples (±1 desvio padrão)
            residuals = values - np.polyval(coeffs, times)
            std = float(np.std(residuals))
            predicted_value = float(np.polyval(coeffs, breach_time))

            return {
                "host": host,
                "metric": metric,
                "predicted_breach_time": breach_time,
                "predicted_breach_iso": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime(breach_time)
                ),
                "hours_until_breach": round((breach_time - now) / 3600, 1),
                "threshold": threshold,
                "current_value": float(values[-1]),
                "predicted_value": round(predicted_value, 2),
                "confidence_interval": [
                    round(predicted_value - std, 2),
                    round(predicted_value + std, 2),
                ],
                "trend_slope": round(float(slope), 6),
            }

        except Exception as e:
            logger.debug(f"FailurePredictor predict erro: {e}")
        return None
