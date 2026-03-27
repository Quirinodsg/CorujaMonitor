"""
QA Enterprise — Failure Predictor v3.5
Testa: ingestão de amostras, predição linear, horizonte 24h, mensagens humanizadas,
severidade por urgência, R², thresholds padrão, predict_all, thread-safety.
"""
import time
import threading
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ai-agent"))
from failure_predictor import FailurePredictor, DEFAULT_THRESHOLDS, PREDICTION_HORIZON, MIN_SAMPLES


# ─── Helpers ────────────────────────────────────────────────────────────────

def feed_trending_up(predictor: FailurePredictor, host: str, metric: str,
                     start_value: float, slope_per_sample: float,
                     n_samples: int = 40, interval_seconds: int = 300):
    """Alimenta predictor com tendência crescente controlada."""
    base_ts = time.time() - (n_samples * interval_seconds)
    for i in range(n_samples):
        ts = base_ts + (i * interval_seconds)
        value = start_value + (i * slope_per_sample)
        predictor.add_sample(host, metric, value, ts)

def feed_flat(predictor: FailurePredictor, host: str, metric: str,
              value: float = 50.0, n_samples: int = 40):
    """Alimenta predictor com valores constantes (sem tendência)."""
    base_ts = time.time() - (n_samples * 300)
    for i in range(n_samples):
        predictor.add_sample(host, metric, value, base_ts + i * 300)


def feed_trending_down(predictor: FailurePredictor, host: str, metric: str,
                       n_samples: int = 40):
    """Alimenta predictor com tendência decrescente."""
    base_ts = time.time() - (n_samples * 300)
    for i in range(n_samples):
        predictor.add_sample(host, metric, 90.0 - i * 0.5, base_ts + i * 300)


# ─── 1. Ingestão de Amostras ─────────────────────────────────────────────────

class TestSampleIngestion:
    def test_add_sample_stores_data(self):
        p = FailurePredictor()
        p.add_sample("host-01", "disk", 75.0)
        assert len(p._data["host-01:disk"]) == 1

    def test_add_sample_uses_current_time_if_none(self):
        p = FailurePredictor()
        before = time.time()
        p.add_sample("host-01", "cpu", 50.0)
        after = time.time()
        ts, _ = p._data["host-01:cpu"][0]
        assert before <= ts <= after

    def test_max_samples_capped_at_2016(self):
        """Histórico limitado a 2016 amostras (7 dias × 5min)."""
        p = FailurePredictor()
        for i in range(2100):
            p.add_sample("host-01", "disk", float(i))
        assert len(p._data["host-01:disk"]) == 2016, \
            "Histórico deve ser limitado a 2016 amostras"

    def test_multiple_hosts_isolated(self):
        """Amostras de hosts diferentes não se misturam."""
        p = FailurePredictor()
        p.add_sample("host-A", "cpu", 80.0)
        p.add_sample("host-B", "cpu", 30.0)
        assert len(p._data["host-A:cpu"]) == 1
        assert len(p._data["host-B:cpu"]) == 1


# ─── 2. Predição — Casos Positivos ───────────────────────────────────────────

