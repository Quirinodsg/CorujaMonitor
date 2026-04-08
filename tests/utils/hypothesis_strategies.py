"""
Hypothesis strategies reutilizáveis — Coruja Monitor v3.0.
Gera instâncias válidas dos modelos Pydantic e estruturas auxiliares.
"""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from hypothesis import strategies as st

from core.spec.enums import (
    AlertStatus,
    EventSeverity,
    HostType,
    NodeType,
    Protocol,
    SensorStatus,
)
from core.spec.models import (
    Alert,
    Event,
    Host,
    Metric,
    Sensor,
    TopologyNode,
)

# ---------------------------------------------------------------------------
# Primitivas
# ---------------------------------------------------------------------------

uuid_st = st.builds(uuid4)

ipv4_st = st.tuples(
    st.integers(1, 254),
    st.integers(0, 255),
    st.integers(0, 255),
    st.integers(1, 254),
).map(lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}")

hostname_st = st.from_regex(r"[a-z][a-z0-9\-]{2,14}", fullmatch=True)

timestamp_st = st.floats(
    min_value=1_700_000_000, max_value=1_800_000_000, allow_nan=False, allow_infinity=False
).map(lambda ts: datetime.fromtimestamp(ts, tz=timezone.utc))

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

host_type_st = st.sampled_from(list(HostType))
protocol_st = st.sampled_from(list(Protocol))
sensor_status_st = st.sampled_from(list(SensorStatus))
event_severity_st = st.sampled_from(list(EventSeverity))
alert_status_st = st.sampled_from(list(AlertStatus))
node_type_st = st.sampled_from(list(NodeType))

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

threshold_st = st.fixed_dictionaries({
    "warning": st.floats(min_value=50.0, max_value=89.9, allow_nan=False, allow_infinity=False),
    "critical": st.floats(min_value=90.0, max_value=100.0, allow_nan=False, allow_infinity=False),
})

# ---------------------------------------------------------------------------
# Modelos Pydantic
# ---------------------------------------------------------------------------

host_st = st.builds(
    Host,
    hostname=hostname_st,
    ip_address=ipv4_st,
    type=host_type_st,
    tags=st.lists(st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnopqrstuvwxyz"), max_size=5),
)

sensor_st = st.builds(
    Sensor,
    host_id=uuid_st,
    type=st.sampled_from(["cpu", "memory", "disk", "network", "ping", "http", "process"]),
    protocol=protocol_st,
    interval=st.integers(min_value=10, max_value=300),
    timeout=st.integers(min_value=5, max_value=60),
    retries=st.integers(min_value=1, max_value=5),
    thresholds=threshold_st,
)

metric_st = st.builds(
    Metric,
    sensor_id=uuid_st,
    host_id=uuid_st,
    value=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    unit=st.sampled_from(["%", "MB", "ms", "bytes/s", "count"]),
    timestamp=timestamp_st,
    status=sensor_status_st,
)

event_st = st.builds(
    Event,
    host_id=uuid_st,
    type=st.sampled_from(["cpu_warning", "cpu_critical", "disk_warning", "disk_critical", "ping_down", "recovery"]),
    severity=event_severity_st,
    timestamp=timestamp_st,
    description=st.text(min_size=5, max_size=100),
)

alert_st = st.builds(
    Alert,
    title=st.text(min_size=5, max_size=80),
    severity=event_severity_st,
    status=alert_status_st,
    affected_hosts=st.lists(uuid_st, min_size=1, max_size=10),
    event_ids=st.lists(uuid_st, min_size=1, max_size=20),
)

topology_node_st = st.builds(
    TopologyNode,
    type=node_type_st,
    parent_id=st.one_of(st.none(), uuid_st),
    children_ids=st.lists(uuid_st, max_size=5),
)

# ---------------------------------------------------------------------------
# DAG strategy — gera nós + arestas sem ciclo
# ---------------------------------------------------------------------------

@st.composite
def dag_st(draw, min_nodes=2, max_nodes=15):
    """
    Gera um DAG válido: lista de nós e lista de arestas (parent, child)
    garantindo ausência de ciclos via ordenação topológica.
    """
    n = draw(st.integers(min_value=min_nodes, max_value=max_nodes))
    nodes = [f"sensor_{i}" for i in range(n)]
    edges = []
    # Arestas só de índice menor → maior garante DAG
    max_edges = min(n * 2, n * (n - 1) // 2)
    num_edges = draw(st.integers(min_value=0, max_value=max_edges))
    possible = [(nodes[i], nodes[j]) for i in range(n) for j in range(i + 1, n)]
    if possible:
        chosen = draw(
            st.lists(
                st.sampled_from(possible),
                min_size=0,
                max_size=min(num_edges, len(possible)),
                unique=True,
            )
        )
        edges = chosen
    return nodes, edges


# ---------------------------------------------------------------------------
# DSL source strategy — gera source DSL válido
# ---------------------------------------------------------------------------

@st.composite
def dsl_source_st(draw):
    """Gera um source DSL válido para o compilador."""
    sensor_name = draw(st.from_regex(r"[A-Z][a-zA-Z0-9_]{2,12}", fullmatch=True))
    protocol = draw(protocol_st)
    interval = draw(st.integers(min_value=10, max_value=300))
    warning = draw(st.floats(min_value=50.0, max_value=89.0, allow_nan=False, allow_infinity=False))
    critical = draw(st.floats(min_value=90.0, max_value=100.0, allow_nan=False, allow_infinity=False))

    source = (
        f"sensor {sensor_name} {{\n"
        f"  protocol {protocol.value}\n"
        f"  interval {interval}\n"
        f"  warning {warning:.1f}\n"
        f"  critical {critical:.1f}\n"
        f"}}\n"
    )
    return source
