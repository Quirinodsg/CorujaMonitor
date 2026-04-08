"""
Fixtures globais da suite de testes — Coruja Monitor v3.0.
Fornece mocks isolados para Redis, PostgreSQL e utilitários compartilhados.
"""
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Optional
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# ---------------------------------------------------------------------------
# Mock Redis com suporte a Streams (XADD / XREADGROUP / XACK)
# ---------------------------------------------------------------------------

class MockRedisStream:
    """Implementação mínima de Redis Streams para testes."""

    def __init__(self):
        self._streams: dict[str, list[tuple[str, dict]]] = defaultdict(list)
        self._groups: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._pending: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        self._counter = 0

    def xadd(self, stream: str, fields: dict, maxlen: Optional[int] = None, **kwargs) -> str:
        self._counter += 1
        msg_id = f"{int(time.time() * 1000)}-{self._counter}"
        self._streams[stream].append((msg_id, fields))
        if maxlen and len(self._streams[stream]) > maxlen:
            self._streams[stream] = self._streams[stream][-maxlen:]
        return msg_id

    def xreadgroup(
        self, groupname: str, consumername: str, streams: dict, count: Optional[int] = None, block: Optional[int] = None, **kwargs
    ) -> list:
        results = []
        for stream_key, last_id in streams.items():
            entries = self._streams.get(stream_key, [])
            offset = self._groups[stream_key][groupname]
            pending = entries[offset: offset + (count or 10)]
            if pending:
                self._groups[stream_key][groupname] = offset + len(pending)
                for msg_id, fields in pending:
                    self._pending[stream_key][groupname].append(msg_id)
                results.append((stream_key, pending))
        return results

    def xack(self, stream: str, groupname: str, *msg_ids: str) -> int:
        acked = 0
        pending = self._pending[stream].get(groupname, [])
        for mid in msg_ids:
            if mid in pending:
                pending.remove(mid)
                acked += 1
        return acked

    def xgroup_create(self, stream: str, groupname: str, id: str = "0", mkstream: bool = False, **kwargs):
        if mkstream and stream not in self._streams:
            self._streams[stream] = []
        self._groups[stream][groupname] = 0

    def xlen(self, stream: str) -> int:
        return len(self._streams.get(stream, []))

    def xrange(self, stream: str, min: str = "-", max: str = "+", count: Optional[int] = None) -> list:
        entries = self._streams.get(stream, [])
        if count:
            entries = entries[:count]
        return entries

    def pipeline(self, **kwargs):
        return MockRedisPipeline(self)

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> Optional[str]:
        return None

    def set(self, key: str, value: str, **kwargs) -> bool:
        return True

    def delete(self, *keys: str) -> int:
        return len(keys)


class MockRedisPipeline:
    """Pipeline mock que acumula comandos e executa em batch."""

    def __init__(self, redis: MockRedisStream):
        self._redis = redis
        self._commands: list[tuple[str, tuple, dict]] = []

    def xadd(self, stream: str, fields: dict, **kwargs):
        self._commands.append(("xadd", (stream, fields), kwargs))
        return self

    def execute(self) -> list:
        results = []
        for cmd, args, kwargs in self._commands:
            if cmd == "xadd":
                results.append(self._redis.xadd(*args, **kwargs))
        self._commands.clear()
        return results

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_redis():
    """Redis mock com suporte a Streams (XADD, XREADGROUP, XACK)."""
    return MockRedisStream()


@pytest.fixture
def mock_db():
    """SQLAlchemy session com SQLite in-memory."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Criar tabela mínima de métricas para testes
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS metrics_ts (
                time TIMESTAMP,
                sensor_id TEXT,
                host_id TEXT,
                value REAL,
                unit TEXT,
                status TEXT
            )
        """))
        conn.commit()

    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def event_simulator():
    """Instância do EventSimulator para geração de dados sintéticos."""
    from tests.utils.event_simulator import EventSimulator
    return EventSimulator()


@pytest.fixture
def topology_simulator():
    """Instância do TopologySimulator para criação de topologias."""
    from tests.utils.topology_simulator import TopologySimulator
    return TopologySimulator()


@pytest.fixture
def chaos_engine():
    """Instância do ChaosEngine para simulação de falhas."""
    from tests.utils.chaos_engine import ChaosEngine
    return ChaosEngine()