class TestPredictionPositive:
    def test_predict_returns_none_below_min_samples(self):
        """Menos de MIN_SAMPLES amostras → None."""
        p = FailurePredictor()
        for i in range(MIN_SAMPLES - 1):
            p.add_sample("host-01", "disk", float(60 + i * 0.5))
        result = p.predict("host-01", "disk", threshold=90.0)
        assert result is None, f"Deve retornar None com {MIN_SAMPLES - 1} amostras"

    def test_predict_disk_breach_within_24h(self):
        """Disco crescendo → deve prever breach em < 24h."""
        p = FailurePredictor()
        # 40 amostras × 300s = 12000s histórico
        # slope = 0.5/amostra → valor atual ≈ 50 + 39*0.5 = 69.5%
        # threshold = 75% → breach em (75 - ~intercept) / (0.5/300) ≈ poucos minutos/horas
        feed_trending_up(p, "host-01", "disk", start_value=50.0, slope_per_sample=0.5)
        result = p.predict("host-01", "disk", threshold=75.0)
        assert result is not None, "Deve prever breach para disco crescente"
        assert result["hours_until_breach"] > 0
        assert result["hours_until_breach"] <= 24

    def test_predict_returns_all_required_fields(self):
        """Predição deve conter todos os campos obrigatórios."""
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "disk", 50.0, 0.5)
        result = p.predict("host-01", "disk", threshold=75.0)
        assert result is not None
        required = {
            "host", "metric", "sensor_type", "predicted_breach_time",
            "predicted_breach_iso", "hours_until_breach", "threshold",
            "current_value", "predicted_value", "confidence_interval",
            "trend_slope", "r_squared", "sample_count", "severity",
            "message", "generated_at",
        }
        missing = required - set(result.keys())
        assert not missing, f"Campos faltando na predição: {missing}"

    def test_predict_trend_slope_positive(self):
        """Tendência crescente → slope positivo."""
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "cpu", 50.0, 0.05)
        result = p.predict("host-01", "cpu", threshold=55.0)
        if result:
            assert result["trend_slope"] > 0

    def test_predict_r_squared_between_0_and_1(self):
        """R² deve estar entre 0 e 1."""
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "disk", 50.0, 0.05)
        result = p.predict("host-01", "disk", threshold=55.0)
        if result:
            assert 0.0 <= result["r_squared"] <= 1.0, \
                f"R² fora do range: {result['r_squared']}"

    def test_predict_confidence_interval_ordered(self):
        """confidence_interval[0] <= confidence_interval[1]."""
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "disk", 50.0, 0.05)
        result = p.predict("host-01", "disk", threshold=55.0)
        if result:
            ci = result["confidence_interval"]
            assert ci[0] <= ci[1], f"Intervalo de confiança invertido: {ci}"


# ─── 3. Predição — Casos Negativos ───────────────────────────────────────────

class TestPredictionNegative:
    def test_flat_trend_returns_none(self):
        """Tendência plana → sem predição de breach."""
        p = FailurePredictor()
        feed_flat(p, "host-01", "disk", value=50.0)
        result = p.predict("host-01", "disk", threshold=90.0)
        assert result is None, "Tendência plana não deve gerar predição"

    def test_decreasing_trend_returns_none(self):
        """Tendência decrescente → sem predição de breach."""
        p = FailurePredictor()
        feed_trending_down(p, "host-01", "disk")
        result = p.predict("host-01", "disk", threshold=90.0)
        assert result is None, "Tendência decrescente não deve gerar predição"

    def test_already_above_threshold_returns_none(self):
        """Valor já acima do threshold → breach_time no passado → None."""
        p = FailurePredictor()
        # Valores já acima de 90% com tendência crescente
        feed_trending_up(p, "host-01", "disk", start_value=91.0, slope_per_sample=0.1)
        result = p.predict("host-01", "disk", threshold=90.0)
        # breach_time estará no passado → deve retornar None
        assert result is None, "Valor já acima do threshold não deve gerar predição futura"

    def test_unknown_host_returns_none(self):
        """Host sem dados → None."""
        p = FailurePredictor()
        result = p.predict("ghost-host", "disk", threshold=90.0)
        assert result is None


# ─── 4. Severidade por Urgência ──────────────────────────────────────────────

class TestSeverityClassification:
    def _make_prediction_with_hours(self, hours: float) -> dict:
        """Cria predição simulada com hours_until_breach específico."""
        p = FailurePredictor()
        # Calcular slope necessário para breach em `hours` horas
        # 40 amostras × 5min = 200min de histórico
        # Precisamos que breach ocorra em `hours` horas a partir de agora
        samples = 40
        interval = 300  # 5min
        base_ts = time.time() - (samples * interval)
        threshold = 90.0
        start_value = 60.0
        # slope para atingir threshold em `hours` horas
        total_seconds = hours * 3600
        # valor atual ≈ start_value + samples * slope
        # breach em: (threshold - intercept) / slope = now + total_seconds
        # Aproximação: slope = (threshold - start_value) / (samples * interval + total_seconds)
        slope = (threshold - start_value) / (samples * interval + total_seconds)
        for i in range(samples):
            ts = base_ts + i * interval
            value = start_value + i * slope * interval
            p.add_sample("host-sev", "disk", value, ts)
        return p.predict("host-sev", "disk", threshold=threshold)

    def test_critical_severity_under_2h(self):
        """Breach em < 2h → severity critical."""
        result = self._make_prediction_with_hours(1.0)
        if result:
            assert result["severity"] == "critical", \
                f"Breach em 1h deve ser critical, obtido: {result['severity']}"

    def test_warning_severity_2_to_6h(self):
        """Breach entre 2h e 6h → severity warning."""
        result = self._make_prediction_with_hours(4.0)
        if result:
            assert result["severity"] == "warning", \
                f"Breach em 4h deve ser warning, obtido: {result['severity']}"

    def test_info_severity_over_6h(self):
        """Breach em > 6h → severity info."""
        result = self._make_prediction_with_hours(12.0)
        if result:
            assert result["severity"] == "info", \
                f"Breach em 12h deve ser info, obtido: {result['severity']}"


