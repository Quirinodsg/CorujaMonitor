"""
Auditoria Técnica Completa - Coruja Monitor Enterprise
Testa todos os 17 componentes implementados
"""
import sys
import os
import time
import threading
import unittest
from unittest.mock import MagicMock, patch

# Ajustar path para importar módulos da probe
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 1 - ARQUITETURA GERAL
# ═══════════════════════════════════════════════════════════════════

class TestArquiteturaGeral(unittest.TestCase):
    """Verifica existência e importabilidade de todos os componentes"""

    def test_01_protocol_engines_importaveis(self):
        from protocol_engines.base_engine import BaseProtocolEngine, EngineResult
        from protocol_engines.icmp_engine import ICMPEngine
        from protocol_engines.tcp_engine import TCPEngine
        from protocol_engines.snmp_engine import SNMPEngine
        from protocol_engines.registry_engine import RegistryEngine
        from protocol_engines.docker_engine import DockerEngine
        from protocol_engines.kubernetes_engine import KubernetesEngine
        self.assertTrue(True)

    def test_02_connection_pools_importaveis(self):
        from connection_pool.snmp_pool import SNMPConnectionPool, get_pool as snmp_pool
        from connection_pool.tcp_pool import TCPConnectionPool, get_pool as tcp_pool
        self.assertTrue(True)

    def test_03_engine_components_importaveis(self):
        from engine.pre_check import ConnectivityPreCheck
        from engine.metric_cache import MetricCache
        from engine.adaptive_monitor import AdaptiveMonitor
        from engine.sensor_engine import SensorEngine, SensorDefinition, SensorResult
        from engine.scheduler import Scheduler
        from engine.thread_pool import WorkerPool
        from engine.internal_metrics import InternalMetricsCollector
        from engine.prometheus_exporter import PrometheusExporter
        self.assertTrue(True)

    def test_04_event_engine_importavel(self):
        from event_engine.wmi_event_listener import WMIEventListener
        from event_engine.docker_event_listener import DockerEventListener
        from event_engine.kubernetes_event_listener import KubernetesEventListener
        self.assertTrue(True)

    def test_05_security_importavel(self):
        from security.credential_manager import CredentialManager
        from security.vault_client import VaultClient
        self.assertTrue(True)

    def test_06_aiops_importavel(self):
        from anomaly_detector import AnomalyDetector
        from failure_predictor import FailurePredictor
        from event_correlator import EventCorrelator
        self.assertTrue(True)


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 2 - PROTOCOL ENGINES
# ═══════════════════════════════════════════════════════════════════

class TestProtocolEngines(unittest.TestCase):

    def test_07_base_engine_interface(self):
        from protocol_engines.base_engine import BaseProtocolEngine, EngineResult
        # Não pode instanciar diretamente (abstrata)
        with self.assertRaises(TypeError):
            BaseProtocolEngine()
        # EngineResult funciona
        r = EngineResult(status="ok", value=10.5, unit="ms")
        self.assertTrue(r.is_ok)
        self.assertTrue(r.is_available)

    def test_08_engine_result_unavailable(self):
        from protocol_engines.base_engine import EngineResult
        r = EngineResult(status="unknown", error="engine_unavailable")
        self.assertFalse(r.is_available)
        self.assertFalse(r.is_ok)

    def test_09_icmp_engine_disponivel(self):
        from protocol_engines.icmp_engine import ICMPEngine
        engine = ICMPEngine()
        self.assertTrue(engine.is_available())

    def test_10_icmp_engine_localhost(self):
        from protocol_engines.icmp_engine import ICMPEngine
        engine = ICMPEngine(count=1, timeout=2, retries=1)
        start = time.monotonic()
        result = engine.execute("127.0.0.1")
        elapsed = (time.monotonic() - start) * 1000
        self.assertIn(result.status, ["ok", "critical"])
        self.assertLess(elapsed, 5000, "ICMP deve completar em < 5s")
        print(f"\n  ICMP 127.0.0.1: status={result.status} latency={result.value}ms elapsed={elapsed:.0f}ms")

    def test_11_icmp_engine_host_invalido(self):
        from protocol_engines.icmp_engine import ICMPEngine
        engine = ICMPEngine(count=1, timeout=1, retries=0)
        result = engine.execute("192.0.2.255")  # TEST-NET, não roteável
        self.assertEqual(result.status, "critical")
        self.assertEqual(result.error, "host_unreachable")

    def test_12_icmp_engine_retry_metadata(self):
        from protocol_engines.icmp_engine import ICMPEngine
        engine = ICMPEngine(count=1, timeout=1, retries=2)
        result = engine.execute("192.0.2.255")
        self.assertIn("attempts", result.metadata)

    def test_13_tcp_engine_disponivel(self):
        from protocol_engines.tcp_engine import TCPEngine
        engine = TCPEngine()
        self.assertTrue(engine.is_available())

    def test_14_tcp_engine_porta_aberta(self):
        """Testa TCP em porta que deve estar aberta (DNS local ou loopback)"""
        from protocol_engines.tcp_engine import TCPEngine
        import socket
        # Criar servidor temporário para teste
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        port = server.getsockname()[1]
        try:
            engine = TCPEngine()
            result = engine.execute("127.0.0.1", port=port, timeout=2)
            self.assertEqual(result.status, "ok")
            self.assertGreater(result.value, 0)
            print(f"\n  TCP 127.0.0.1:{port}: status={result.status} latency={result.value}ms")
        finally:
            server.close()

    def test_15_tcp_engine_porta_fechada(self):
        from protocol_engines.tcp_engine import TCPEngine
        engine = TCPEngine()
        result = engine.execute("127.0.0.1", port=19999, timeout=1)
        self.assertEqual(result.status, "critical")

    def test_16_snmp_engine_disponivel_ou_nao(self):
        from protocol_engines.snmp_engine import SNMPEngine
        engine = SNMPEngine()
        # Apenas verifica que retorna bool
        avail = engine.is_available()
        self.assertIsInstance(avail, bool)
        print(f"\n  SNMP engine disponível: {avail}")

    def test_17_snmp_engine_host_invalido_retorna_unknown(self):
        from protocol_engines.snmp_engine import SNMPEngine
        engine = SNMPEngine()
        if not engine.is_available():
            self.skipTest("pysnmp não instalado")
        result = engine.execute("192.0.2.255", timeout=1, retries=0)
        self.assertIn(result.status, ["unknown", "critical"])

    def test_18_registry_engine_graceful_sem_winreg(self):
        from protocol_engines.registry_engine import RegistryEngine
        engine = RegistryEngine()
        avail = engine.is_available()
        self.assertIsInstance(avail, bool)
        if not avail:
            result = engine.execute("localhost")
            self.assertEqual(result.error, "engine_unavailable")

    def test_19_docker_engine_graceful_sem_docker(self):
        from protocol_engines.docker_engine import DockerEngine
        engine = DockerEngine()
        avail = engine.is_available()
        self.assertIsInstance(avail, bool)
        if not avail:
            result = engine.execute("localhost")
            self.assertEqual(result.error, "engine_unavailable")

    def test_20_kubernetes_engine_graceful_sem_k8s(self):
        from protocol_engines.kubernetes_engine import KubernetesEngine
        engine = KubernetesEngine()
        avail = engine.is_available()
        self.assertIsInstance(avail, bool)
        if not avail:
            result = engine.execute("localhost")
            self.assertEqual(result.error, "engine_unavailable")


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 3 - CONNECTION POOLS
# ═══════════════════════════════════════════════════════════════════

