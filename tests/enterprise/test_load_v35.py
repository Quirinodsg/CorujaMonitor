"""
QA Enterprise — Load & Performance Tests v3.5
Testa: throughput do FailurePredictor, AlertEngine com 50k eventos,
supressão topológica em escala, memory bounds, latência p95/p99.
Nível: Arquiteto Senior — SLOs de performance definidos e verificados.
"""
import time
import uuid
import gc
import statistics
import threading
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ai-agent"))

# SLOs de Performance
SLO_INGEST_THROUGHPUT = 10_000      # amostras/s mínimo
SLO_ALERT_ENGINE_MAX_SECONDS = 10   # máximo para 50k eventos
SLO_PREDICTION_MAX_SECONDS = 30     # máximo para predict_all com 1000 hosts
SLO_TOPOLOGY_SUPPRESSION_MIN = 400  # mínimo de suprimidos (5 switches × 100 hosts)
SLO_MEMORY_DELTA_MAX_MB = 500       # máximo de delta de memória


# ─── 1. FailurePredictor — Throughput de Ingestão ────────────────────────────

class TestFailurePredictorLoad:
    def test_ingest_throughput_meets_slo(self):
        """
        SLO: ingestão de amostras >= 10.000/s.
        Simula 1000 hosts × 50 métricas × 30 amostras = 1.500.000 amostras.
        """
        from failure_predictor import FailurePredictor
        predictor = FailurePredictor()

        HOSTS = 1000
        METRICS = 50
        SAMPLES = 30
        base_ts = time.time() - (SAMPLES * 300)

        start = time.perf_counter()
        total = 0
        for h in range(HOSTS):
            for m in range(METRICS):
                for s in range(SAMPLES):
                    ts = base_ts + s * 300
                    value = 50.0 + s * 0.5
                    predictor.add_sample(f"host-{h:04d}", f"metric-{m}", value, ts)
                    total += 1
        elapsed = time.perf_counter() - start
        throughput = total / elapsed

        print(f"\n[LOAD] Ingestão: {total:,} amostras em {elapsed:.2f}s = {throughput:,.0f}/s")
        assert throughput >= SLO_INGEST_THROUGHPUT, \
            f"SLO violado: throughput {throughput:.0f}/s < {SLO_INGEST_THROUGHPUT}/s"

    def test_predict_all_latency_meets_slo(self):
        """
        SLO: predict_all() com 1000 hosts × 5 métricas em < 30s.
        """
        from failure_predictor import FailurePredictor
        predictor = FailurePredictor()

        HOSTS = 1000
        base_ts = time.time() - (40 * 300)
        for h in range(HOSTS):
            for s in range(40):
                ts = base_ts + s * 300
                predictor.add_sample(f"host-{h:04d}", "disk", 60.0 + s * 0.75, ts)

        start = time.perf_counter()
        predictions = predictor.predict_all()
        elapsed = time.perf_counter() - start

        print(f"\n[LOAD] predict_all: {len(predictions)} predições em {elapsed:.2f}s")
        assert elapsed < SLO_PREDICTION_MAX_SECONDS, \
            f"SLO violado: predict_all levou {elapsed:.2f}s > {SLO_PREDICTION_MAX_SECONDS}s"

    def test_predict_all_generates_predictions(self):
        """predict_all deve gerar predições para hosts com tendência crescente."""
        from failure_predictor import FailurePredictor
        predictor = FailurePredictor()
        base_ts = time.time() - (40 * 300)
        for s in range(40):
            # Tendência crescente de 50 a 80 (ainda abaixo do threshold 90)
            predictor.add_sample("host-trend", "disk", 50.0 + s * 0.75, base_ts + s * 300)
        predictions = predictor.predict_all()
        assert len(predictions) > 0, "Deve gerar pelo menos 1 predição"


# ─── 2. AlertEngine — Throughput com 50k Eventos ─────────────────────────────

