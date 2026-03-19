"""
Testes da Fase 1 — Spec Central (core/spec/)
Cobre: Property 1 (round-trip), Property 2 (validação campos obrigatórios)
"""
import json
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from core.spec import (
    Host, Sensor, Metric, Event, Alert, TopologyNode, ProbeNode,
    HostType, Protocol, SensorStatus, EventSeverity, AlertStatus,
    NodeType, ProbeStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_host(**kwargs):
    defaults = dict(hostname="srv01", ip_address="192.168.1.1", type=HostType.SERVER)
    defaults.update(kwargs)
    return Host(**defaults)


def make_sensor(**kwargs):
    defaults = dict(host_id=uuid4(), type="cpu", protocol=Protocol.WMI, interval=60)
    defaults.update(kwargs)
    return Sensor(**defaults)


def make_metric(**kwargs):
    defaults = dict(
        sensor_id=uuid4(), host_id=uuid4(), value=42.0,
        unit="%", timestamp=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Metric(**defaults)


def make_event(**kwargs):
    defaults = dict(
        host_id=uuid4(), type="high_cpu",
        severity=EventSeverity.WARNING,
        timestamp=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Event(**defaults)


def make_alert(**kwargs):
    defaults = dict(title="CPU alta", severity=EventSeverity.CRITICAL)
    defaults.update(kwargs)
    return Alert(**defaults)


def make_topology_node(**kwargs):
    defaults = dict(type=NodeType.SERVER)
    defaults.update(kwargs)
    return TopologyNode(**defaults)


def make_probe_node(**kwargs):
    defaults = dict(name="probe01", location="datacenter", capacity=100)
    defaults.update(kwargs)
    return ProbeNode(**defaults)


# ---------------------------------------------------------------------------
# Property 1: Round-trip de serialização JSON
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_host_roundtrip(self):
        obj = make_host(tags=["prod", "linux"], metadata={"rack": "A1"})
        restored = Host.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert restored.hostname == obj.hostname
        assert restored.tags == obj.tags
        assert restored.metadata == obj.metadata

    def test_sensor_roundtrip(self):
        obj = make_sensor(thresholds={"warning": 80, "critical": 95})
        restored = Sensor.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert restored.thresholds == obj.thresholds

    def test_metric_roundtrip(self):
        obj = make_metric(value=99.9, status=SensorStatus.CRITICAL)
        restored = Metric.model_validate_json(obj.model_dump_json())
        assert restored.value == obj.value
        assert restored.status == obj.status

    def test_event_roundtrip(self):
        obj = make_event(description="CPU acima de 95%")
        restored = Event.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert restored.description == obj.description

    def test_alert_roundtrip(self):
        h1, h2 = uuid4(), uuid4()
        obj = make_alert(affected_hosts=[h1, h2], root_cause="switch_down")
        restored = Alert.model_validate_json(obj.model_dump_json())
        assert restored.id == obj.id
        assert len(restored.affected_hosts) == 2

    def test_topology_node_roundtrip(self):
        parent = make_topology_node(type=NodeType.SWITCH)
        child = make_topology_node(type=NodeType.SERVER, parent_id=parent.id)
        restored = TopologyNode.model_validate_json(child.model_dump_json())
        assert restored.parent_id == parent.id

    def test_probe_node_roundtrip(self):
        hosts = [uuid4(), uuid4()]
        obj = make_probe_node(assigned_hosts=hosts, status=ProbeStatus.ONLINE)
        restored = ProbeNode.model_validate_json(obj.model_dump_json())
        assert restored.status == obj.status
        assert len(restored.assigned_hosts) == 2

    def test_dict_roundtrip_all_models(self):
        """Serializar para dict e recriar deve produzir objeto equivalente."""
        models = [
            make_host(), make_sensor(), make_metric(), make_event(),
            make_alert(), make_topology_node(), make_probe_node(),
        ]
        for obj in models:
            cls = type(obj)
            restored = cls.model_validate(obj.model_dump())
            assert restored.model_dump() == obj.model_dump(), f"Round-trip falhou para {cls.__name__}"


# ---------------------------------------------------------------------------
# Property 2: Validação de campos obrigatórios
# ---------------------------------------------------------------------------

class TestValidation:
    def test_host_missing_hostname(self):
        with pytest.raises(ValidationError):
            Host(ip_address="1.2.3.4", type=HostType.SERVER)

    def test_host_missing_ip(self):
        with pytest.raises(ValidationError):
            Host(hostname="srv", type=HostType.SERVER)

    def test_host_missing_type(self):
        with pytest.raises(ValidationError):
            Host(hostname="srv", ip_address="1.2.3.4")

    def test_sensor_missing_host_id(self):
        with pytest.raises(ValidationError):
            Sensor(type="cpu", protocol=Protocol.WMI, interval=60)

    def test_sensor_missing_interval(self):
        with pytest.raises(ValidationError):
            Sensor(host_id=uuid4(), type="cpu", protocol=Protocol.WMI)

    def test_sensor_invalid_protocol(self):
        with pytest.raises(ValidationError):
            Sensor(host_id=uuid4(), type="cpu", protocol="ftp", interval=60)

    def test_metric_missing_value(self):
        with pytest.raises(ValidationError):
            Metric(sensor_id=uuid4(), host_id=uuid4(), unit="%",
                   timestamp=datetime.now(timezone.utc))

    def test_event_missing_severity(self):
        with pytest.raises(ValidationError):
            Event(host_id=uuid4(), type="high_cpu",
                  timestamp=datetime.now(timezone.utc))

    def test_alert_missing_title(self):
        with pytest.raises(ValidationError):
            Alert(severity=EventSeverity.CRITICAL)

    def test_probe_node_missing_capacity(self):
        with pytest.raises(ValidationError):
            ProbeNode(name="p1", location="dc1")

    def test_host_invalid_type_enum(self):
        with pytest.raises(ValidationError):
            Host(hostname="srv", ip_address="1.2.3.4", type="mainframe")


# ---------------------------------------------------------------------------
# Testes de campos opcionais e defaults
# ---------------------------------------------------------------------------

class TestDefaults:
    def test_host_defaults(self):
        h = make_host()
        assert h.tags == []
        assert h.metadata == {}
        assert h.id is not None
        assert h.created_at is not None

    def test_sensor_defaults(self):
        s = make_sensor()
        assert s.timeout == 30
        assert s.retries == 3
        assert s.query is None
        assert s.thresholds == {}

    def test_metric_default_status(self):
        m = make_metric()
        assert m.status == SensorStatus.UNKNOWN.value

    def test_alert_default_status(self):
        a = make_alert()
        assert a.status == AlertStatus.OPEN.value

    def test_probe_node_default_status(self):
        p = make_probe_node()
        assert p.status == ProbeStatus.OFFLINE.value

    def test_topology_node_optional_parent(self):
        n = make_topology_node()
        assert n.parent_id is None
        assert n.children_ids == []
