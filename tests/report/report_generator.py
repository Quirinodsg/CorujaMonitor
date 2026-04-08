"""
Report Generator — Coruja Monitor v3.0
Generates test execution reports with threshold validation.
Requirements: 18.3, 18.4, 18.5
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

from tests.report.metrics_collector import TestMetrics, ChaosScenario


class ReportGenerator:
    """Generates test execution reports."""

    # Thresholds
    MAX_DATA_LOSS_PCT = 0.0
    MIN_ALERT_ACCURACY_PCT = 95.0
    MAX_ALERT_DELAY_SECONDS = 30.0
    MIN_AI_RESOLUTION = 0  # at least 1 incident resolved

    def collect_metrics(self, test_results: Dict) -> TestMetrics:
        """Extract TestMetrics from test execution results."""
        return TestMetrics(
            disponibilidade_pct=test_results.get("disponibilidade_pct", 100.0),
            perda_eventos_pct=test_results.get("perda_eventos_pct", 0.0),
            precisao_alertas_pct=test_results.get("precisao_alertas_pct", 100.0),
            precisao_ia_pct=test_results.get("precisao_ia_pct", 100.0),
            mttr_seconds=test_results.get("mttr_seconds", 0.0),
            throughput_metrics_sec=test_results.get("throughput_metrics_sec", 0.0),
            latencia_api_ms=test_results.get("latencia_api_ms", 0.0),
            tempo_ui_seconds=test_results.get("tempo_ui_seconds", 0.0),
        )

    def validate_thresholds(self, metrics: TestMetrics) -> List[str]:
        """Validate metrics against thresholds. Returns list of violations."""
        violations = []
        if metrics.perda_eventos_pct > self.MAX_DATA_LOSS_PCT:
            violations.append(
                f"Data loss {metrics.perda_eventos_pct}% > {self.MAX_DATA_LOSS_PCT}%"
            )
        if metrics.precisao_alertas_pct < self.MIN_ALERT_ACCURACY_PCT:
            violations.append(
                f"Alert accuracy {metrics.precisao_alertas_pct}% < {self.MIN_ALERT_ACCURACY_PCT}%"
            )
        if metrics.mttr_seconds > self.MAX_ALERT_DELAY_SECONDS:
            violations.append(
                f"Alert delay {metrics.mttr_seconds}s > {self.MAX_ALERT_DELAY_SECONDS}s"
            )
        return violations

    def generate_report(self, metrics: TestMetrics, output_path: Optional[str] = None) -> Dict:
        """Generate report dict. Optionally write to file."""
        violations = self.validate_thresholds(metrics)
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "PASS" if not violations else "FAIL",
            "metrics": {
                "disponibilidade_pct": metrics.disponibilidade_pct,
                "perda_eventos_pct": metrics.perda_eventos_pct,
                "precisao_alertas_pct": metrics.precisao_alertas_pct,
                "precisao_ia_pct": metrics.precisao_ia_pct,
                "mttr_seconds": metrics.mttr_seconds,
                "throughput_metrics_sec": metrics.throughput_metrics_sec,
                "latencia_api_ms": metrics.latencia_api_ms,
                "tempo_ui_seconds": metrics.tempo_ui_seconds,
            },
            "violations": violations,
        }
        if output_path:
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
        return report