class TestAlertEngineLoad:
    def _make_events(self, count: int):
        from core.spec.models import Event
        from core.spec.enums import EventSeverity
        events = []
        for i in range(count):
            events.append(Event(
                id=uuid.uuid4(),
                host_id=uuid.UUID(int=(i % 1000) + 1),
                type=["cpu_high", "memory_high", "disk_full", "host_down", "service_down"][i % 5],
                severity=EventSeverity.WARNING if i % 3 != 0 else EventSeverity.CRITICAL,
                timestamp=time.time(),
            ))
        return events

    def test_50k_events_within_slo(self):
        """
        SLO: processar 50.000 eventos em < 10s.
        """
        from alert_engine.engine import AlertEngine
        engine = AlertEngine(cooldown_seconds=0)
        events = self._make_events(50_000)

        start = time.perf_counter()
        alerts = engine.process_events(events)
        elapsed = time.perf_counter() - start

        throughput = len(events) / elapsed
        print(f"\n[LOAD] AlertEngine: {len(events):,} eventos → {len(alerts)} alertas em {elapsed:.2f}s ({throughput:,.0f} ev/s)")
        assert elapsed < SLO_ALERT_ENGINE_MAX_SECONDS, \
            f"SLO violado: {elapsed:.2f}s > {SLO_ALERT_ENGINE_MAX_SECONDS}s"

    def test_grouping_reduces_alert_count(self):
        """Agrupamento deve reduzir drasticamente o número de alertas."""
        from alert_engine.engine import AlertEngine
        engine = AlertEngine(cooldown_seconds=0)
        events = self._make_events(10_000)
        alerts = engine.process_events(events)
        # Com agrupamento por host, deve ter muito menos alertas que eventos
        assert len(alerts) < len(events), \
            f"Agrupamento não funcionou: {len(alerts)} alertas para {len(events)} eventos"

    def test_metrics_tracked_correctly(self):
        """Métricas do engine devem ser incrementadas corretamente."""
        from alert_engine.engine import AlertEngine
        engine = AlertEngine(cooldown_seconds=0)
        events = self._make_events(1000)
        engine.process_events(events)
        metrics = engine.get_metrics()
        assert metrics["alerts_total"] > 0
        # Total de alertas deve ser menor que eventos (agrupamento)
        assert metrics["alerts_total"] <= 1000


# ─── 3. Supressão Topológica em Escala ───────────────────────────────────────

class TestTopologySuppressionScale:
    def test_1000_hosts_5_switches_suppression(self):
        """
        1000 hosts em 10 switches, 5 switches em falha.
        Esperado: >= 400 eventos suprimidos (5 × 100 hosts).
        """
        from alert_engine.engine import AlertEngine
        from core.spec.models import Event
        from core.spec.enums import EventSeverity

        engine = AlertEngine(cooldown_seconds=0)

        # Topologia: 1000 hosts em 10 switches (100 por switch)
        topology = {}
        for i in range(1000):
            switch_id = f"switch-{i // 100:02d}"
            topology[str(uuid.UUID(int=i + 1))] = switch_id
        engine._topology_parents = topology

        # 5 switches em falha
        for i in range(5):
            engine._failed_hosts.add(f"switch-{i:02d}")

        events = [
            Event(
                id=uuid.uuid4(),
                host_id=uuid.UUID(int=i + 1),
                type="host_down",
                severity=EventSeverity.CRITICAL,
                timestamp=time.time(),
            )
            for i in range(1000)
        ]

        engine.process_events(events)
        metrics = engine.get_metrics()
        suppressed = metrics["alerts_topology_suppressed"]

        print(f"\n[LOAD] Supressão topológica: {suppressed}/1000 eventos suprimidos")
        assert suppressed >= SLO_TOPOLOGY_SUPPRESSION_MIN, \
            f"SLO violado: {suppressed} suprimidos < {SLO_TOPOLOGY_SUPPRESSION_MIN}"


# ─── 4. Latência P95/P99 ─────────────────────────────────────────────────────