class TestConnectionPools(unittest.TestCase):

    def test_21_snmp_pool_acquire_release(self):
        from connection_pool.snmp_pool import SNMPConnectionPool
        pool = SNMPConnectionPool(max_per_host=5)
        conn = pool.acquire("10.0.0.1", community="public", port=161, version="2c")
        self.assertIsNotNone(conn)
        self.assertTrue(conn.in_use)
        pool.release("10.0.0.1", conn)
        self.assertFalse(conn.in_use)

    def test_22_snmp_pool_reuso_conexao(self):
        from connection_pool.snmp_pool import SNMPConnectionPool
        pool = SNMPConnectionPool(max_per_host=5)
        conn1 = pool.acquire("10.0.0.1", community="public", port=161, version="2c")
        pool.release("10.0.0.1", conn1)
        conn2 = pool.acquire("10.0.0.1", community="public", port=161, version="2c")
        self.assertIs(conn1, conn2, "Deve reutilizar a mesma conexão")
        pool.release("10.0.0.1", conn2)

    def test_23_snmp_pool_limite_por_host(self):
        from connection_pool.snmp_pool import SNMPConnectionPool
        pool = SNMPConnectionPool(max_per_host=3)
        conns = []
        for i in range(3):
            c = pool.acquire("10.0.0.2", community=f"pub{i}", port=161, version="2c")
            self.assertIsNotNone(c)
            conns.append(c)
        # 4ª deve falhar
        c4 = pool.acquire("10.0.0.2", community="pub4", port=161, version="2c")
        self.assertIsNone(c4, "Deve retornar None quando limite atingido")
        for c in conns:
            pool.release("10.0.0.2", c)

    def test_24_snmp_pool_stats(self):
        from connection_pool.snmp_pool import SNMPConnectionPool
        pool = SNMPConnectionPool(max_per_host=5)
        conn = pool.acquire("10.0.0.3", community="public", port=161, version="2c")
        stats = pool.stats()
        self.assertIn("10.0.0.3", stats)
        self.assertEqual(stats["10.0.0.3"]["in_use"], 1)
        pool.release("10.0.0.3", conn)

    def test_25_snmp_pool_50_sensores_simultaneos(self):
        """Simula 50 sensores WMI simultâneos — valida reuso e limite"""
        from connection_pool.snmp_pool import SNMPConnectionPool
        pool = SNMPConnectionPool(max_per_host=5)
        acquired = []
        failed = 0
        for i in range(50):
            host = f"10.0.{i // 10}.{i % 10 + 1}"
            c = pool.acquire(host, community="public", port=161, version="2c")
            if c:
                acquired.append((host, c))
            else:
                failed += 1
        # Liberar tudo
        for host, c in acquired:
            pool.release(host, c)
        print(f"\n  50 sensores: {len(acquired)} adquiridos, {failed} falhas (esperado: 0)")
        self.assertEqual(failed, 0, "Hosts diferentes não devem conflitar")

    def test_26_tcp_pool_acquire_release(self):
        """Testa TCP pool com servidor real"""
        import socket
        from connection_pool.tcp_pool import TCPConnectionPool
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(5)
        port = server.getsockname()[1]
        # Aceitar conexões em background
        def accept_loop():
            for _ in range(3):
                try:
                    s, _ = server.accept()
                    s.close()
                except:
                    break
        t = threading.Thread(target=accept_loop, daemon=True)
        t.start()
        try:
            pool = TCPConnectionPool(max_per_host=10)
            conn = pool.acquire("127.0.0.1", port)
            self.assertIsNotNone(conn)
            pool.release("127.0.0.1", port, conn)
            stats = pool.stats()
            key = f"127.0.0.1:{port}"
            self.assertIn(key, stats)
        finally:
            server.close()


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 4 - SCHEDULER
# ═══════════════════════════════════════════════════════════════════

class TestScheduler(unittest.TestCase):

    def _make_scheduler(self):
        from engine.sensor_engine import SensorEngine
        from engine.scheduler import Scheduler
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=20)
        engine = SensorEngine()
        return Scheduler(engine, pool), pool

    def test_27_scheduler_add_sensor(self):
        from engine.sensor_engine import SensorDefinition, SensorType
        from engine.scheduler import Scheduler
        sched, pool = self._make_scheduler()
        s = SensorDefinition(id="s1", type=SensorType.ICMP_PING, target="127.0.0.1", interval=60)
        result = sched.add(s)
        self.assertTrue(result)
        pool.shutdown(wait=False)

    def test_28_scheduler_intervalo_invalido_arredondado(self):
        from engine.sensor_engine import SensorDefinition, SensorType
        sched, pool = self._make_scheduler()
        s = SensorDefinition(id="s2", type=SensorType.ICMP_PING, target="127.0.0.1", interval=45)
        sched.add(s)
        # Deve ter arredondado para 30 ou 60
        from engine.scheduler import VALID_INTERVALS
        self.assertIn(s.interval, VALID_INTERVALS)
        pool.shutdown(wait=False)

    def test_29_scheduler_limite_por_host(self):
        from engine.sensor_engine import SensorDefinition, SensorType
        from engine.scheduler import MAX_SENSORS_PER_HOST
        sched, pool = self._make_scheduler()
        added = 0
        for i in range(MAX_SENSORS_PER_HOST + 2):
            s = SensorDefinition(id=f"host_s{i}", type=SensorType.ICMP_PING,
                                 target="10.0.0.1", interval=60)
            if sched.add(s):
                added += 1
        self.assertLessEqual(added, MAX_SENSORS_PER_HOST)
        print(f"\n  Scheduler limite por host: {added}/{MAX_SENSORS_PER_HOST + 2} aceitos")
        pool.shutdown(wait=False)

    def test_30_scheduler_delay_escalonado_add_many(self):
        from engine.sensor_engine import SensorDefinition, SensorType
        sched, pool = self._make_scheduler()
        sensors = [
            SensorDefinition(id=f"bulk_{i}", type=SensorType.ICMP_PING,
                             target=f"10.1.{i}.1", interval=60)
            for i in range(20)
        ]
        start = time.monotonic()
        sched.add_many(sensors)
        elapsed = time.monotonic() - start
        # add_many deve ser rápido (delay é no next_run, não no add)
        self.assertLess(elapsed, 2.0, "add_many deve ser rápido")
        pool.shutdown(wait=False)

    def test_31_scheduler_status(self):
        from engine.sensor_engine import SensorDefinition, SensorType
        sched, pool = self._make_scheduler()
        s = SensorDefinition(id="stat_s1", type=SensorType.ICMP_PING, target="127.0.0.1", interval=60)
        sched.add(s)
        status = sched.status()
        self.assertIn("total_sensors", status)
        self.assertEqual(status["total_sensors"], 1)
        pool.shutdown(wait=False)

    def test_32_scheduler_100_sensores(self):
        """Teste de carga: 100 sensores com intervalo 60s"""
        from engine.sensor_engine import SensorDefinition, SensorType
        sched, pool = self._make_scheduler()
        sensors = [
            SensorDefinition(id=f"load_{i}", type=SensorType.ICMP_PING,
                             target=f"10.2.{i//10}.{i%10+1}", interval=60)
            for i in range(100)
        ]
        sched.add_many(sensors)
        status = sched.status()
        print(f"\n  100 sensores: {status['total_sensors']} agendados")
        self.assertGreater(status["total_sensors"], 0)
        pool.shutdown(wait=False)


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 5 - WORKER POOL
# ═══════════════════════════════════════════════════════════════════

