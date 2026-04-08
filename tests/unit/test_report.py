"""
Unit tests for Report module — Coruja Monitor v3.0
Tests: TestMetrics, ChaosScenario, ReportGenerator.
Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
"""
import pytest

from tests.report.metrics_collector import TestMetrics, ChaosScenario, MetricsCollector
from tests.report.report_generator import ReportGenerator


@pytest.mark.unit
class TestTestMetrics:
    """Req 18.1 — TestMetrics dataclass."""

    def test_default_values(self):
        m = TestMetrics()
        assert m.disponibilidade_pct == 100.0
        assert m.perda_eventos_pct == 0.0

    def test_custom_values(self):
        m = TestMetrics(disponibilidade_pct=95.0, perda_eventos_pct=2.0)
        assert m.disponibilidade_pct == 95.0
        assert m.perda_eventos_pct == 2.0


@pytest.mark.unit
class TestChaosScenario:
    """Req 18.2 — ChaosScenario dataclass."""

    def test_create_scenario(self):
        s = ChaosScenario(
            name="Redis Offline",
            failure_type="redis_offline",
            duration_seconds=30.0,
            expected_behavior="buffer_activated",
        )
        assert s.name == "Redis Offline"
        assert s.failure_type == "redis_offline"


@pytest.mark.unit
class TestMetricsCollector:
    """MetricsCollector aggregation."""

    def test_record_and_summarize(self):
        collector = MetricsCollector()
        collector.record_metrics(TestMetrics(disponibilidade_pct=95.0))
        collector.record_metrics(TestMetrics(disponibilidade_pct=85.0))
        summary = collector.get_summary()
        assert summary["total_runs"] == 2
        assert summary["avg_disponibilidade_pct"] == 90.0

    def test_empty_summary(self):
        collector = MetricsCollector()
        summary = collector.get_summary()
        assert summary["total_runs"] == 0


@pytest.mark.unit
class TestReportGenerator:
    """Req 18.3-18.5 — ReportGenerator validation and output."""

    def test_no_violations_pass(self):
        gen = ReportGenerator()
        metrics = TestMetrics(perda_eventos_pct=0.0, precisao_alertas_pct=98.0, mttr_seconds=10.0)
        violations = gen.validate_thresholds(metrics)
        assert violations == []

    def test_data_loss_violation(self):
        gen = ReportGenerator()
        metrics = TestMetrics(perda_eventos_pct=5.0)
        violations = gen.validate_thresholds(metrics)
        assert any("Data loss" in v for v in violations)

    def test_alert_accuracy_violation(self):
        gen = ReportGenerator()
        metrics = TestMetrics(precisao_alertas_pct=80.0)
        violations = gen.validate_thresholds(metrics)
        assert any("Alert accuracy" in v for v in violations)

    def test_alert_delay_violation(self):
        gen = ReportGenerator()
        metrics = TestMetrics(mttr_seconds=60.0)
        violations = gen.validate_thresholds(metrics)
        assert any("Alert delay" in v for v in violations)

    def test_generate_report_pass(self):
        gen = ReportGenerator()
        metrics = TestMetrics()
        report = gen.generate_report(metrics)
        assert report["status"] == "PASS"
        assert report["violations"] == []

    def test_generate_report_fail(self):
        gen = ReportGenerator()
        metrics = TestMetrics(perda_eventos_pct=10.0)
        report = gen.generate_report(metrics)
        assert report["status"] == "FAIL"

    def test_generate_report_to_file(self, tmp_path):
        gen = ReportGenerator()
        metrics = TestMetrics()
        output = tmp_path / "report.json"
        report = gen.generate_report(metrics, output_path=str(output))
        assert output.exists()
        assert report["status"] == "PASS"
