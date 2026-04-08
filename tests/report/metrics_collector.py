"""
Test Metrics Collector — Coruja Monitor v3.0
Dataclasses for test metrics and chaos scenarios.
Requirements: 18.1, 18.2
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class TestMetrics:
    """Metrics collected during test suite execution."""
    disponibilidade_pct: float = 100.0       # % sensors OK
    perda_eventos_pct: float = 0.0           # % events lost
    precisao_alertas_pct: float = 100.0      # % alerts correct
    precisao_ia_pct: float = 100.0           # % AI decisions correct
    mttr_seconds: float = 0.0               # Mean Time To Resolve
    throughput_metrics_sec: float = 0.0      # metrics/second ingested
    latencia_api_ms: float = 0.0            # average API latency
    tempo_ui_seconds: float = 0.0           # UI update time


@dataclass
class ChaosScenario:
    """Definition of a chaos engineering scenario."""
    name: str
    failure_type: str                        # redis_offline, api_offline, network_latency, packet_loss
    duration_seconds: float = 0.0
    parameters: Dict = field(default_factory=dict)
    expected_behavior: str = ""              # buffer_activated, retry_success, graceful_degradation


class MetricsCollector:
    """Collects and aggregates test metrics."""

    def __init__(self):
        self._metrics: List[TestMetrics] = []
        self._scenarios: List[ChaosScenario] = []

    def record_metrics(self, metrics: TestMetrics) -> None:
        self._metrics.append(metrics)

    def record_scenario(self, scenario: ChaosScenario) -> None:
        self._scenarios.append(scenario)

    def get_summary(self) -> Dict:
        if not self._metrics:
            return {"total_runs": 0}
        avg_disponibilidade = sum(m.disponibilidade_pct for m in self._metrics) / len(self._metrics)
        avg_perda = sum(m.perda_eventos_pct for m in self._metrics) / len(self._metrics)
        avg_precisao = sum(m.precisao_alertas_pct for m in self._metrics) / len(self._metrics)
        return {
            "total_runs": len(self._metrics),
            "avg_disponibilidade_pct": round(avg_disponibilidade, 2),
            "avg_perda_eventos_pct": round(avg_perda, 2),
            "avg_precisao_alertas_pct": round(avg_precisao, 2),
            "chaos_scenarios": len(self._scenarios),
        }