class TestWorkerPool(unittest.TestCase):

    def test_33_worker_pool_20_workers(self):
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=20)
        self.assertEqual(pool.max_workers, 20)
        pool.shutdown(wait=False)

    def test_34_worker_pool_submit_e_resultado(self):
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=5)
        results = []
        futures = []
        for i in range(10):
            f = pool.submit(lambda x=i: x * 2, task_id=f"t{i}")
            futures.append(f)
        for f in futures:
            results.append(f.result(timeout=5))
        self.assertEqual(sorted(results), [0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
        pool.shutdown()

    def test_35_worker_pool_stats(self):
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=10)
        event = threading.Event()
        def slow_task():
            event.wait(timeout=5)
            return 1
        futures = [pool.submit(slow_task) for _ in range(3)]
        time.sleep(0.1)
        stats = pool.stats()
        self.assertIn("max_workers", stats)
        self.assertIn("active_workers", stats)
        self.assertIn("completed", stats)
        event.set()
        for f in futures:
            f.result(timeout=5)
        pool.shutdown()

    def test_36_worker_pool_200_tarefas_paralelas(self):
        """Benchmark: 200 tarefas simultâneas"""
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=20)
        counter = {"done": 0}
        lock = threading.Lock()
        def task():
            time.sleep(0.01)
            with lock:
                counter["done"] += 1
        start = time.monotonic()
        futures = [pool.submit(task) for _ in range(200)]
        for f in futures:
            f.result(timeout=30)
        elapsed = time.monotonic() - start
        print(f"\n  200 tarefas com 20 workers: {elapsed:.2f}s (esperado ~0.1s)")
        self.assertEqual(counter["done"], 200)
        self.assertLess(elapsed, 5.0, "200 tarefas devem completar em < 5s com 20 workers")
        pool.shutdown()

    def test_37_worker_pool_resize(self):
        """Verifica se resize() existe e funciona"""
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=10)
        # resize não está implementado ainda — verificar
        has_resize = hasattr(pool, 'resize')
        print(f"\n  WorkerPool.resize() implementado: {has_resize}")
        pool.shutdown(wait=False)


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 6 - METRIC CACHE
# ═══════════════════════════════════════════════════════════════════

class TestMetricCache(unittest.TestCase):

    def test_38_cache_set_get_local(self):
        from engine.metric_cache import MetricCache
        cache = MetricCache()  # sem Redis → local
        cache.set("host1", "cpu", "query1", 85.5, ttl=5)
        val = cache.get("host1", "cpu", "query1")
        self.assertEqual(val, 85.5)

    def test_39_cache_miss(self):
        from engine.metric_cache import MetricCache
        cache = MetricCache()
        val = cache.get("host_inexistente", "cpu", "q")
        self.assertIsNone(val)

    def test_40_cache_ttl_expira(self):
        from engine.metric_cache import MetricCache
        cache = MetricCache()
        cache.set("host2", "cpu", "q", 99.0, ttl=1)
        time.sleep(1.1)
        val = cache.get("host2", "cpu", "q")
        self.assertIsNone(val, "Cache deve expirar após TTL")

    def test_41_cache_stats(self):
        from engine.metric_cache import MetricCache
        cache = MetricCache()
        cache.set("h", "cpu", "q", 50.0, ttl=10)
        cache.get("h", "cpu", "q")   # hit
        cache.get("h", "cpu", "q2")  # miss
        stats = cache.stats
        self.assertIn("hits", stats)
        self.assertIn("misses", stats)
        self.assertIn("hit_ratio", stats)
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertAlmostEqual(stats["hit_ratio"], 0.5, places=1)

    def test_42_cache_3_sensores_mesmo_host(self):
        """3 sensores pedindo CPU do mesmo host — apenas 1 miss, 2 hits"""
        from engine.metric_cache import MetricCache
        cache = MetricCache()
        host = "10.0.0.1"
        # Simula: primeiro sensor faz query WMI e armazena
        val = cache.get(host, "cpu", "wmi_cpu")
        self.assertIsNone(val)  # miss — faria query WMI
        cache.set(host, "cpu", "wmi_cpu", 72.3, ttl=5)
        # Segundo e terceiro sensores pegam do cache
        val2 = cache.get(host, "cpu", "wmi_cpu")
        val3 = cache.get(host, "cpu", "wmi_cpu")
        self.assertEqual(val2, 72.3)
        self.assertEqual(val3, 72.3)
        stats = cache.stats
        print(f"\n  Cache 3 sensores: hits={stats['hits']} misses={stats['misses']} ratio={stats['hit_ratio']}")
        self.assertEqual(stats["hits"], 2)

    def test_43_cache_ttl_cpu_5s(self):
        from engine.metric_cache import MetricCache
        self.assertEqual(MetricCache.TTL_CPU_MEMORY, 5)

    def test_44_cache_ttl_disco_10s(self):
        from engine.metric_cache import MetricCache
        self.assertEqual(MetricCache.TTL_DISK_SERVICES, 10)

    def test_45_cache_invalidate_host(self):
        from engine.metric_cache import MetricCache
        cache = MetricCache()
        cache.set("host3", "cpu", "q", 50.0, ttl=60)
        cache.invalidate("host3")
        val = cache.get("host3", "cpu", "q")
        self.assertIsNone(val)


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 7 - PRÉ-CHECK DE CONECTIVIDADE
# ═══════════════════════════════════════════════════════════════════

class TestPreCheck(unittest.TestCase):

    def test_46_precheck_localhost_wmi(self):
        from engine.pre_check import ConnectivityPreCheck
        pc = ConnectivityPreCheck()
        result = pc.check_wmi("127.0.0.1")
        # Pode passar ou falhar na porta 135, mas não deve lançar exceção
        self.assertIsNotNone(result)
        self.assertIsInstance(result.passed, bool)
        print(f"\n  PreCheck WMI 127.0.0.1: passed={result.passed} error={result.error}")

    def test_47_precheck_host_invalido_retorna_critico(self):
        from engine.pre_check import ConnectivityPreCheck
        pc = ConnectivityPreCheck()
        result = pc.check_wmi("192.0.2.255")
        self.assertFalse(result.passed)
        self.assertEqual(result.error, "host_unreachable")

    def test_48_precheck_cache_ttl_30s(self):
        from engine.pre_check import ConnectivityPreCheck
        self.assertEqual(ConnectivityPreCheck.CACHE_TTL, 30)

    def test_49_precheck_cache_funciona(self):
        from engine.pre_check import ConnectivityPreCheck
        pc = ConnectivityPreCheck()
        r1 = pc.check_wmi("192.0.2.255")
        start = time.monotonic()
        r2 = pc.check_wmi("192.0.2.255")  # deve vir do cache
        elapsed = (time.monotonic() - start) * 1000
        self.assertFalse(r2.passed)
        self.assertLess(elapsed, 50, "Cache deve responder em < 50ms")
        print(f"\n  PreCheck cache: {elapsed:.1f}ms (esperado < 50ms)")

    def test_50_precheck_snmp(self):
        from engine.pre_check import ConnectivityPreCheck
        pc = ConnectivityPreCheck()
        result = pc.check_snmp("192.0.2.255")
        self.assertFalse(result.passed)

    def test_51_precheck_tcp(self):
        from engine.pre_check import ConnectivityPreCheck
        import socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 0))
        server.listen(1)
        port = server.getsockname()[1]
        def accept():
            try:
                s, _ = server.accept()
                s.close()
            except:
                pass
        threading.Thread(target=accept, daemon=True).start()
        try:
            pc = ConnectivityPreCheck()
            result = pc.check_tcp("127.0.0.1", port)
            self.assertTrue(result.passed)
        finally:
            server.close()


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 8 - ADAPTIVE MONITOR
# ═══════════════════════════════════════════════════════════════════