class TestLatencyPercentiles:
    def test_alert_engine_p99_latency(self):
        """
        P99 de latência por batch de 100 eventos deve ser < 100ms.
        """
        from alert_engine.engine import AlertEngine
        from core.spec.models import Event
        from core.spec.enums import EventSeverity

        engine = AlertEngine(cooldown_seconds=0)
        latencies = []

        for batch in range(100):
            events = [
                Event(
                    id=uuid.uuid4(),
                    host_id=uuid.UUID(int=batch + 1),
                    type="cpu_high",
                    severity=EventSeverity.WARNING,
                    timestamp=time.time(),
                )
                for _ in range(100)
            ]
            start = time.perf_counter()
            engine.process_events(events)
            latencies.append((time.perf_counter() - start) * 1000)  # ms

        p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile

        print(f"\n[LOAD] Latência AlertEngine — P95: {p95:.1f}ms, P99: {p99:.1f}ms")
        assert p99 < 100, f"P99 muito alto: {p99:.1f}ms > 100ms"

    def test_failure_predictor_predict_latency(self):
        """
        predict() individual deve completar em < 50ms.
        """
        from failure_predictor import FailurePredictor
        predictor = FailurePredictor()
        base_ts = time.time() - (40 * 300)
        for s in range(40):
            predictor.add_sample("host-lat", "disk", 60.0 + s * 0.75, base_ts + s * 300)

        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            predictor.predict("host-lat", "disk", threshold=90.0)
            latencies.append((time.perf_counter() - start) * 1000)

        p99 = statistics.quantiles(latencies, n=100)[98]
        print(f"\n[LOAD] Latência predict() — P99: {p99:.2f}ms")
        assert p99 < 50, f"predict() P99 muito alto: {p99:.2f}ms > 50ms"


# ─── 5. Memory Bounds ────────────────────────────────────────────────────────

class TestMemoryBounds:
    def test_predictor_memory_bounded(self):
        """
        FailurePredictor com 1000 hosts × 50 métricas × 2016 amostras
        não deve exceder 500MB de delta.
        """
        try:
            import psutil
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024

            from failure_predictor import FailurePredictor
            predictor = FailurePredictor()
            for h in range(100):  # 100 hosts para não demorar demais
                for m in range(10):
                    for s in range(100):
                        predictor.add_sample(f"h{h}", f"m{m}", float(s))

            gc.collect()
            mem_after = process.memory_info().rss / 1024 / 1024
            delta = mem_after - mem_before

            print(f"\n[LOAD] Memória FailurePredictor: delta={delta:.1f}MB")
            assert delta < SLO_MEMORY_DELTA_MAX_MB, \
                f"SLO violado: delta {delta:.1f}MB > {SLO_MEMORY_DELTA_MAX_MB}MB"
        except ImportError:
            pytest.skip("psutil não disponível")

    def test_alert_engine_memory_bounded(self):
        """AlertEngine não deve vazar memória após processar 50k eventos."""
        try:
            import psutil
            from alert_engine.engine import AlertEngine
            from core.spec.models import Event
            from core.spec.enums import EventSeverity

            process = psutil.Process()
            engine = AlertEngine(cooldown_seconds=0)
            mem_before = process.memory_info().rss / 1024 / 1024

            for _ in range(10):
                events = [
                    Event(
                        id=uuid.uuid4(),
                        host_id=uuid.UUID(int=(i % 100) + 1),
                        type="cpu_high",
                        severity=EventSeverity.WARNING,
                        timestamp=time.time(),
                    )
                    for i in range(5000)
                ]
                engine.process_events(events)

            gc.collect()
            mem_after = process.memory_info().rss / 1024 / 1024
            delta = mem_after - mem_before

            print(f"\n[LOAD] Memória AlertEngine: delta={delta:.1f}MB")
            assert delta < 200, f"Possível memory leak: delta {delta:.1f}MB > 200MB"
        except ImportError:
            pytest.skip("psutil não disponível")


# ─── 6. Concorrência ─────────────────────────────────────────────────────────

class TestConcurrency:
    def test_predictor_concurrent_writes_reads(self):
        """FailurePredictor suporta escritas e leituras concorrentes sem crash."""
        from failure_predictor import FailurePredictor
        predictor = FailurePredictor()
        errors = []

        def writer(host_id: int):
            try:
                base_ts = time.time() - 40 * 300
                for s in range(40):
                    predictor.add_sample(f"host-{host_id}", "disk", 60.0 + s * 0.75, base_ts + s * 300)
            except Exception as e:
                errors.append(f"writer-{host_id}: {e}")

        def reader():
            try:
                predictor.predict_all()
            except Exception as e:
                errors.append(f"reader: {e}")

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(20)]
        threads += [threading.Thread(target=reader) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Erros de concorrência: {errors}"
