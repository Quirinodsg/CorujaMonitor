"""
Load Test Enterprise — Coruja Monitor v3.5
Simula 1000 hosts × 50 sensores = 50.000 sensores
Valida: latência, memória, throughput
"""
import time
import threading
import statistics
import gc
import os
import sys

# Adicionar paths necessários
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../ai-agent"))

HOSTS = 1000
SENSORS_PER_HOST = 50
TOTAL_SENSORS = HOSTS * SENSORS_PER_HOST


def _make_event(host_id: int, sensor_idx: int):
    """Cria evento simulado."""
    import random
    return {
        "host_id": f"host-{host_id:04d}",
        "sensor_id": f"sensor-{host_id:04d}-{sensor_idx:02d}",
        "sensor_type": ["cpu", "memory", "disk", "ping", "service"][sensor_idx % 5],
        "value": random.uniform(10, 99),
        "status": random.choice(["ok", "ok", "ok", "warning", "critical"]),
        "timestamp": time.time(),
    }


def test_failure_predictor_throughput():
    """Testa throughput do FailurePredictor com 1000 hosts × 50 métricas."""
    from failure_predictor import FailurePredictor
    predictor = FailurePredictor()

    # Alimentar com dados históricos simulados (30 amostras por sensor)
    start = time.time()
    total_samples = 0
    base_ts = time.time() - 3600  # 1h atrás

    for host_idx in range(HOSTS):
        host = f"host-{host_idx:04d}"
        for sensor_idx in range(SENSORS_PER_HOST):
            metric = ["cpu", "memory", "disk", "network", "ping"][sensor_idx % 5]
            for sample_idx in range(30):
                ts = base_ts + (sample_idx * 120)  # a cada 2min
                # Tendência crescente para disk (vai acionar predição)
                if metric == "disk":
                    value = 60 + (sample_idx * 1.0)  # 60% → 89%
                else:
                    value = 50 + (sample_idx * 0.1)
                predictor.add_sample(host, metric, value, ts)
                total_samples += 1

    ingest_time = time.time() - start
    throughput = total_samples / ingest_time

    print(f"\n[LOAD TEST] Ingestão: {total_samples:,} amostras em {ingest_time:.2f}s")
    print(f"[LOAD TEST] Throughput ingestão: {throughput:,.0f} amostras/s")

    assert throughput > 10_000, f"Throughput muito baixo: {throughput:.0f}/s"

    # Testar predições
    pred_start = time.time()
    predictions = predictor.predict_all()
    pred_time = time.time() - pred_start

    print(f"[LOAD TEST] Predições calculadas: {len(predictions)} em {pred_time:.2f}s")
    assert pred_time < 30, f"Predição muito lenta: {pred_time:.2f}s"
    assert len(predictions) > 0, "Nenhuma predição gerada"


def test_alert_engine_throughput():
    """Testa AlertEngine com 50.000 eventos simultâneos."""
    from core.spec.models import Event
    from core.spec.enums import EventSeverity
    from alert_engine.engine import AlertEngine
    import uuid

    engine = AlertEngine()

    # Gerar 50.000 eventos
    events = []
    for host_idx in range(HOSTS):
        for sensor_idx in range(SENSORS_PER_HOST):
            ev = Event(
                id=str(uuid.uuid4()),
                host_id=uuid.UUID(int=(host_idx % 1000) + 1),
                type=["cpu_high", "memory_high", "disk_full", "host_down", "service_down"][sensor_idx % 5],
                severity=EventSeverity.WARNING if sensor_idx % 3 != 0 else EventSeverity.CRITICAL,
                timestamp=time.time(),
            )
            events.append(ev)

    start = time.time()
    alerts = engine.process_events(events)
    elapsed = time.time() - start

    throughput = len(events) / elapsed
    print(f"\n[LOAD TEST] AlertEngine: {len(events):,} eventos → {len(alerts)} alertas em {elapsed:.2f}s")
    print(f"[LOAD TEST] Throughput alertas: {throughput:,.0f} eventos/s")
    print(f"[LOAD TEST] Métricas: {engine.get_metrics()}")

    assert elapsed < 10, f"AlertEngine muito lento: {elapsed:.2f}s para {len(events):,} eventos"
    assert len(alerts) < len(events), "Agrupamento/supressão não funcionou"


