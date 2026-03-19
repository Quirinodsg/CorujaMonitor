"""
FASE 5 — Chaos Engineering: Coruja Monitor v3.0
Testa resiliência do sistema sob falhas injetadas.
"""
import time
import threading
import logging
from collections import deque
from typing import Callable, Optional, Dict, Any
from unittest.mock import patch, MagicMock

logger = logging.getLogger(__name__)


class ChaosResult:
    def __init__(self, scenario: str):
        self.scenario = scenario
        self.passed = False
        self.details: Dict[str, Any] = {}
        self.error: Optional[str] = None
        self.duration_ms: float = 0.0

    def __repr__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"ChaosResult({self.scenario}: {status}, {self.duration_ms:.0f}ms)"


class ChaosRunner:
    """Executa cenários de chaos engineering."""

    def run_all(self) -> list[ChaosResult]:
        scenarios = [
            self.scenario_redis_down,
            self.scenario_postgres_down,
            self.scenario_host_offline,
            self.scenario_high_latency,
        ]
        results = []
        for scenario in scenarios:
            start = time.monotonic()
            result = scenario()
            result.duration_ms = (time.monotonic() - start) * 1000
            results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            logger.info(f"{status} {result.scenario} ({result.duration_ms:.0f}ms)")
        return results

    def scenario_redis_down(self) -> ChaosResult:
        """
        Cenário 1: Redis indisponível.
        Esperado: StreamProducer usa fallback deque(10k) sem crash.
        """
        result = ChaosResult("redis_down")
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../probe'))
            from metrics_pipeline.stream_producer import StreamProducer, MetricEvent

            # Criar producer sem Redis (simula Redis down)
            producer = StreamProducer(redis_url=None)

            # Publicar 100 eventos — devem ir para fallback queue
            published = 0
            for i in range(100):
                event = MetricEvent(
                    sensor_id=i, server_id=1,
                    sensor_type="cpu", value=float(i),
                    unit="%", status="ok"
                )
                ok = producer.publish(event)
                if ok:
                    published += 1

            result.details["published"] = published
            result.details["fallback_queue_size"] = len(producer._fallback_queue)
            result.details["redis_connected"] = producer._redis is not None

            # Validar: fallback queue tem os eventos
            assert len(producer._fallback_queue) > 0, "Fallback queue vazia — eventos perdidos!"
            assert producer._redis is None, "Redis deveria estar desconectado"

            result.passed = True

        except Exception as e:
            result.error = str(e)
            result.passed = False

        return result

    def scenario_postgres_down(self) -> ChaosResult:
        """
        Cenário 2: PostgreSQL indisponível.
        Esperado: API retorna 503 graciosamente, sem crash.
        """
        result = ChaosResult("postgres_down")
        try:
            from event_processor.processor import EventProcessor
            from core.spec.models import Metric, Sensor
            from core.spec.enums import Protocol
            from uuid import uuid4
            from datetime import datetime, timezone

            # Simular DB down: processor sem db_session
            processor = EventProcessor(redis_client=None, db_session=None)

            sensor = Sensor(
                host_id=uuid4(), type="cpu",
                protocol=Protocol.WMI, interval=60,
                thresholds={"warning": 80, "critical": 95}
            )
            metric = Metric(
                sensor_id=sensor.id, host_id=sensor.host_id,
                value=97.0, unit="%",
                timestamp=datetime.now(timezone.utc)
            )

            # Deve processar sem crash mesmo sem DB
            processor.seed_state(str(sensor.id), None)
            event = processor.process(metric, sensor)

            result.details["event_generated"] = event is not None
            result.details["no_crash"] = True
            result.passed = True

        except Exception as e:
            result.error = str(e)
            result.passed = False

        return result

    def scenario_host_offline(self) -> ChaosResult:
        """
        Cenário 3: Host offline.
        Esperado: ICMP sensor retorna critical sem travar o sistema.
        """
        result = ChaosResult("host_offline")
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../probe'))
            from collectors.icmp_sensor import ICMPSensor

            # Host que não existe
            sensor = ICMPSensor("192.0.2.1", count=1, timeout=1, retries=0)

            start = time.monotonic()
            r = sensor.collect()
            elapsed = (time.monotonic() - start) * 1000

            result.details["status"] = r.get("status")
            result.details["elapsed_ms"] = round(elapsed, 1)
            result.details["timed_out_gracefully"] = elapsed < 10000  # <10s

            assert r.get("status") == "critical", f"Host offline deveria ser critical, got: {r.get('status')}"
            assert elapsed < 10000, f"Sensor travou por {elapsed:.0f}ms"

            result.passed = True

        except Exception as e:
            result.error = str(e)
            result.passed = False

        return result

    def scenario_high_latency(self) -> ChaosResult:
        """
        Cenário 4: Latência alta no HTTP sensor.
        Esperado: timeout configurável funciona, retorna critical.
        """
        result = ChaosResult("high_latency")
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../probe'))
            from collectors.http_sensor import HTTPSensor
            import requests as req_lib
            from unittest.mock import patch

            sensor = HTTPSensor("http://slow-host.example.com", timeout=1.0)

            with patch("requests.get", side_effect=req_lib.exceptions.Timeout("timed out")):
                start = time.monotonic()
                r = sensor.collect()
                elapsed = (time.monotonic() - start) * 1000

            result.details["status"] = r.get("status")
            result.details["error_type"] = r.get("error_type")
            result.details["elapsed_ms"] = round(elapsed, 1)

            assert r.get("status") == "critical"
            assert r.get("error_type") == "timeout"

            result.passed = True

        except Exception as e:
            result.error = str(e)
            result.passed = False

        return result
