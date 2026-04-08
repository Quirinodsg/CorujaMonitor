"""
Load: Throughput Tests — Coruja Monitor v3.0
Tests: 1000 hosts × 50 sensors, throughput ≥1000 metrics/s.
Requirements: 13.1, 13.2
"""
import pytest
import time

from tests.utils.load_generator import LoadGenerator


@pytest.mark.load
class TestThroughput:
    """Req 13.1 — throughput ≥1000 metrics/s for 50k metrics."""

    def test_50k_metrics_throughput(self):
        """Generate 50k metrics and verify throughput."""
        gen = LoadGenerator()
        result = gen.simulate_collection_cycle(host_count=1000, sensors_per_host=50)
        assert result["metrics"] == 50000
        assert result["throughput_per_sec"] >= 1000

    def test_metric_batch_generation_speed(self):
        """Batch generation of 10k metrics is fast."""
        gen = LoadGenerator()
        hosts = gen.generate_hosts(200)
        sensors = gen.generate_sensors(hosts, 50)
        start = time.monotonic()
        metrics = gen.generate_metrics_batch(sensors)
        elapsed = time.monotonic() - start
        assert len(metrics) == 10000
        assert elapsed < 5.0  # <5s

    def test_host_generation_speed(self):
        """1000 hosts generated quickly."""
        gen = LoadGenerator()
        start = time.monotonic()
        hosts = gen.generate_hosts(1000)
        elapsed = time.monotonic() - start
        assert len(hosts) == 1000
        assert elapsed < 2.0

    def test_sensor_generation_speed(self):
        """50k sensors generated quickly."""
        gen = LoadGenerator()
        hosts = gen.generate_hosts(1000)
        start = time.monotonic()
        sensors = gen.generate_sensors(hosts, 50)
        elapsed = time.monotonic() - start
        assert len(sensors) == 50000
        assert elapsed < 10.0