def test_topology_suppression_at_scale():
    """Testa supressão topológica com 1000 hosts."""
    from core.spec.models import Event
    from core.spec.enums import EventSeverity
    from alert_engine.engine import AlertEngine
    import uuid

    engine = AlertEngine()

    # Configurar topologia: todos os hosts dependem de 10 switches
    topology = {}
    for host_idx in range(HOSTS):
        switch_id = f"switch-{host_idx // 100:02d}"
        topology[str(uuid.UUID(int=host_idx + 1))] = switch_id
    engine.set_topology(topology)

    # Marcar 5 switches como falhos
    for i in range(5):
        engine.mark_host_failed(f"switch-{i:02d}")

    # Gerar eventos para todos os hosts
    events = [
        Event(
            id=str(uuid.uuid4()),
            host_id=uuid.UUID(int=i + 1),
            type="host_down",
            severity=EventSeverity.CRITICAL,
            timestamp=time.time(),
        )
        for i in range(HOSTS)
    ]

    alerts = engine.process_events(events)
    metrics = engine.get_metrics()

    suppressed = metrics["alerts_topology_suppressed"]
    print(f"\n[LOAD TEST] Supressão topológica: {suppressed} de {HOSTS} eventos suprimidos")
    # 5 switches × 100 hosts = 500 suprimidos
    assert suppressed >= 400, f"Supressão topológica insuficiente: {suppressed}"


def test_memory_usage():
    """Valida consumo de memória com carga máxima."""
    try:
        import psutil
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Simular carga
        from failure_predictor import FailurePredictor
        predictor = FailurePredictor()
        for i in range(100):
            for j in range(50):
                predictor.add_sample(f"host-{i}", f"metric-{j}", float(i + j))

        gc.collect()
        mem_after = process.memory_info().rss / 1024 / 1024
        mem_delta = mem_after - mem_before

        print(f"\n[LOAD TEST] Memória: antes={mem_before:.1f}MB, depois={mem_after:.1f}MB, delta={mem_delta:.1f}MB")
        assert mem_delta < 500, f"Consumo de memória excessivo: {mem_delta:.1f}MB"
    except ImportError:
        print("[LOAD TEST] psutil não disponível — pulando teste de memória")


if __name__ == "__main__":
    print("=" * 60)
    print("CORUJA MONITOR v3.5 — LOAD TEST ENTERPRISE")
    print(f"Simulando {HOSTS:,} hosts × {SENSORS_PER_HOST} sensores = {TOTAL_SENSORS:,} sensores")
    print("=" * 60)

    tests = [
        ("FailurePredictor Throughput", test_failure_predictor_throughput),
        ("AlertEngine Throughput", test_alert_engine_throughput),
        ("Topology Suppression Scale", test_topology_suppression_at_scale),
        ("Memory Usage", test_memory_usage),
    ]

    results = []
    for name, fn in tests:
        print(f"\n▶ {name}")
        try:
            fn()
            results.append((name, "PASS"))
            print(f"  ✓ PASS")
        except AssertionError as e:
            results.append((name, f"FAIL: {e}"))
            print(f"  ✗ FAIL: {e}")
        except Exception as e:
            results.append((name, f"ERROR: {e}"))
            print(f"  ✗ ERROR: {e}")

    print("\n" + "=" * 60)
    print("RESULTADOS:")
    for name, result in results:
        status = "✓" if result == "PASS" else "✗"
        print(f"  {status} {name}: {result}")
    print("=" * 60)
