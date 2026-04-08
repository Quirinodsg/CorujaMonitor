"""
ChaosEngine — Coruja Monitor v3.0.
Simula falhas de infraestrutura para testes de resiliência.
Context managers que injetam falhas controladas.
"""
import random
import time
import threading
from contextlib import contextmanager
from unittest.mock import MagicMock, patch


class ChaosEngine:
    """Simulador de falhas de infraestrutura para chaos engineering."""

    @contextmanager
    def simulate_redis_offline(self):
        """
        Context manager que fornece um mock Redis que lança ConnectionError
        em qualquer operação de escrita/leitura.
        """
        mock = MagicMock()
        error = ConnectionError("Redis connection refused (chaos)")

        mock.xadd.side_effect = error
        mock.xreadgroup.side_effect = error
        mock.xack.side_effect = error
        mock.ping.side_effect = error
        mock.get.side_effect = error
        mock.set.side_effect = error
        mock.pipeline.side_effect = error

        yield mock

    @contextmanager
    def simulate_api_offline(self):
        """
        Context manager que fornece um mock HTTP client que retorna 503
        em qualquer requisição.
        """
        mock = MagicMock()

        response_503 = MagicMock()
        response_503.status_code = 503
        response_503.text = "Service Unavailable (chaos)"
        response_503.json.return_value = {"error": "Service Unavailable"}
        response_503.raise_for_status.side_effect = Exception("503 Service Unavailable")

        mock.get.return_value = response_503
        mock.post.return_value = response_503
        mock.put.return_value = response_503
        mock.delete.return_value = response_503

        yield mock

    @contextmanager
    def simulate_network_latency(self, min_ms: int = 100, max_ms: int = 500):
        """
        Context manager que injeta latência artificial em chamadas.
        Fornece uma função `delayed_call` que adiciona sleep antes de executar.
        """
        def add_latency():
            delay = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
            time.sleep(delay)
            return delay * 1000  # retorna latência em ms

        ctx = {
            "add_latency": add_latency,
            "min_ms": min_ms,
            "max_ms": max_ms,
            "calls": [],
        }

        original_sleep = time.sleep

        def patched_operation(func):
            """Wrapper que adiciona latência antes de executar a função."""
            def wrapper(*args, **kwargs):
                latency_ms = add_latency()
                ctx["calls"].append(latency_ms)
                return func(*args, **kwargs)
            return wrapper

        ctx["wrap"] = patched_operation
        yield ctx

    @contextmanager
    def simulate_packet_loss(self, loss_pct: float = 20.0):
        """
        Context manager que simula perda de pacotes.
        Fornece uma função `maybe_drop` que retorna True se o pacote foi "perdido".
        """
        stats = {"total": 0, "dropped": 0, "delivered": 0}

        def maybe_drop() -> bool:
            """Retorna True se o pacote foi perdido."""
            stats["total"] += 1
            if random.random() * 100 < loss_pct:
                stats["dropped"] += 1
                return True
            stats["delivered"] += 1
            return False

        def send_with_loss(data, send_fn):
            """Envia dados com possibilidade de perda. Retorna True se entregue."""
            if maybe_drop():
                return False
            send_fn(data)
            return True

        ctx = {
            "maybe_drop": maybe_drop,
            "send_with_loss": send_with_loss,
            "loss_pct": loss_pct,
            "stats": stats,
        }
        yield ctx

    @contextmanager
    def simulate_redis_reconnect(self, offline_seconds: float = 2.0):
        """
        Context manager que simula Redis offline seguido de reconexão.
        Primeiro período: ConnectionError. Após offline_seconds: operação normal.
        Fornece mock Redis que muda de comportamento após o tempo.
        """
        start = time.monotonic()
        error = ConnectionError("Redis offline (chaos reconnect)")

        mock = MagicMock()
        _streams: dict[str, list] = {}
        _counter = [0]

        def _xadd(stream, fields, **kwargs):
            elapsed = time.monotonic() - start
            if elapsed < offline_seconds:
                raise error
            _counter[0] += 1
            msg_id = f"{int(time.time() * 1000)}-{_counter[0]}"
            _streams.setdefault(stream, []).append((msg_id, fields))
            return msg_id

        def _ping():
            elapsed = time.monotonic() - start
            if elapsed < offline_seconds:
                raise error
            return True

        mock.xadd.side_effect = _xadd
        mock.ping.side_effect = _ping
        mock.xreadgroup.side_effect = lambda *a, **kw: (
            (_ for _ in ()).throw(error)
            if time.monotonic() - start < offline_seconds
            else []
        )

        ctx = {
            "redis": mock,
            "offline_seconds": offline_seconds,
            "streams": _streams,
        }
        yield ctx