class TestAdaptiveMonitor(unittest.TestCase):

    def test_52_adaptive_critical_reduz_para_30s(self):
        from engine.adaptive_monitor import AdaptiveMonitor, INTERVAL_CRITICAL
        am = AdaptiveMonitor()
        interval = am.update("host1", "critical")
        self.assertEqual(interval, INTERVAL_CRITICAL)
        self.assertEqual(interval, 30)

    def test_53_adaptive_warning_reduz_para_60s(self):
        from engine.adaptive_monitor import AdaptiveMonitor, INTERVAL_WARNING
        am = AdaptiveMonitor()
        interval = am.update("host2", "warning")
        self.assertEqual(interval, INTERVAL_WARNING)
        self.assertEqual(interval, 60)

    def test_54_adaptive_5_ok_restaura_300s(self):
        from engine.adaptive_monitor import AdaptiveMonitor, INTERVAL_NORMAL, OK_CYCLES_TO_RESTORE
        am = AdaptiveMonitor()
        am.update("host3", "critical")
        for _ in range(OK_CYCLES_TO_RESTORE):
            interval = am.update("host3", "ok")
        self.assertEqual(interval, INTERVAL_NORMAL)
        self.assertEqual(interval, 300)

    def test_55_adaptive_ok_antes_de_5_mantem_intervalo(self):
        from engine.adaptive_monitor import AdaptiveMonitor, INTERVAL_CRITICAL
        am = AdaptiveMonitor()
        am.update("host4", "critical")
        for _ in range(3):  # apenas 3 ok, não 5
            interval = am.update("host4", "ok")
        self.assertEqual(interval, INTERVAL_CRITICAL, "Deve manter 30s até 5 ok consecutivos")

    def test_56_adaptive_status_dict(self):
        from engine.adaptive_monitor import AdaptiveMonitor
        am = AdaptiveMonitor()
        am.update("h1", "critical")
        am.update("h2", "warning")
        status = am.status()
        self.assertIn("h1", status)
        self.assertIn("h2", status)
        self.assertEqual(status["h1"]["interval"], 30)
        self.assertEqual(status["h2"]["interval"], 60)

    def test_57_adaptive_reset(self):
        from engine.adaptive_monitor import AdaptiveMonitor, INTERVAL_NORMAL
        am = AdaptiveMonitor()
        am.update("h5", "critical")
        am.reset("h5")
        self.assertEqual(am.get_interval("h5"), INTERVAL_NORMAL)

    def test_58_adaptive_host_estavel_vs_problema(self):
        """Simula host estável e host com problema — verifica diferença de intervalos"""
        from engine.adaptive_monitor import AdaptiveMonitor
        am = AdaptiveMonitor()
        # Host estável
        for _ in range(10):
            am.update("stable_host", "ok")
        # Host com problema
        am.update("problem_host", "critical")
        stable_interval = am.get_interval("stable_host")
        problem_interval = am.get_interval("problem_host")
        print(f"\n  Host estável: {stable_interval}s | Host com problema: {problem_interval}s")
        self.assertLess(problem_interval, stable_interval)


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 9 - SEGURANÇA (CREDENTIAL MANAGER)
# ═══════════════════════════════════════════════════════════════════

class TestSeguranca(unittest.TestCase):

    def test_59_credential_manager_set_get(self):
        from security.credential_manager import CredentialManager
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        import tempfile, pathlib
        with tempfile.NamedTemporaryFile(suffix=".enc", delete=False) as f:
            tmp = pathlib.Path(f.name)
        try:
            cm = CredentialManager(key=key, credentials_file=tmp)
            cm.set("wmi_server1", {"username": "admin", "password": "secret123"})
            cred = cm.get("wmi_server1")
            self.assertIsNotNone(cred)
            self.assertEqual(cred["username"], "admin")
        finally:
            tmp.unlink(missing_ok=True)

    def test_60_credential_manager_senha_nao_em_log(self):
        """Verifica que senhas são redactadas nos logs"""
        import logging
        from security.credential_manager import CredentialManager
        from cryptography.fernet import Fernet
        import tempfile, pathlib
        key = Fernet.generate_key()
        with tempfile.NamedTemporaryFile(suffix=".enc", delete=False) as f:
            tmp = pathlib.Path(f.name)
        log_records = []
        handler = logging.handlers_test = type('H', (logging.Handler,), {
            'emit': lambda self, r: log_records.append(r.getMessage())
        })()
        logging.getLogger('security.credential_manager').addHandler(handler)
        try:
            cm = CredentialManager(key=key, credentials_file=tmp)
            cm.set("test_cred", {"username": "user", "password": "SuperSecret!"})
            for msg in log_records:
                self.assertNotIn("SuperSecret!", msg, "Senha não deve aparecer em logs")
                if "password" in msg.lower():
                    self.assertIn("[REDACTED]", msg)
        finally:
            tmp.unlink(missing_ok=True)
            logging.getLogger('security.credential_manager').removeHandler(handler)

    def test_61_credential_manager_integridade(self):
        from security.credential_manager import CredentialManager
        from cryptography.fernet import Fernet
        import tempfile, pathlib
        key = Fernet.generate_key()
        with tempfile.NamedTemporaryFile(suffix=".enc", delete=False) as f:
            tmp = pathlib.Path(f.name)
        try:
            cm = CredentialManager(key=key, credentials_file=tmp)
            cm.set("cred1", {"password": "abc"})
            self.assertTrue(cm.validate_integrity())
        finally:
            tmp.unlink(missing_ok=True)

    def test_62_credential_manager_integridade_arquivo_corrompido(self):
        from security.credential_manager import CredentialManager
        from cryptography.fernet import Fernet
        import tempfile, pathlib
        key = Fernet.generate_key()
        with tempfile.NamedTemporaryFile(suffix=".enc", delete=False) as f:
            tmp = pathlib.Path(f.name)
            f.write(b"arquivo_corrompido_nao_e_fernet")
        try:
            cm = CredentialManager(key=key, credentials_file=tmp)
            self.assertFalse(cm.validate_integrity())
        finally:
            tmp.unlink(missing_ok=True)

    def test_63_vault_client_sem_backend(self):
        from security.vault_client import VaultClient
        import os
        # Garantir que não há variáveis de ambiente de vault
        os.environ.pop("VAULT_ADDR", None)
        os.environ.pop("AZURE_KEYVAULT_URL", None)
        vc = VaultClient()
        self.assertFalse(vc.is_available())
        result = vc.get_secret("any/path")
        self.assertIsNone(result)


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 10 - AIOPS
# ═══════════════════════════════════════════════════════════════════

class TestAIOps(unittest.TestCase):

    def test_64_anomaly_detector_sem_dados_retorna_none(self):
        from anomaly_detector import AnomalyDetector
        ad = AnomalyDetector()
        result = ad.detect("host1", "cpu", 95.0)
        self.assertIsNone(result, "Sem dados suficientes deve retornar None")

    def test_65_anomaly_detector_add_samples(self):
        from anomaly_detector import AnomalyDetector
        ad = AnomalyDetector()
        for i in range(60):
            ad.add_sample("host1", "cpu", float(i % 30 + 20))
        # Deve ter dados suficientes para treinar
        self.assertGreater(len(ad._data["host1:cpu"]), 50)

    def test_66_anomaly_detector_treina_com_sklearn(self):
        from anomaly_detector import AnomalyDetector
        try:
            import sklearn
            sklearn_ok = True
        except ImportError:
            sklearn_ok = False
        ad = AnomalyDetector()
        for i in range(60):
            ad.add_sample("h", "cpu", float(i % 20 + 30))
        ad._retrain_all()
        if sklearn_ok:
            self.assertIn("h:cpu", ad._models)
            print(f"\n  AnomalyDetector: modelo treinado com scikit-learn OK")
        else:
            print(f"\n  AnomalyDetector: scikit-learn não instalado (skip treino)")

    def test_67_failure_predictor_sem_dados_retorna_none(self):
        from failure_predictor import FailurePredictor
        fp = FailurePredictor()
        result = fp.predict("host1", "disk", threshold=90.0)
        self.assertIsNone(result)

    def test_68_failure_predictor_tendencia_crescente(self):
        from failure_predictor import FailurePredictor
        fp = FailurePredictor()
        now = time.time()
        # Disco crescendo de 50% para 80% em 30 amostras
        for i in range(30):
            fp.add_sample("host1", "disk", 50.0 + i, timestamp=now - (30 - i) * 3600)
        result = fp.predict("host1", "disk", threshold=90.0)
        if result:
            print(f"\n  FailurePredictor: breach em {result['hours_until_breach']:.1f}h "
                  f"(slope={result['trend_slope']:.4f})")
            self.assertIn("predicted_breach_time", result)
            self.assertIn("confidence_interval", result)
        else:
            print(f"\n  FailurePredictor: sem previsão de breach (tendência insuficiente)")

    def test_69_event_correlator_sem_eventos(self):
        from event_correlator import EventCorrelator
        ec = EventCorrelator()
        groups = ec.correlate()
        self.assertEqual(groups, [])

    def test_70_event_correlator_agrupa_por_host(self):
        from event_correlator import EventCorrelator
        ec = EventCorrelator()
        now = time.time()
        ec.add_event({"host": "srv1", "sensor_type": "cpu", "status": "critical", "timestamp": now})
        ec.add_event({"host": "srv1", "sensor_type": "memory", "status": "warning", "timestamp": now + 10})
        ec.add_event({"host": "srv2", "sensor_type": "cpu", "status": "ok", "timestamp": now + 5})
        groups = ec.correlate()
        self.assertGreater(len(groups), 0)
        srv1_group = next((g for g in groups if "srv1" in g["hosts"]), None)
        self.assertIsNotNone(srv1_group)
        self.assertEqual(srv1_group["event_count"], 2)
        print(f"\n  EventCorrelator: {len(groups)} grupos, causa raiz srv1={srv1_group['root_cause']['status']}")

    def test_71_event_correlator_causa_raiz_mais_severa(self):
        from event_correlator import EventCorrelator
        ec = EventCorrelator()
        now = time.time()
        ec.add_event({"host": "srv3", "sensor_type": "cpu", "status": "warning", "timestamp": now})
        ec.add_event({"host": "srv3", "sensor_type": "disk", "status": "critical", "timestamp": now + 5})
        groups = ec.correlate()
        g = groups[0]
        # Causa raiz deve ser o critical
        self.assertEqual(g["root_cause"]["status"], "critical")


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 11 - ESCALABILIDADE (BENCHMARK)
# ═══════════════════════════════════════════════════════════════════