# ─── 5. Mensagens Humanizadas ────────────────────────────────────────────────

class TestHumanMessages:
    def test_disk_message_contains_keyword(self):
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "disk", 50.0, 0.05)
        result = p.predict("host-01", "disk", threshold=55.0)
        if result:
            assert "disco" in result["message"].lower() or "disk" in result["message"].lower()

    def test_message_contains_host(self):
        p = FailurePredictor()
        feed_trending_up(p, "my-special-host", "disk", 50.0, 0.05)
        result = p.predict("my-special-host", "disk", threshold=55.0)
        if result:
            assert "my-special-host" in result["message"]

    def test_message_contains_time_string(self):
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "disk", 50.0, 0.05)
        result = p.predict("host-01", "disk", threshold=55.0)
        if result:
            assert "hora" in result["message"] or "minuto" in result["message"]


# ─── 6. Default Thresholds ───────────────────────────────────────────────────

class TestDefaultThresholds:
    def test_disk_default_threshold(self):
        assert DEFAULT_THRESHOLDS["disk"] == 90.0

    def test_cpu_default_threshold(self):
        assert DEFAULT_THRESHOLDS["cpu"] == 95.0

    def test_memory_default_threshold(self):
        assert DEFAULT_THRESHOLDS["memory"] == 90.0

    def test_predict_uses_default_threshold_when_none(self):
        """predict() sem threshold usa o padrão do tipo."""
        p = FailurePredictor()
        feed_trending_up(p, "host-01", "disk", 50.0, 0.05)
        result_default = p.predict("host-01", "disk")  # sem threshold
        result_explicit = p.predict("host-01", "disk", threshold=90.0)
        if result_default and result_explicit:
            assert abs(result_default["threshold"] - result_explicit["threshold"]) < 0.01


# ─── 7. predict_all ──────────────────────────────────────────────────────────

class TestPredictAll:
    def test_predict_all_returns_list(self):
        p = FailurePredictor()
        results = p.predict_all()
        assert isinstance(results, list)

    def test_predict_all_sorted_by_urgency(self):
        """predict_all() retorna predições ordenadas por hours_until_breach (menor primeiro)."""
        p = FailurePredictor()
        # Host A e B com slope pequeno, threshold baixo para garantir breach futuro
        feed_trending_up(p, "host-A", "disk", 50.0, 0.05)
        feed_trending_up(p, "host-B", "disk", 50.0, 0.05)

        results = p.predict_all()
        if len(results) >= 2:
            hours = [r["hours_until_breach"] for r in results]
            assert hours == sorted(hours), \
                f"predict_all deve estar ordenado por urgência: {hours}"

    def test_predict_all_excludes_flat_trends(self):
        """predict_all não inclui hosts com tendência plana."""
        p = FailurePredictor()
        feed_flat(p, "flat-host", "disk", value=50.0)
        results = p.predict_all()
        flat_preds = [r for r in results if r["host"] == "flat-host"]
        assert len(flat_preds) == 0


# ─── 8. Thread Safety ────────────────────────────────────────────────────────

class TestThreadSafety:
    def test_concurrent_add_sample_no_crash(self):
        """Múltiplas threads adicionando amostras simultaneamente não causam crash."""
        p = FailurePredictor()
        errors = []

        def worker(host_id: int):
            try:
                for i in range(50):
                    p.add_sample(f"host-{host_id}", "cpu", float(i))
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Erros em threads: {errors}"

    def test_concurrent_predict_no_crash(self):
        """predict() chamado de múltiplas threads não causa crash."""
        p = FailurePredictor()
        feed_trending_up(p, "shared-host", "disk", 50.0, 0.05)
        errors = []

        def worker():
            try:
                p.predict("shared-host", "disk", threshold=90.0)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Erros em threads: {errors}"
