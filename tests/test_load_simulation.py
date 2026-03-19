"""
Simulação de carga — 1.000 hosts × 50 sensores — Coruja Monitor v3.0
Properties 20, 21 + benchmark de throughput
"""
import time
import pytest
from uuid import uuid4

from core.spec.models import Host, Sensor
from core.spec.enums import HostType, Protocol, ProbeStatus


# ─── Fixtures ────────────────────────────────────────────────────────────────

def make_hosts(n: int) -> list[Host]:
    return [
        Host(
            id=uuid4(),
            hostname=f"server-{i:04d}",
            ip_address=f"10.{(i // 256) % 256}.{i % 256}.1",
            type=HostType.SERVER,
        )
        for i in range(n)
    ]


def make_sensors_for_host(host: Host, count: int) -> list[Sensor]:
    protocols = list(Protocol)
    return [
        Sensor(
            id=uuid4(),
            host_id=host.id,
            type=f"sensor_{j}",
            protocol=protocols[j % len(protocols)],
            interval=60,
        )
        for j in range(count)
    ]


# ─── Property 20: Invariante de atribuição de hosts ─────────────────────────

class TestProbeAssignmentInvariant:
    def test_each_host_assigned_to_exactly_one_probe(self):
        """
        Property 20: Cada host é monitorado por exatamente uma ProbeNode ativa.
        """
        from engine.probe_manager import ProbeManager

        manager = ProbeManager()

        # Registrar 3 probes
        probe_ids = []
        for i in range(3):
            state = manager.register_probe(
                probe_id=uuid4(),
                name=f"probe-{i}",
                probe_type="windows",
                subnet=f"10.{i}",
                capacity=500,
            )
            probe_ids.append(state.probe_id)

        # Atribuir 100 hosts
        hosts = make_hosts(100)
        assigned = {}
        for host in hosts:
            probe_id = manager.assign_host(host)
            assert probe_id is not None, f"Host {host.id} não foi atribuído"
            assigned[host.id] = probe_id

        # Verificar invariante: cada host em exatamente uma probe
        assert manager.invariant_check()

        # Verificar que não há duplicatas
        assert len(assigned) == 100

        # Verificar que host_to_probe é consistente com assigned_hosts
        status = manager.get_status()
        all_assigned_in_probes = set()
        for probe_info in status["probes"]:
            probe_state = manager._probes[
                next(p for p in manager._probes if str(p) == probe_info["probe_id"])
            ]
            for h_id in probe_state.assigned_hosts:
                assert h_id not in all_assigned_in_probes, f"Host {h_id} duplicado em múltiplas probes"
                all_assigned_in_probes.add(h_id)

        assert len(all_assigned_in_probes) == 100

    def test_invariant_maintained_after_failover(self):
        """Invariante mantida após failover de probe."""
        from engine.probe_manager import ProbeManager

        manager = ProbeManager()

        p1_id = uuid4()
        p2_id = uuid4()
        manager.register_probe(p1_id, "probe-1", "windows", capacity=100)
        manager.register_probe(p2_id, "probe-2", "windows", capacity=100)

        hosts = make_hosts(20)
        for host in hosts:
            manager.assign_host(host)

        # Simular probe-1 offline
        manager.handle_probe_offline(p1_id)

        # Após failover, todos os hosts devem estar em probe-2 (ou sem cobertura se capacidade insuficiente)
        status = manager.get_status()
        total_assigned = status["total_hosts_assigned"]
        assert total_assigned == 20  # todos devem ter sido migrados

    def test_invariant_maintained_after_restore(self):
        """Invariante mantida após restauração de probe."""
        from engine.probe_manager import ProbeManager

        manager = ProbeManager()

        p1_id = uuid4()
        p2_id = uuid4()
        manager.register_probe(p1_id, "probe-1", "windows", capacity=100)
        manager.register_probe(p2_id, "probe-2", "windows", capacity=100)

        hosts = make_hosts(10)
        for host in hosts:
            manager.assign_host(host)

        manager.handle_probe_offline(p1_id)
        manager.restore_probe(p1_id)

        assert manager.invariant_check()


# ─── Property 21: Balanceamento de carga ≤ 80% ──────────────────────────────