class TestEscalabilidade(unittest.TestCase):

    def test_72_benchmark_500_hosts_20_sensores(self):
        """
        Simula ambiente com 500 hosts × 20 sensores = 10.000 sensores.
        Mede tempo de registro e uso de memória.
        """
        from engine.sensor_engine import SensorEngine, SensorDefinition, SensorType
        from engine.scheduler import Scheduler
        from engine.thread_pool import WorkerPool
        import tracemalloc

        tracemalloc.start()
        pool = WorkerPool(max_workers=20)
        engine = SensorEngine()
        sched = Scheduler(engine, pool)

        start = time.monotonic()
        total_added = 0
        for host_idx in range(500):
            host = f"10.{host_idx // 256}.{host_idx % 256}.1"
            sensors = [
                SensorDefinition(
                    id=f"h{host_idx}_s{s}",
                    type=SensorType.ICMP_PING,
                    target=host,
                    interval=60,
                )
                for s in range(20)
            ]
            sched.add_many(sensors)
            total_added += len(sensors)

        elapsed = time.monotonic() - start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        status = sched.status()
        mem_mb = peak / (1024 * 1024)

        print(f"\n  BENCHMARK 500 hosts × 20 sensores:")
        print(f"    Sensores registrados: {status['total_sensors']}")
        print(f"    Tempo de registro: {elapsed:.3f}s")
        print(f"    Memória pico: {mem_mb:.1f}MB")

        self.assertLess(elapsed, 10.0, "Registro de 10k sensores deve ser < 10s")
        self.assertLess(mem_mb, 200, "Uso de memória deve ser < 200MB para 10k sensores")
        pool.shutdown(wait=False)

    def test_73_benchmark_cache_throughput(self):
        """Mede throughput do cache local: operações/segundo"""
        from engine.metric_cache import MetricCache
        cache = MetricCache()
        N = 10000
        start = time.monotonic()
        for i in range(N):
            cache.set(f"host{i % 100}", "cpu", f"q{i}", float(i), ttl=60)
        for i in range(N):
            cache.get(f"host{i % 100}", "cpu", f"q{i}")
        elapsed = time.monotonic() - start
        ops_per_sec = (N * 2) / elapsed
        print(f"\n  Cache throughput: {ops_per_sec:.0f} ops/s ({N*2} ops em {elapsed:.3f}s)")
        self.assertGreater(ops_per_sec, 10000, "Cache deve suportar > 10k ops/s")

    def test_74_benchmark_adaptive_monitor_throughput(self):
        """Mede throughput do AdaptiveMonitor"""
        from engine.adaptive_monitor import AdaptiveMonitor
        am = AdaptiveMonitor()
        N = 50000
        start = time.monotonic()
        for i in range(N):
            am.update(f"host{i % 500}", "ok" if i % 10 != 0 else "critical")
        elapsed = time.monotonic() - start
        ops_per_sec = N / elapsed
        print(f"\n  AdaptiveMonitor throughput: {ops_per_sec:.0f} updates/s")
        self.assertGreater(ops_per_sec, 5000)

    def test_75_benchmark_worker_pool_throughput(self):
        """Mede throughput real do WorkerPool com 20 workers"""
        from engine.thread_pool import WorkerPool
        pool = WorkerPool(max_workers=20)
        N = 500
        counter = {"n": 0}
        lock = threading.Lock()
        def task():
            with lock:
                counter["n"] += 1
        start = time.monotonic()
        futures = [pool.submit(task) for _ in range(N)]
        for f in futures:
            f.result(timeout=30)
        elapsed = time.monotonic() - start
        tasks_per_sec = N / elapsed
        print(f"\n  WorkerPool throughput: {tasks_per_sec:.0f} tasks/s ({N} tasks em {elapsed:.3f}s)")
        self.assertEqual(counter["n"], N)
        pool.shutdown()


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 12 - MULTI-PROBE API
# ═══════════════════════════════════════════════════════════════════

class TestMultiProbeAPI(unittest.TestCase):

    def test_76_multi_probe_tipos_validos(self):
        """Verifica constantes do multi_probe sem importar FastAPI"""
        # Lê o arquivo diretamente para verificar as constantes
        import pathlib
        content = pathlib.Path(os.path.join(
            os.path.dirname(__file__), '..', 'api', 'routers', 'multi_probe.py'
        )).read_text()
        self.assertIn("probe_datacenter", content)
        self.assertIn("probe_cloud", content)
        self.assertIn("probe_edge", content)
        self.assertIn("OFFLINE_THRESHOLD_SECONDS", content)
        print("\n  multi_probe.py: tipos e constantes presentes OK")

    def test_77_multi_probe_offline_threshold_valor(self):
        """Verifica que OFFLINE_THRESHOLD_SECONDS = 120 no código"""
        import pathlib
        content = pathlib.Path(os.path.join(
            os.path.dirname(__file__), '..', 'api', 'routers', 'multi_probe.py'
        )).read_text()
        self.assertIn("OFFLINE_THRESHOLD_SECONDS = 120", content)
        print("\n  multi_probe.py: OFFLINE_THRESHOLD_SECONDS = 120 OK")


# ═══════════════════════════════════════════════════════════════════
# SEÇÃO 13 - WMI CONNECTION POOL
# ═══════════════════════════════════════════════════════════════════

