"""
Anomaly Detector — IsolationForest + baseline automático + tendências + previsão de capacidade
Janela de treinamento: 7 dias | Retreinamento: a cada 24h
"""
import logging
import threading
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

RETRAIN_INTERVAL = 86400      # 24h
TRAINING_WINDOW  = 7 * 86400  # 7 dias
MIN_SAMPLES      = 50
TREND_MIN_SAMPLES = 10


class AnomalyDetector:
    def __init__(self):
        self._models: Dict[str, object] = {}
        self._baselines: Dict[str, dict] = {}   # baseline automático por chave
        self._data: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ─── Ciclo de vida ────────────────────────────────────────────

    def start(self):
        self._running = True
        self._thread = threading.Thread(
            target=self._retrain_loop, daemon=True, name="AnomalyDetector"
        )
        self._thread.start()
        logger.info("AnomalyDetector iniciado")

    def stop(self):
        self._running = False

    # ─── Ingestão de dados ────────────────────────────────────────

    def add_sample(self, host: str, metric: str, value: float, timestamp: float = None):
        key = f"{host}:{metric}"
        ts = timestamp or time.time()
        cutoff = ts - TRAINING_WINDOW
        with self._lock:
            self._data[key].append((ts, value))
            self._data[key] = [(t, v) for t, v in self._data[key] if t >= cutoff]

    # ─── Detecção de anomalia ─────────────────────────────────────

    def detect(self, host: str, metric: str, value: float) -> Optional[dict]:
        key = f"{host}:{metric}"
        with self._lock:
            model = self._models.get(key)
            data = self._data.get(key, [])
            baseline = self._baselines.get(key)

        if model is None or len(data) < MIN_SAMPLES:
            return None

        try:
            import numpy as np
            X = np.array([[value]])
            score = model.decision_function(X)[0]
            prediction = model.predict(X)[0]

            if prediction == -1:
                values = [v for _, v in data]
                result = {
                    "host": host,
                    "metric": metric,
                    "anomaly_score": round(float(score), 4),
                    "affected_metric": metric,
                    "observed_value": value,
                    "expected_range": [round(float(min(values)), 2), round(float(max(values)), 2)],
                    "confidence_level": round(min(abs(score) * 10, 1.0), 3),
                }
                if baseline:
                    result["baseline"] = baseline
                return result
        except Exception as e:
            logger.debug(f"AnomalyDetector detect erro: {e}")
        return None

    # ─── Baseline automático ──────────────────────────────────────

    def get_baseline(self, host: str, metric: str) -> Optional[dict]:
        """Retorna baseline calculado automaticamente (média, p95, desvio padrão)."""
        key = f"{host}:{metric}"
        with self._lock:
            return self._baselines.get(key)

    def _compute_baseline(self, key: str, data: list) -> dict:
        try:
            values = sorted([v for _, v in data])
            n = len(values)
            mean = sum(values) / n
            variance = sum((v - mean) ** 2 for v in values) / n
            std = variance ** 0.5

            def percentile(p):
                idx = (p / 100.0) * (n - 1)
                lo, hi = int(idx), min(int(idx) + 1, n - 1)
                return values[lo] + (values[hi] - values[lo]) * (idx - lo)

            return {
                "mean": round(mean, 2),
                "std": round(std, 2),
                "p50": round(percentile(50), 2),
                "p95": round(percentile(95), 2),
                "p99": round(percentile(99), 2),
                "min": round(values[0], 2),
                "max": round(values[-1], 2),
                "samples": n,
                "computed_at": time.time(),
            }
        except Exception as e:
            logger.debug(f"Baseline compute erro [{key}]: {e}")
            return {}

    # ─── Detecção de tendências ───────────────────────────────────

    def detect_trend(self, host: str, metric: str) -> Optional[dict]:
        """
        Detecta tendência linear nos dados recentes.
        Retorna slope, direção e previsão para 1h/6h/24h.
        Funciona com ou sem numpy.
        """
        key = f"{host}:{metric}"
        with self._lock:
            data = list(self._data.get(key, []))

        if len(data) < TREND_MIN_SAMPLES:
            return None

        try:
            times = [t for t, _ in data]
            values = [v for _, v in data]

            # Normalizar tempo para horas
            t0 = times[0]
            t_hours = [(t - t0) / 3600.0 for t in times]

            # Regressão linear simples (sem numpy)
            n = len(t_hours)
            sum_x = sum(t_hours)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(t_hours, values))
            sum_x2 = sum(x * x for x in t_hours)
            denom = n * sum_x2 - sum_x * sum_x
            if denom == 0:
                slope = 0.0
                intercept = sum_y / n
            else:
                slope = (n * sum_xy - sum_x * sum_y) / denom
                intercept = (sum_y - slope * sum_x) / n

            # Previsões
            t_now = (time.time() - t0) / 3600.0
            pred_1h  = intercept + slope * (t_now + 1)
            pred_6h  = intercept + slope * (t_now + 6)
            pred_24h = intercept + slope * (t_now + 24)

            direction = "stable"
            if slope > 0.5:
                direction = "increasing"
            elif slope < -0.5:
                direction = "decreasing"

            return {
                "host": host,
                "metric": metric,
                "slope_per_hour": round(slope, 4),
                "direction": direction,
                "current_value": round(float(values[-1]), 2),
                "predicted_1h": round(pred_1h, 2),
                "predicted_6h": round(pred_6h, 2),
                "predicted_24h": round(pred_24h, 2),
                "samples": len(data),
            }
        except Exception as e:
            logger.debug(f"Trend detect erro [{key}]: {e}")
            return None

    # ─── Previsão de capacidade ───────────────────────────────────

    def predict_capacity(self, host: str, metric: str, threshold: float = 90.0) -> Optional[dict]:
        """
        Prevê quando o valor atingirá o threshold (ex: disco 90%).
        Usa regressão linear. Retorna horas até breach ou None se tendência não aponta para isso.
        """
        trend = self.detect_trend(host, metric)
        if not trend:
            return None

        slope = trend["slope_per_hour"]
        current = trend["current_value"]

        if slope <= 0:
            return None  # Não está crescendo

        hours_until = (threshold - current) / slope
        if hours_until <= 0:
            return None  # Já passou do threshold

        breach_time = time.time() + hours_until * 3600

        return {
            "host": host,
            "metric": metric,
            "threshold": threshold,
            "current_value": current,
            "slope_per_hour": slope,
            "hours_until_breach": round(hours_until, 1),
            "predicted_breach_time": breach_time,
            "predicted_breach_iso": _iso(breach_time),
            "confidence": _trend_confidence(trend["samples"]),
        }

    # ─── Retreinamento ────────────────────────────────────────────

    def _retrain_loop(self):
        while self._running:
            self._retrain_all()
            time.sleep(RETRAIN_INTERVAL)

    def _retrain_all(self):
        with self._lock:
            keys = list(self._data.keys())

        for key in keys:
            with self._lock:
                data = list(self._data.get(key, []))
            if len(data) < MIN_SAMPLES:
                continue

            # Baseline sempre calculado (sem dependência de sklearn)
            baseline = self._compute_baseline(key, data)
            with self._lock:
                self._baselines[key] = baseline

            # Modelo IsolationForest (requer sklearn)
            try:
                from sklearn.ensemble import IsolationForest
                import numpy as np
                X = np.array([[v] for _, v in data])
                model = IsolationForest(contamination=0.05, random_state=42)
                model.fit(X)
                with self._lock:
                    self._models[key] = model
                logger.debug(f"AnomalyDetector: retreinado [{key}] ({len(data)} amostras)")
            except ImportError:
                logger.debug("AnomalyDetector: scikit-learn não instalado, apenas baseline calculado")
            except Exception as e:
                logger.error(f"AnomalyDetector retrain erro [{key}]: {e}")


# ─── Helpers ──────────────────────────────────────────────────────

def _iso(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _trend_confidence(samples: int) -> float:
    """Confiança cresce com número de amostras, máximo 0.95."""
    return round(min(0.95, samples / 200.0), 2)