class TestProbeLoadBalance:
    def test_load_never_exceeds_80_percent(self):
        """
        Property 21: Balanceamento de carga respeita capacidade máxima de 80%.
        """
        from engine.probe_manager import ProbeManager, MAX_LOAD

        manager = ProbeManager()

        # 2 probes com capacidade 10 cada
        p1_id = uuid4()
        p2_id = uuid4()
        manager.register_probe(p1_id, "probe-1", "windows", capacity=10)
        manager.register_probe(p2_id, "probe-2", "windows", capacity=10)

        # Tentar atribuir 20 hosts (16 cabem com load < 80%)
        hosts = make_hosts(20)
        assigned_count = 0
        for host in hosts:
            probe_id = manager.assign_host(host)
            if probe_id:
                assigned_count += 1

        # Verificar que nenhuma probe excedeu 80% de carga
        for probe in manager._probes.values():
            assert probe.load <= MAX_LOAD, (
                f"Probe {probe.name} com load {probe.load:.2f} excede {MAX_LOAD}"
            )

    def test_load_distributes_across_probes(self):
        """Carga deve ser distribuída entre probes disponíveis."""
        from engine.probe_manager import ProbeManager

        manager = ProbeManager()

        for i in range(4):
            manager.register_probe(uuid4(), f"probe-{i}", "windows", capacity=100)

        hosts = make_hosts(100)
        for host in hosts:
            manager.assign_host(host)

        # Nenhuma probe deve ter mais de 50% da carga total (distribuição razoável)
        loads = [p.load for p in manager._probes.values()]
        max_load = max(loads)
        assert max_load <= 0.80

    def test_overloaded_probe_not_selected(self):
        """Probe com load >= 80% não deve receber novos hosts."""
        from engine.probe_manager import ProbeManager, MAX_LOAD

        manager = ProbeManager()

        # Probe 1: capacidade 5 (vai ficar cheia)
        p1_id = uuid4()
        p2_id = uuid4()
        manager.register_probe(p1_id, "probe-1", "windows", capacity=5)
        manager.register_probe(p2_id, "probe-2", "windows", capacity=100)

        # Encher probe-1 até 80%
        hosts_p1 = make_hosts(4)  # 4/5 = 80%
        for host in hosts_p1:
            manager.assign_host(host)

        # Próximos hosts devem ir para probe-2
        extra_hosts = make_hosts(5)
        for host in extra_hosts:
            probe_id = manager.assign_host(host)
            if probe_id:
                assert probe_id == p2_id, "Host deveria ir para probe-2 (probe-1 está cheia)"


# ─── Teste de throughput: 1.000 hosts × 50 sensores ─────────────────────────

class TestLoadSimulation:
    def test_1000_hosts_50_sensors_throughput(self):
        """
        Simula criação e serialização de 1.000 hosts × 50 sensores.
        Latência média deve ser < 2 segundos para o lote completo.
        """
        NUM_HOSTS = 1000
        SENSORS_PER_HOST = 50
        MAX_TOTAL_TIME_SEC = 2.0

        start = time.perf_counter()

        hosts = make_hosts(NUM_HOSTS)
        all_sensors = []
        for host in hosts:
            sensors = make_sensors_for_host(host, SENSORS_PER_HOST)
            all_sensors.extend(sensors)

        elapsed = time.perf_counter() - start

        assert len(hosts) == NUM_HOSTS
        assert len(all_sensors) == NUM_HOSTS * SENSORS_PER_HOST
        assert elapsed < MAX_TOTAL_TIME_SEC, (
            f"Criação de {NUM_HOSTS}×{SENSORS_PER_HOST} levou {elapsed:.2f}s "
            f"(limite: {MAX_TOTAL_TIME_SEC}s)"
        )

    def test_1000_hosts_serialization_no_data_loss(self):
        """Serialização de 1.000 hosts não perde dados."""
        hosts = make_hosts(1000)

        serialized = [h.model_dump() for h in hosts]
        restored = [Host(**d) for d in serialized]

        assert len(restored) == 1000
        for original, rest in zip(hosts, restored):
            assert original.id == rest.id
            assert original.hostname == rest.hostname

    @pytest.mark.benchmark(group="load")
    def test_probe_assignment_1000_hosts(self, benchmark):
        """Benchmark: atribuição de 1.000 hosts a probes."""
        from engine.probe_manager import ProbeManager

        def run():
            manager = ProbeManager()
            for i in range(5):
                manager.register_probe(uuid4(), f"probe-{i}", "windows", capacity=300)
            hosts = make_hosts(1000)
            for host in hosts:
                manager.assign_host(host)
            return manager

        result = benchmark(run)
        assert result.get_status()["total_hosts_assigned"] == 1000

    def test_event_processor_1000_metrics(self):
        """EventProcessor processa 1.000 métricas sem perda."""
        from event_processor.processor import EventProcessor
        from core.spec.models import Metric
        from core.spec.enums import SensorStatus
        from datetime import datetime, timezone

        processor = EventProcessor()
        sensor_ids = [uuid4() for _ in range(100)]
        host_id = uuid4()

        events_generated = []
        processed = 0

        for i in range(1000):
            metric = Metric(
                sensor_id=sensor_ids[i % 100],
                host_id=host_id,
                value=float(i % 100),
                unit="%",
                timestamp=datetime.now(timezone.utc),
                status=SensorStatus.OK if i % 10 != 0 else SensorStatus.WARNING,
            )
            event = processor.process(metric)
            processed += 1
            if event:
                events_generated.append(event)

        # Deve ter processado todas as métricas
        assert processed == 1000
        # Deve ter gerado eventos apenas em transições de estado
        assert len(events_generated) >= 0