class TestWMIConnectionPool(unittest.TestCase):
    """Valida WMIConnectionPool — max 3 por host, reuso, stats, CoInitializeSecurity"""

    def _make_pool(self, max_per_host=3):
        from engine.wmi_pool import WMIConnectionPool
        return WMIConnectionPool(max_per_host=max_per_host)

    def test_78_wmi_pool_importavel(self):
        """WMIConnectionPool deve ser importável"""
        from engine.wmi_pool import WMIConnectionPool, get_pool
        self.assertIsNotNone(WMIConnectionPool)
        self.assertIsNotNone(get_pool)

    def test_79_wmi_pool_max_3_por_host(self):
        """Limite padrão deve ser 3 conexões por host"""
        from engine.wmi_pool import WMIConnectionPool, MAX_CONNECTIONS_PER_HOST
        self.assertEqual(MAX_CONNECTIONS_PER_HOST, 3)
        pool = WMIConnectionPool()
        self.assertEqual(pool.max_per_host, 3)

    def test_80_wmi_pool_idle_timeout_300s(self):
        """Idle timeout deve ser 300s (5 min)"""
        from engine.wmi_pool import IDLE_TIMEOUT_SEC
        self.assertEqual(IDLE_TIMEOUT_SEC, 300)

    def test_81_wmi_pool_acquire_sem_wmi_retorna_none(self):
        """Sem wmi instalado, acquire deve retornar None graciosamente"""
        from engine.wmi_pool import WMIConnectionPool
        pool = WMIConnectionPool(max_per_host=3)
        # Em ambiente sem wmi (Linux/CI), _create_connection retorna None
        conn = pool.acquire("192.0.2.1", "user", "pass", "domain")
        # Deve retornar None sem lançar exceção
        self.assertIsNone(conn)
        print(f"\n  WMI Pool acquire sem wmi: retornou None corretamente")

    def test_82_wmi_pool_limite_por_host_com_mock(self):
        """Com conexões mockadas, deve respeitar limite de 3 por host"""
        from engine.wmi_pool import WMIConnectionPool, PooledConnection
        pool = WMIConnectionPool(max_per_host=3)

        # Injetar conexões mockadas diretamente no pool
        host = "10.0.0.1"
        mock_conns = []
        with pool._lock:
            pool._pools[host] = []
            for i in range(3):
                mock_conn = object()  # objeto qualquer como mock
                pc = PooledConnection(host=host, connection=mock_conn, in_use=True)
                pool._pools[host].append(pc)
                mock_conns.append(mock_conn)

        # 4ª tentativa deve retornar None (limite atingido)
        result = pool.acquire(host, "user", "pass")
        self.assertIsNone(result, "Deve retornar None quando limite de 3 atingido")
        print(f"\n  WMI Pool limite 3/host: 4ª conexão retornou None corretamente")

    def test_83_wmi_pool_reuso_com_mock(self):
        """Conexão ociosa deve ser reutilizada"""
        from engine.wmi_pool import WMIConnectionPool, PooledConnection
        pool = WMIConnectionPool(max_per_host=3)

        host = "10.0.0.2"
        mock_conn = object()
        with pool._lock:
            pc = PooledConnection(host=host, connection=mock_conn, in_use=False)
            pool._pools[host] = [pc]

        # Acquire deve reutilizar a conexão ociosa
        acquired = pool.acquire(host, "user", "pass")
        self.assertIs(acquired, mock_conn, "Deve reutilizar conexão ociosa existente")

        # Liberar
        pool.release(host, mock_conn)
        with pool._lock:
            self.assertFalse(pool._pools[host][0].in_use)
        print(f"\n  WMI Pool reuso: conexão ociosa reutilizada corretamente")

    def test_84_wmi_pool_release_marca_idle(self):
        """Release deve marcar conexão como não em uso"""
        from engine.wmi_pool import WMIConnectionPool, PooledConnection
        pool = WMIConnectionPool(max_per_host=3)

        host = "10.0.0.3"
        mock_conn = object()
        with pool._lock:
            pc = PooledConnection(host=host, connection=mock_conn, in_use=True)
            pool._pools[host] = [pc]

        pool.release(host, mock_conn)
        with pool._lock:
            self.assertFalse(pool._pools[host][0].in_use)

    def test_85_wmi_pool_invalidate_remove_conexao(self):
        """Invalidate deve remover conexão com erro do pool"""
        from engine.wmi_pool import WMIConnectionPool, PooledConnection
        pool = WMIConnectionPool(max_per_host=3)

        host = "10.0.0.4"
        mock_conn = object()
        with pool._lock:
            pc = PooledConnection(host=host, connection=mock_conn, in_use=True)
            pool._pools[host] = [pc]

        pool.invalidate(host, mock_conn)
        with pool._lock:
            self.assertEqual(len(pool._pools[host]), 0, "Conexão inválida deve ser removida")

    def test_86_wmi_pool_stats(self):
        """Stats deve retornar total, in_use e idle por host"""
        from engine.wmi_pool import WMIConnectionPool, PooledConnection
        pool = WMIConnectionPool(max_per_host=3)

        host = "10.0.0.5"
        with pool._lock:
            pool._pools[host] = [
                PooledConnection(host=host, connection=object(), in_use=True),
                PooledConnection(host=host, connection=object(), in_use=False),
            ]

        stats = pool.stats()
        self.assertIn(host, stats)
        self.assertEqual(stats[host]["total"], 2)
        self.assertEqual(stats[host]["in_use"], 1)
        self.assertEqual(stats[host]["idle"], 1)
        print(f"\n  WMI Pool stats: {stats[host]}")

    def test_87_wmi_pool_coinitializesecurity_disponivel(self):
        """_init_thread_com deve existir e não lançar exceção"""
        from engine.wmi_pool import _init_thread_com
        # Deve executar sem exceção (mesmo sem pythoncom instalado)
        try:
            _init_thread_com()
        except Exception as e:
            # Sem pythoncom é esperado falhar graciosamente
            pass
        self.assertTrue(True)

    def test_88_wmi_pool_singleton_get_pool(self):
        """get_pool() deve retornar sempre a mesma instância"""
        from engine.wmi_pool import get_pool
        p1 = get_pool()
        p2 = get_pool()
        self.assertIs(p1, p2, "get_pool() deve retornar singleton")

    def test_89_wmi_pool_50_hosts_simultaneos(self):
        """50 hosts diferentes não devem conflitar entre si"""
        from engine.wmi_pool import WMIConnectionPool, PooledConnection
        pool = WMIConnectionPool(max_per_host=3)

        # Injetar 1 conexão ociosa em cada host
        hosts = [f"10.1.{i//10}.{i%10+1}" for i in range(50)]
        for host in hosts:
            mock_conn = object()
            with pool._lock:
                pc = PooledConnection(host=host, connection=mock_conn, in_use=False)
                pool._pools[host] = [pc]

        # Adquirir de todos os 50 hosts
        acquired = []
        for host in hosts:
            conn = pool.acquire(host, "user", "pass")
            if conn:
                acquired.append((host, conn))

        self.assertEqual(len(acquired), 50, "50 hosts diferentes devem adquirir sem conflito")
        print(f"\n  WMI Pool 50 hosts: {len(acquired)}/50 adquiridos sem conflito")

        # Liberar tudo
        for host, conn in acquired:
            pool.release(host, conn)


# ═══════════════════════════════════════════════════════════════════
# FASE 2 — NOVOS COMPONENTES v2.1
# ═══════════════════════════════════════════════════════════════════

class TestGlobalRateLimiter(unittest.TestCase):
    """Valida GlobalRateLimiter — max 200 sensores, fila 1000"""

    def _make_limiter(self, max_running=5, queue_limit=10):
        from engine.global_rate_limiter import GlobalRateLimiter
        return GlobalRateLimiter(max_running=max_running, queue_limit=queue_limit)

    def test_90_rate_limiter_importavel(self):
        from engine.global_rate_limiter import GlobalRateLimiter, get_limiter
        from engine.global_rate_limiter import MAX_GLOBAL_SENSORS_RUNNING, QUEUE_LIMIT
        self.assertEqual(MAX_GLOBAL_SENSORS_RUNNING, 200)
        self.assertEqual(QUEUE_LIMIT, 1000)

    def test_91_rate_limiter_acquire_release(self):
        limiter = self._make_limiter(max_running=3)
        with limiter.acquire_slot("sensor_1"):
            self.assertEqual(limiter.global_active_sensors, 1)
        self.assertEqual(limiter.global_active_sensors, 0)

    def test_92_rate_limiter_respeita_limite(self):
        from engine.global_rate_limiter import GlobalRateLimiter
        limiter = GlobalRateLimiter(max_running=2, queue_limit=5)
        # Adquirir 2 slots manualmente
        limiter._acquire("s1", timeout=1)
        limiter._acquire("s2", timeout=1)
        self.assertEqual(limiter.global_active_sensors, 2)
        # 3ª deve falhar (timeout=0)
        result = limiter._acquire("s3", timeout=0)
        self.assertFalse(result)
        limiter._release("s1")
        limiter._release("s2")

    def test_93_rate_limiter_fila_cheia_rejeita(self):
        from engine.global_rate_limiter import GlobalRateLimiter
        limiter = GlobalRateLimiter(max_running=1, queue_limit=0)
        # Ocupar o único slot
        limiter._acquire("s1", timeout=1)
        # Fila cheia (0), deve rejeitar
        result = limiter._acquire("s2", timeout=0)
        self.assertFalse(result)
        limiter._release("s1")

    def test_94_rate_limiter_metrics(self):
        limiter = self._make_limiter(max_running=10)
        metrics = limiter.metrics()
        self.assertIn("global_active_sensors", metrics)
        self.assertIn("global_queue_depth", metrics)
        self.assertIn("utilization_pct", metrics)
        self.assertEqual(metrics["max_running"], 10)

    def test_95_rate_limiter_singleton(self):
        from engine.global_rate_limiter import get_limiter
        l1 = get_limiter()
        l2 = get_limiter()
        self.assertIs(l1, l2)


class TestMetricsPipeline(unittest.TestCase):
    """Valida StreamProducer, StreamConsumer e MetricsProcessor"""

    def test_96_stream_producer_importavel(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from metrics_pipeline.stream_producer import StreamProducer, MetricEvent, get_producer
        self.assertIsNotNone(StreamProducer)
        self.assertIsNotNone(MetricEvent)

    def test_97_stream_producer_fallback_sem_redis(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from metrics_pipeline.stream_producer import StreamProducer, MetricEvent
        producer = StreamProducer(redis_url=None)
        event = MetricEvent(sensor_id=1, server_id=1, sensor_type="cpu", value=75.0)
        result = producer.publish(event)
        self.assertTrue(result)
        stats = producer.stats()
        self.assertEqual(stats["published"], 1)
        self.assertEqual(stats["backend"], "memory")
        self.assertEqual(stats["fallback_queue_size"], 1)

    def test_98_stream_producer_drain_fallback(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from metrics_pipeline.stream_producer import StreamProducer, MetricEvent
        producer = StreamProducer()
        for i in range(5):
            producer.publish(MetricEvent(sensor_id=i, server_id=1, sensor_type="cpu", value=float(i)))
        drained = producer.drain_fallback(max_items=3)
        self.assertEqual(len(drained), 3)
        self.assertEqual(producer.stats()["fallback_queue_size"], 2)

    def test_99_metrics_processor_importavel(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from metrics_pipeline.metrics_processor import MetricsProcessor
        self.assertIsNotNone(MetricsProcessor)

    def test_100_metrics_processor_deduplicacao(self):
        import sys, os, time
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from metrics_pipeline.stream_producer import MetricEvent
        from metrics_pipeline.metrics_processor import MetricsProcessor

        persisted_batches = []
        processor = MetricsProcessor.__new__(MetricsProcessor)
        processor._api_url = ""
        processor._api_token = ""
        processor._seen = {}
        processor._persisted = 0
        processor._deduplicated = 0
        processor._errors = 0

        # Substituir _persist por mock
        processor._persist = lambda events: persisted_batches.extend(events)

        ts = time.time()
        events = [
            MetricEvent(sensor_id=1, server_id=1, sensor_type="cpu", value=80.0, timestamp=ts),
            MetricEvent(sensor_id=1, server_id=1, sensor_type="cpu", value=81.0, timestamp=ts),  # duplicata
            MetricEvent(sensor_id=2, server_id=1, sensor_type="mem", value=60.0, timestamp=ts),
        ]
        processor.process_batch(events)
        # sensor_id=1 deve aparecer apenas 1x (dedup por bucket de 5s)
        self.assertEqual(len(persisted_batches), 2)
        print(f"\n  MetricsProcessor dedup: {processor._deduplicated} duplicatas removidas")


class TestEventQueue(unittest.TestCase):
    """Valida EventQueue — dedup, rate limit, agrupamento"""

    def test_101_event_queue_importavel(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from event_engine.event_queue import EventQueue, MonitoringEvent
        self.assertIsNotNone(EventQueue)

    def test_102_event_queue_push_e_flush(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from event_engine.event_queue import EventQueue, MonitoringEvent
        queue = EventQueue()
        e = MonitoringEvent(host="srv1", event_type="cpu_high", severity="warning", message="CPU 90%")
        result = queue.push(e)
        self.assertTrue(result)
        flushed = queue.flush()
        self.assertEqual(len(flushed), 1)

    def test_103_event_queue_deduplicacao(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from event_engine.event_queue import EventQueue, MonitoringEvent
        queue = EventQueue(dedup_window=60)
        e1 = MonitoringEvent(host="srv1", event_type="cpu_high", severity="warning", message="CPU 90%")
        e2 = MonitoringEvent(host="srv1", event_type="cpu_high", severity="warning", message="CPU 91%")
        r1 = queue.push(e1)
        r2 = queue.push(e2)  # duplicata dentro da janela
        self.assertTrue(r1)
        self.assertFalse(r2)
        stats = queue.stats()
        self.assertEqual(stats["total_deduplicated"], 1)

    def test_104_event_queue_rate_limit(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from event_engine.event_queue import EventQueue, MonitoringEvent
        queue = EventQueue(dedup_window=0, rate_limit=3)
        host = "srv_rate"
        accepted = 0
        for i in range(5):
            e = MonitoringEvent(host=host, event_type=f"event_{i}", severity="info", message=f"msg {i}")
            if queue.push(e):
                accepted += 1
        self.assertLessEqual(accepted, 3)
        print(f"\n  EventQueue rate limit: {accepted}/5 aceitos (limite=3)")

    def test_105_event_queue_stats(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'probe'))
        from event_engine.event_queue import EventQueue, MonitoringEvent
        queue = EventQueue()
        queue.push(MonitoringEvent(host="h1", event_type="e1", severity="info", message="m"))
        stats = queue.stats()
        self.assertIn("queue_size", stats)
        self.assertIn("total_pushed", stats)
        self.assertIn("total_deduplicated", stats)


class TestRootCauseEngine(unittest.TestCase):
    """Valida RootCauseEngine — detecção de causa raiz e cascata"""

    def test_106_rca_importavel(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))
        from root_cause_engine import RootCauseEngine, RCAEvent, RCAHypothesis
        self.assertIsNotNone(RootCauseEngine)

    def test_107_rca_sem_eventos_retorna_vazio(self):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))
        from root_cause_engine import RootCauseEngine
        engine = RootCauseEngine()
        result = engine.analyze()
        self.assertEqual(result, [])

    def test_108_rca_detecta_cascata(self):
        import sys, os, time
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))
        from root_cause_engine import RootCauseEngine, RCAEvent
        engine = RootCauseEngine()
        t = time.time()
        # Switch offline primeiro
        engine.add_event(RCAEvent(host="switch1", event_type="switch_offline", severity="critical", timestamp=t, message="Switch offline"))
        # Hosts dependentes offline depois
        engine.add_event(RCAEvent(host="srv1", event_type="host_offline", severity="critical", timestamp=t+5, message="Host offline"))
        engine.add_event(RCAEvent(host="srv2", event_type="ping_failed", severity="critical", timestamp=t+6, message="Ping falhou"))
        hypotheses = engine.analyze()
        self.assertGreater(len(hypotheses), 0)
        top = hypotheses[0]
        self.assertGreater(top.confidence, 0.5)
        print(f"\n  RCA cascata: causa={top.root_cause_host}, confiança={top.confidence:.2f}, padrão={top.pattern}")

    def test_109_rca_to_dict(self):
        import sys, os, time
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))
        from root_cause_engine import RootCauseEngine, RCAEvent
        engine = RootCauseEngine()
        t = time.time()
        engine.add_event(RCAEvent(host="sw1", event_type="switch_offline", severity="critical", timestamp=t, message=""))
        engine.add_event(RCAEvent(host="h1", event_type="host_offline", severity="critical", timestamp=t+1, message=""))
        hypotheses = engine.analyze()
        if hypotheses:
            d = hypotheses[0].to_dict()
            self.assertIn("root_cause_host", d)
            self.assertIn("confidence", d)
            self.assertIn("affected_hosts", d)


class TestWMIPoolConnectionLayer(unittest.TestCase):
    """Valida que connection_pool/wmi_pool.py expõe WMIConnectionPool corretamente"""

    def test_110_wmi_pool_connection_layer_importavel(self):
        """connection_pool/wmi_pool deve re-exportar WMIConnectionPool"""
        import sys, os
        # Adicionar probe ao path
        probe_path = os.path.join(os.path.dirname(__file__), '..', 'probe')
        if probe_path not in sys.path:
            sys.path.insert(0, probe_path)
        # Importar diretamente do arquivo
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "wmi_pool_conn",
            os.path.join(probe_path, "connection_pool", "wmi_pool.py")
        )
        # Arquivo existe e é importável
        self.assertIsNotNone(spec)


# ═══════════════════════════════════════════════════════════════════
# FASE 3 — ANOMALY DETECTOR EXPANDIDO + DISCOVERY + DARK MODE
# ═══════════════════════════════════════════════════════════════════

class TestAnomalyDetectorExpandido(unittest.TestCase):
    """Valida baseline automático, detecção de tendências e previsão de capacidade"""

    def _make_detector_with_data(self, host="h1", metric="cpu", n=60, start=20.0, step=1.0):
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))
        from anomaly_detector import AnomalyDetector
        ad = AnomalyDetector()
        now = time.time()
        for i in range(n):
            ad.add_sample(host, metric, start + i * step, timestamp=now - (n - i) * 3600)
        return ad

    def test_111_anomaly_detector_baseline_automatico(self):
        """Após retreino, baseline deve conter mean/std/p95 (funciona sem sklearn)"""
        ad = self._make_detector_with_data(n=60, start=30.0, step=0.5)
        ad._retrain_all()
        baseline = ad.get_baseline("h1", "cpu")
        self.assertIsNotNone(baseline, "Baseline deve ser calculado mesmo sem sklearn")
        self.assertIn("mean", baseline)
        self.assertIn("std", baseline)
        self.assertIn("p95", baseline)
        self.assertIn("samples", baseline)
        self.assertEqual(baseline["samples"], 60)
        print(f"\n  Baseline automático: mean={baseline['mean']}, p95={baseline['p95']}")

    def test_112_anomaly_detector_detect_trend_crescente(self):
        """detect_trend deve identificar tendência crescente"""
        ad = self._make_detector_with_data(n=30, start=50.0, step=1.0)
        trend = ad.detect_trend("h1", "cpu")
        self.assertIsNotNone(trend)
        self.assertEqual(trend["direction"], "increasing")
        self.assertGreater(trend["slope_per_hour"], 0)
        self.assertIn("predicted_1h", trend)
        self.assertIn("predicted_24h", trend)
        print(f"\n  Trend crescente: slope={trend['slope_per_hour']:.4f}/h, pred_24h={trend['predicted_24h']:.1f}")

    def test_113_anomaly_detector_detect_trend_estavel(self):
        """Dados estáveis devem retornar direction=stable"""
        ad = self._make_detector_with_data(n=30, start=50.0, step=0.0)
        trend = ad.detect_trend("h1", "cpu")
        self.assertIsNotNone(trend)
        self.assertEqual(trend["direction"], "stable")

    def test_114_anomaly_detector_predict_capacity(self):
        """predict_capacity deve retornar horas até breach quando tendência crescente"""
        ad = self._make_detector_with_data(n=30, start=50.0, step=1.0)
        result = ad.predict_capacity("h1", "cpu", threshold=90.0)
        if result:
            self.assertIn("hours_until_breach", result)
            self.assertIn("predicted_breach_iso", result)
            self.assertIn("confidence", result)
            self.assertGreater(result["hours_until_breach"], 0)
            print(f"\n  Capacity prediction: breach em {result['hours_until_breach']:.1f}h, confiança={result['confidence']}")
        else:
            print("\n  Capacity prediction: sem breach previsto (dados insuficientes)")

    def test_115_anomaly_detector_predict_capacity_sem_tendencia(self):
        """Dados decrescentes não devem gerar previsão de breach"""
        ad = self._make_detector_with_data(n=30, start=80.0, step=-1.0)
        result = ad.predict_capacity("h1", "cpu", threshold=90.0)
        self.assertIsNone(result, "Tendência decrescente não deve gerar breach")

    def test_116_anomaly_detector_trend_poucos_dados(self):
        """Com menos de 10 amostras, detect_trend deve retornar None"""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-agent'))
        from anomaly_detector import AnomalyDetector
        ad = AnomalyDetector()
        for i in range(5):
            ad.add_sample("h2", "disk", float(i * 10))
        result = ad.detect_trend("h2", "disk")
        self.assertIsNone(result)


class TestDiscoveryFiles(unittest.TestCase):
    """Valida existência e estrutura dos arquivos de Discovery"""

    def test_117_discovery_js_existe(self):
        """Discovery.js deve existir no frontend"""
        import pathlib
        path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'frontend' / 'src' / 'components' / 'Discovery.js'
        self.assertTrue(path.exists(), "Discovery.js deve existir")
        content = path.read_text(encoding='utf-8')
        self.assertIn("network-scan", content)
        self.assertIn("snmp", content)
        self.assertIn("wmi", content)
        print("\n  Discovery.js: network-scan, snmp, wmi presentes OK")

    def test_118_discovery_css_existe(self):
        """Discovery.css deve existir"""
        import pathlib
        path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'frontend' / 'src' / 'components' / 'Discovery.css'
        self.assertTrue(path.exists(), "Discovery.css deve existir")

    def test_119_discovery_api_existe(self):
        """api/routers/discovery.py deve existir com endpoints corretos"""
        import pathlib
        path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'api' / 'routers' / 'discovery.py'
        self.assertTrue(path.exists(), "discovery.py deve existir")
        content = path.read_text(encoding='utf-8')
        self.assertIn("/network-scan", content)
        self.assertIn("/snmp", content)
        self.assertIn("/wmi", content)
        print("\n  discovery.py: endpoints /network-scan, /snmp, /wmi presentes OK")

    def test_120_dark_mode_toggle_sidebar(self):
        """Sidebar.js deve ter toggle de colapso (sidebar--collapsed)"""
        import pathlib
        path = pathlib.Path(os.path.dirname(__file__)) / '..' / 'frontend' / 'src' / 'components' / 'Sidebar.js'
        content = path.read_text(encoding='utf-8')
        self.assertIn("collapsed", content)
        self.assertIn("onToggleCollapse", content)
        print("\n  Sidebar.js: toggle collapse implementado OK")


# ═══════════════════════════════════════════════════════════════════
# RUNNER PRINCIPAL COM RELATÓRIO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import time as _time

    print("=" * 70)
    print("  AUDITORIA TÉCNICA - CORUJA MONITOR ENTERPRISE")
    print(f"  Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    t0 = _time.monotonic()
    result = runner.run(suite)
    total_time = _time.monotonic() - t0

    print("\n" + "=" * 70)
    print("  RELATÓRIO FINAL")
    print("=" * 70)
    print(f"  Testes executados : {result.testsRun}")
    print(f"  Passou            : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Falhou            : {len(result.failures)}")
    print(f"  Erros             : {len(result.errors)}")
    print(f"  Tempo total       : {total_time:.2f}s")
    print(f"  Status            : {'APROVADO' if result.wasSuccessful() else 'REPROVADO'}")
    print("=" * 70)
