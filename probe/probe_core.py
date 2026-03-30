import time
import json
import logging
from datetime import datetime
from pathlib import Path
import httpx
from typing import List, Dict, Any

# Componentes enterprise
try:
    from engine.global_rate_limiter import get_limiter as get_rate_limiter
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    RATE_LIMITER_AVAILABLE = False

try:
    from engine.wmi_batch_collector import get_batch_collector
    WMI_BATCH_AVAILABLE = True
except ImportError:
    WMI_BATCH_AVAILABLE = False

from collectors.cpu_collector import CPUCollector
from collectors.memory_collector import MemoryCollector
from collectors.disk_collector import DiskCollector
from collectors.network_collector import NetworkCollector
from collectors.service_collector import ServiceCollector
from collectors.wmi_service_collector import WMIServiceCollector
from collectors.hyperv_collector import HyperVCollector
from collectors.hyperv_wmi_collector import HyperVWMICollector
from collectors.udm_collector import UDMCollector
from collectors.system_collector import SystemCollector
from collectors.ping_collector import PingCollector
from collectors.docker_collector import DockerCollector
from collectors.kubernetes_collector import KubernetesCollector
from config import ProbeConfig

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('probe.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProbeCore:
    def __init__(self):
        self.config = ProbeConfig()
        self.running = False
        self.collectors = []
        self.buffer = []
        self.max_buffer_size = 1000
        
        # Initialize Kubernetes collector
        self.kubernetes_collector = None
        
        # Initialize collectors
        self._init_collectors()
    
    def _init_collectors(self):
        """Initialize all metric collectors"""
        # Standard sensors in specific order: Ping, CPU, Memory, Disk, Uptime, Network IN, Network OUT
        self.collectors = [
            PingCollector(target="8.8.8.8"),  # 1. Ping
            CPUCollector(),                    # 2. CPU
            MemoryCollector(),                 # 3. Memory
            DiskCollector(),                   # 4. Disk
            SystemCollector(),                 # 5. Uptime
            NetworkCollector(),                # 6. Network IN/OUT
            WMIServiceCollector(),             # 7. Serviços Windows (StartMode=Auto)
            HyperVCollector(),
            UDMCollector(self.config.udm_targets),
            DockerCollector()                  # Docker monitoring
        ]
        
        # Initialize Kubernetes collector (separate from standard collectors)
        try:
            self.kubernetes_collector = KubernetesCollector(
                api_url=self.config.api_url,
                probe_token=self.config.probe_token
            )
            logger.info("Kubernetes collector initialized")
        except Exception as e:
            logger.warning(f"Kubernetes collector not available: {e}")
            self.kubernetes_collector = None
        
        logger.info(f"Initialized {len(self.collectors)} collectors")
    
    def start(self):
        """Start the probe"""
        self.running = True
        logger.info("Coruja Probe started")
        
        # Send initial heartbeat
        self._send_heartbeat()
        
        # Auto-register this server
        self._auto_register_server()
        
        # Main collection loop
        last_heartbeat = time.time()
        last_collection = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Send heartbeat every 60 seconds
                if current_time - last_heartbeat >= 60:
                    self._send_heartbeat()
                    last_heartbeat = current_time
                
                # Collect metrics based on interval
                if current_time - last_collection >= self.config.collection_interval:
                    self._collect_metrics()
                    last_collection = current_time
                    
                    # Send metrics immediately after collection
                    if len(self.buffer) > 0:
                        self._send_metrics()
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the probe"""
        self.running = False
        # Send any buffered metrics
        if self.buffer:
            self._send_metrics()
        logger.info("Coruja Probe stopped")
    
    def _get_server_credential(self, server_id):
        """
        Busca credencial do servidor via API (sistema moderno como PRTG)
        Usa herança: Servidor → Grupo → Empresa
        """
        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                response = client.get(
                    f"{self.config.api_url}/api/v1/credentials/resolve/{server_id}",
                    params={"probe_token": self.config.probe_token}
                )
                
                if response.status_code == 404:
                    logger.debug(f"Nenhuma credencial configurada para servidor ID {server_id}")
                    return None
                
                if response.status_code != 200:
                    logger.warning(f"Erro ao buscar credencial: HTTP {response.status_code}")
                    return None
                
                credential = response.json()
                
                # Verificar se realmente encontrou uma credencial
                if credential.get('source') == 'none' or not credential.get('credential_type'):
                    logger.debug(f"Nenhuma credencial configurada para servidor ID {server_id}")
                    return None
                
                logger.info(f"🔑 Credencial: {credential.get('name')} | Nível: {credential.get('inheritance_level')}")
                return credential
                
        except Exception as e:
            logger.error(f"Erro ao buscar credencial do servidor {server_id}: {e}")
            return None
    
    def _collect_metrics(self):
        """Collect metrics from all collectors"""
        timestamp = datetime.now()
        
        # Collect from local machine (where probe is installed)
        for collector in self.collectors:
            try:
                metrics = collector.collect()
                for metric in metrics:
                    metric['timestamp'] = timestamp.isoformat()
                    self.buffer.append(metric)
                    
                    # Prevent buffer overflow
                    if len(self.buffer) > self.max_buffer_size:
                        self._send_metrics()
                        
            except Exception as e:
                logger.error(f"Error collecting from {collector.__class__.__name__}: {e}")
        
        # Collect from remote servers (PRTG-style agentless)
        self._collect_remote_servers()
        
        # Collect standalone sensors (HTTP, SNMP, etc.)
        self._collect_standalone_sensors()
        
        # Collect Hyper-V hosts via WMI
        self._collect_hyperv_hosts()
        
        # Collect from Kubernetes clusters (if collector is available)
        if self.kubernetes_collector:
            try:
                logger.info("🔍 Starting Kubernetes collection...")
                self.kubernetes_collector.collect_all_clusters()
            except Exception as e:
                logger.error(f"Error collecting Kubernetes metrics: {e}")
    
    def _collect_remote_servers(self):
        """
        Collect metrics from remote servers (PRTG-style agentless)
        Fetches list of servers from API and collects via WMI/SNMP
        """
        try:
            # Get list of servers assigned to this probe
            with httpx.Client(timeout=10.0, verify=False) as client:
                response = client.get(
                    f"{self.config.api_url}/api/v1/probes/servers",
                    params={"probe_token": self.config.probe_token}
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch remote servers: {response.status_code}")
                    return
                
                servers = response.json()
                logger.info(f"Found {len(servers)} servers to monitor remotely")
                
                if not servers:
                    logger.debug("No remote servers configured")
                    return
                
                # Get local machine info to skip it
                import socket
                local_hostname = socket.gethostname().lower()
                local_ip = socket.gethostbyname(socket.gethostname())
                
                # Rate limiter global — evita sobrecarga com muitos servidores simultâneos
                rate_limiter = get_rate_limiter() if RATE_LIMITER_AVAILABLE else None

                for server in servers:
                    hostname = server.get('hostname', '').lower()
                    ip_address = server.get('ip_address', '')

                    # Skip local machine (already collected above)
                    if hostname == local_hostname or ip_address == local_ip:
                        logger.debug(f"Skipping local machine: {hostname}")
                        continue

                    slot = None
                    try:
                        # Rate limiter via context manager (GlobalRateLimiter)
                        if rate_limiter:
                            slot = rate_limiter.acquire_slot(sensor_id=hostname, timeout=30)
                            try:
                                slot.__enter__()
                            except RuntimeError:
                                logger.warning(f"Rate limiter: fila cheia, pulando {hostname}")
                                slot = None
                                continue

                        logger.info(f"Collecting from remote server: {hostname} ({ip_address})")

                        # Collect based on protocol
                        protocol = server.get('monitoring_protocol', 'wmi')

                        if protocol == 'snmp':
                            logger.info(f"Using SNMP for {hostname}")
                            self._collect_snmp_remote(server)
                        elif protocol == 'wmi' or server.get('wmi_enabled'):
                            logger.info(f"Using WMI for {hostname}")
                            self._collect_wmi_remote(server)
                        else:
                            logger.info(f"Protocol '{protocol}' - trying WMI credential fallback for {hostname}")
                            self._collect_wmi_remote(server)

                    except Exception as e:
                        logger.error(f"Error collecting from {server.get('hostname')}: {e}", exc_info=True)
                    finally:
                        if slot:
                            slot.__exit__(None, None, None)
                        
        except Exception as e:
            logger.error(f"Error fetching remote servers: {e}", exc_info=True)
    
    def _collect_wmi_remote(self, server):
        """
        Coleta métricas de servidor Windows remoto via WMI Engine + SmartCollector.
        Usa Connection Pool para reutilizar conexões e evitar sobrecarga do wmiprvse.exe.
        Hierarquia: PerfCounter → WQL → Registry (fallback automático)
        """
        try:
            from engine.wmi_pool import get_pool
            from engine.smart_collector import SmartCollector

            hostname = server.get('hostname') or server.get('ip_address')
            server_id = server.get('id')

            credential = self._get_server_credential(server_id)

            if not credential:
                logger.warning(f"⚠️ Nenhuma credencial WMI para {hostname} (ID: {server_id}) - usando PING only")
                self._collect_ping_only(server)
                return

            if credential.get('credential_type') != 'wmi':
                logger.warning(f"Credencial para {hostname} não é do tipo WMI - usando PING only")
                self._collect_ping_only(server)
                return

            username = credential.get('wmi_username')
            password = credential.get('wmi_password')
            domain = credential.get('wmi_domain', '')

            if not username or not password:
                logger.warning(f"Credencial WMI incompleta para {hostname}")
                return

            logger.info(f"🔐 Credencial: {credential.get('name')} | Usuário: {domain}\\{username}")

            # Adquirir conexão do pool (reutiliza se disponível)
            pool = get_pool()
            conn = pool.acquire(hostname, username, password, domain)

            if not conn:
                logger.error(f"❌ Não foi possível adquirir conexão WMI para {hostname}")
                return

            try:
                # SmartCollector decide automaticamente: PerfCounter → WQL → Registry
                sc = SmartCollector(wmi_connection=conn)
                all_metrics = sc.collect_all()

                timestamp = datetime.now().isoformat()
                for metric in all_metrics:
                    metric['timestamp'] = timestamp
                    metric['hostname'] = server.get('hostname')
                    metric['server_id'] = server_id
                    # Incluir ip_address no metadata para que a API atualize o servidor
                    # (mesmo comportamento do PRTG/Zabbix: a sonda conhece o IP do host monitorado)
                    if 'metadata' not in metric:
                        metric['metadata'] = {}
                    if server.get('ip_address'):
                        metric['metadata']['ip_address'] = server.get('ip_address')
                    self.buffer.append(metric)

                # Log do método usado (diagnóstico de performance)
                report = sc.get_method_report()
                logger.info(
                    f"✅ WMI {hostname}: {len(all_metrics)} métricas | "
                    f"métodos={report['methods_in_use']} | "
                    f"latências={report['query_latency_ms']}"
                )

                # Enviar catálogo de serviços descobertos para a API (estilo PRTG/Zabbix)
                # Faz upsert de sensores tipo 'service' — usuário seleciona quais monitorar na UI
                self._sync_services_discovery(server_id, conn, hostname=hostname)

            finally:
                pool.release(hostname, conn)

        except Exception as e:
            logger.error(f"❌ WMI collection failed for {server.get('hostname')}: {e}", exc_info=True)

    def _sync_services_discovery(self, server_id: int, wmi_conn, hostname: str = None):
        """
        Envia catálogo de serviços Windows descobertos via WMI para a API.
        Estilo PRTG/Zabbix: sonda descobre → API armazena → usuário seleciona na UI.
        Apenas serviços com StartMode=Auto são enviados.
        """
        try:
            from engine.wmi_engine import WMIEngine
            engine = WMIEngine(wmi_conn)
            # Coletar catálogo completo (sem filtrar por is_active — isso é papel da UI)
            rows = wmi_conn.query(
                "SELECT Name,DisplayName,State,StartMode FROM Win32_Service WHERE StartMode='Auto'"
            )
            if not rows:
                logger.debug(f"Nenhum serviço Auto encontrado para server_id={server_id}")
                return

            services = [
                {
                    "service_name": r.Name,
                    "display_name": r.DisplayName or r.Name,
                    "state": r.State or "Unknown",
                    "start_mode": r.StartMode or "Auto",
                }
                for r in rows
            ]

            with httpx.Client(timeout=15.0, verify=False) as client:
                resp = client.post(
                    f"{self.config.api_url}/api/v1/servers/{server_id}/services/sync",
                    json={
                        "probe_token": self.config.probe_token,
                        "services": services,
                    }
                )
                if resp.status_code == 200:
                    result = resp.json()
                    # Apenas serviços que o usuário ativou na UI recebem métricas
                    active_services = set(result.get('active_services', []))
                    logger.info(
                        f"🔍 Service discovery server_id={server_id}: "
                        f"{result.get('created', 0)} novos, {result.get('updated', 0)} atualizados "
                        f"({len(services)} total, {len(active_services)} ativos)"
                    )
                    # Enfileirar métricas APENAS para serviços ativos (selecionados pelo usuário)
                    timestamp = datetime.now().isoformat()
                    srv_hostname = hostname or f'server_{server_id}'
                    enqueued = 0
                    for svc in services:
                        if svc['service_name'] not in active_services:
                            continue  # Ignorar serviços não selecionados pelo usuário
                        is_running = svc['state'].lower() == 'running'
                        self.buffer.append({
                            'hostname': srv_hostname,
                            'server_id': server_id,
                            'sensor_type': 'service',
                            'name': f"Service {svc['service_name']}",
                            'value': 1 if is_running else 0,
                            'unit': 'state',
                            'status': 'ok' if is_running else 'warning',
                            'timestamp': timestamp,
                            'metadata': {
                                'service_name': svc['service_name'],
                                'display_name': svc['display_name'],
                                'state': svc['state'],
                                'start_mode': svc['start_mode'],
                            }
                        })
                        enqueued += 1
                    logger.info(f"📊 {enqueued}/{len(services)} métricas de serviço enfileiradas para {srv_hostname}")
                else:
                    logger.warning(f"Service sync falhou: HTTP {resp.status_code} — {resp.text[:200]}")

        except Exception as e:
            logger.warning(f"Service discovery falhou para server_id={server_id}: {e}")
    
    def _collect_snmp_remote(self, server):
            """Collect metrics from remote device via SNMP"""
            try:
                from collectors.snmp_collector import SNMPCollector

                hostname = server.get('ip_address') or server.get('hostname')
                community = server.get('snmp_community', 'public')
                version = server.get('snmp_version', '2c')
                port = server.get('snmp_port', 161)

                # Normalizar version (remover 'v' se existir)
                if version and version.startswith('v'):
                    version = version[1:]  # Remove 'v' do início

                logger.info(f"Collecting SNMP metrics from {hostname} (v{version})")

                collector = SNMPCollector()
                metrics = []

                if version == '2c':
                    result = collector.collect_snmp_v2c(
                        host=hostname,
                        community=community,
                        port=port
                    )

                    if result.get('status') == 'success':
                        logger.debug(f"SNMP v2c collected {len(result.get('data', {}))} OIDs from {hostname}")
                    else:
                        logger.warning(f"SNMP v2c failed for {hostname}: {result.get('error')}")

                    # Converter resultado SNMP em métricas
                    metrics = self._parse_snmp_metrics(result, server)
                    logger.info(f"Parsed {len(metrics)} metrics from SNMP data")
                elif version == '3':
                    metrics = collector.collect_snmp_v3(
                        hostname=hostname,
                        username=server.get('snmp_username'),
                        auth_password=server.get('snmp_auth_password'),
                        priv_password=server.get('snmp_priv_password'),
                        auth_protocol=server.get('snmp_auth_protocol', 'SHA'),
                        priv_protocol=server.get('snmp_priv_protocol', 'AES'),
                        port=port
                    )

                # Adicionar métricas ao buffer
                timestamp = datetime.now().isoformat()
                for metric in metrics:
                    metric['timestamp'] = timestamp
                    metric['hostname'] = server.get('hostname')
                    if 'metadata' not in metric:
                        metric['metadata'] = {}
                    if server.get('ip_address'):
                        metric['metadata']['ip_address'] = server.get('ip_address')
                    self.buffer.append(metric)

                logger.info(f"Collected {len(metrics)} SNMP metrics from {hostname}")

                # SEMPRE coletar PING para servidores SNMP (independente do sucesso)
                logger.debug(f"Collecting PING metric for SNMP server {hostname}")
                self._collect_ping_only(server)

            except ImportError as ie:
                logger.error(f"ImportError in SNMP collection: {ie}", exc_info=True)
                logger.warning(f"pysnmp not installed or import error, falling back to PING for {server.get('hostname')}")
                self._collect_ping_only(server)
            except Exception as e:
                logger.error(f"SNMP collection failed for {server.get('hostname')}: {e}", exc_info=True)
                # Fallback to PING
                self._collect_ping_only(server)

    
    def _collect_ping_only(self, server):
        """
        DESABILITADO: PING agora é feito direto do servidor Linux (worker).
        Mantido apenas para compatibilidade com código legado.
        """
        logger.info(f"⚠️ PING desabilitado na probe - feito pelo servidor central (worker)")
        return  # Não coleta PING
    def _collect_standalone_sensors(self):
        """Coleta sensores standalone: HTTP, SNMP, etc. (estilo PRTG - probe faz o request)"""
        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                response = client.get(
                    f"{self.config.api_url}/api/v1/sensors/standalone/by-probe",
                    params={"probe_token": self.config.probe_token}
                )
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch standalone sensors: {response.status_code}")
                    return
                sensors = response.json()

            if not sensors:
                return

            logger.info(f"Collecting {len(sensors)} standalone sensors")
            timestamp = datetime.now()

            for sensor in sensors:
                # ── HTTP sensors ──
                if (sensor.get('sensor_type') == 'http' or sensor.get('http_url')) and sensor.get('http_url'):
                    try:
                        start = time.time()
                        with httpx.Client(timeout=15.0, verify=False, follow_redirects=True) as http_client:
                            resp = http_client.request(
                                method=sensor.get('http_method', 'GET'),
                                url=sensor['http_url']
                            )
                        elapsed_ms = (time.time() - start) * 1000
                        status = 'ok' if resp.status_code < 400 else 'critical'
                        logger.info(f"HTTP {sensor['name']}: {resp.status_code} in {elapsed_ms:.0f}ms")
                    except Exception as e:
                        elapsed_ms = 0
                        status = 'critical'
                        logger.warning(f"HTTP {sensor['name']} unreachable: {e}")

                    self.buffer.append({
                        'sensor_id': sensor['id'],
                        'sensor_type': 'http',
                        'name': sensor['name'],
                        'value': round(elapsed_ms, 2),
                        'unit': 'ms',
                        'status': status,
                        'timestamp': timestamp.isoformat(),
                        'hostname': '__standalone__',
                        'metadata': {'sensor_id': sensor['id']}
                    })

                # ── SNMP sensors (UPS, switches, APs, etc.) ──
                elif sensor.get('sensor_type') in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch') and sensor.get('ip_address'):
                    try:
                        self._collect_snmp_standalone(sensor, timestamp)
                    except Exception as e:
                        logger.warning(f"SNMP {sensor['name']} error: {e}")

        except Exception as e:
            logger.error(f"Error collecting standalone sensors: {e}")

    def _collect_snmp_standalone(self, sensor, timestamp):
        """Coleta SNMP de sensor standalone (UPS, switch, AP, etc.)."""
        ip = sensor.get('ip_address')
        community = sensor.get('snmp_community') or 'public'
        port = sensor.get('snmp_port') or 161
        name = sensor.get('name', 'SNMP')

        try:
            from collectors.snmp_collector import SNMPCollector
            collector = SNMPCollector()
            # Coleta básica: sysUpTime, sysDescr + OIDs UPS se disponíveis
            result = collector.collect_device(ip, community, port)
            if result and isinstance(result, list):
                for metric in result:
                    metric['sensor_id'] = sensor['id']
                    metric['hostname'] = '__standalone__'
                    metric['timestamp'] = timestamp.isoformat()
                    metric['metadata'] = {'sensor_id': sensor['id']}
                    self.buffer.append(metric)
                logger.info(f"SNMP {name} ({ip}): {len(result)} metrics")
            else:
                # Fallback: ping SNMP para verificar se está online
                self._snmp_ping_check(sensor, timestamp, ip, community, port)
        except ImportError:
            # SNMPCollector não disponível, fazer check básico
            self._snmp_ping_check(sensor, timestamp, ip, community, port)
        except Exception as e:
            logger.warning(f"SNMP {name} ({ip}) failed: {e}")
            self.buffer.append({
                'sensor_id': sensor['id'],
                'sensor_type': sensor.get('sensor_type', 'snmp'),
                'name': name,
                'value': 0,
                'unit': 'status',
                'status': 'critical',
                'timestamp': timestamp.isoformat(),
                'hostname': '__standalone__',
                'metadata': {'sensor_id': sensor['id'], 'error': str(e)}
            })

    def _snmp_ping_check(self, sensor, timestamp, ip, community, port):
        """Check básico SNMP: tenta ler sysUpTime para verificar se dispositivo responde."""
        import subprocess
        name = sensor.get('name', 'SNMP')
        try:
            # Tenta ping TCP na porta SNMP como fallback
            import socket
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            # Enviar SNMP GET sysUpTime.0 (OID 1.3.6.1.2.1.1.3.0)
            # Simplificado: apenas verificar se a porta responde
            sock.sendto(b'\x30\x26\x02\x01\x01\x04\x06public\xa0\x19\x02\x04\x00\x00\x00\x01\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00', (ip, port))
            try:
                data, addr = sock.recvfrom(1024)
                elapsed_ms = (time.time() - start) * 1000
                status = 'ok'
                value = round(elapsed_ms, 2)
                logger.info(f"SNMP {name} ({ip}): online ({elapsed_ms:.0f}ms)")
            except socket.timeout:
                status = 'critical'
                value = 0
                logger.warning(f"SNMP {name} ({ip}): timeout")
            finally:
                sock.close()
        except Exception as e:
            status = 'critical'
            value = 0
            logger.warning(f"SNMP {name} ({ip}): check failed: {e}")

        self.buffer.append({
            'sensor_id': sensor['id'],
            'sensor_type': sensor.get('sensor_type', 'snmp'),
            'name': name,
            'value': value,
            'unit': 'ms',
            'status': status,
            'timestamp': timestamp.isoformat(),
            'hostname': '__standalone__',
            'metadata': {'sensor_id': sensor['id']}
        })

    def _collect_hyperv_hosts(self):
        """Collect Hyper-V metrics from configured hosts and send to API."""
        # Pre-configured Hyper-V hosts
        hyperv_hosts = [
            {"hostname": "SRVHVSPRD010", "ip": "192.168.31.110"},
            {"hostname": "SRVHVSPRD011", "ip": "192.168.31.111"},
        ]
        try:
            collector = HyperVWMICollector(
                api_url=self.config.api_url,
                probe_token=self.config.probe_token,
            )
            payloads = collector.collect_all(hyperv_hosts)
            if payloads:
                logger.info(f"🖥️ HyperV: collected {len(payloads)} hosts")
                collector.send_to_api(payloads)
            else:
                logger.debug("HyperV: no data collected")
        except Exception as e:
            logger.error(f"HyperV collection error: {e}")

    def _parse_snmp_metrics(self, snmp_result, server):
        """Parse SNMP raw data into metrics format"""
        metrics = []

        if snmp_result.get('status') != 'success':
            logger.error(f"SNMP collection failed: {snmp_result.get('error')}")
            return metrics

        data = snmp_result.get('data', {})
        server_id = server.get('id')
        
        logger.debug(f"Parsing {len(data)} SNMP OIDs for server {server.get('hostname')}")

        # OIDs padrão para Linux
        OID_CPU_IDLE = '1.3.6.1.4.1.2021.11.11.0'  # ssCpuIdle
        OID_MEM_TOTAL = '1.3.6.1.4.1.2021.4.5.0'   # memTotalReal
        OID_MEM_AVAIL = '1.3.6.1.4.1.2021.4.6.0'   # memAvailReal
        OID_DISK_PATH = '1.3.6.1.4.1.2021.9.1.2'   # dskPath
        OID_DISK_PERCENT = '1.3.6.1.4.1.2021.9.1.9' # dskPercent
        OID_LOAD_1MIN = '1.3.6.1.4.1.2021.10.1.3.1' # laLoad.1

        # CPU (converter idle para usage)
        for oid, value in data.items():
            if OID_CPU_IDLE in oid:
                try:
                    cpu_idle = float(value)
                    cpu_usage = 100 - cpu_idle
                    logger.debug(f"CPU: {cpu_usage:.1f}% (idle: {cpu_idle}%)")
                    metrics.append({
                        'type': 'cpu',
                        'name': 'CPU',
                        'value': cpu_usage,
                        'unit': 'percent',
                        'status': 'critical' if cpu_usage > 95 else ('warning' if cpu_usage > 80 else 'ok'),
                        'server_id': server_id
                    })
                except ValueError as e:
                    logger.error(f"Error parsing CPU value '{value}': {e}")

        # Memória
        # OIDs adicionais para calcular memória disponível real (incluindo buffers/cache do Linux)
        OID_MEM_BUFFER = '1.3.6.1.4.1.2021.4.14.0'  # memBuffer
        OID_MEM_CACHED = '1.3.6.1.4.1.2021.4.15.0'  # memCached

        mem_total = None
        mem_avail = None
        mem_buffer = 0
        mem_cached = 0
        for oid, value in data.items():
            if OID_MEM_TOTAL in oid:
                try:
                    mem_total = float(value)
                    logger.debug(f"Memory total: {mem_total} KB")
                except ValueError as e:
                    logger.error(f"Error parsing mem_total '{value}': {e}")
            elif OID_MEM_AVAIL in oid:
                try:
                    mem_avail = float(value)
                    logger.debug(f"Memory available (raw): {mem_avail} KB")
                except ValueError as e:
                    logger.error(f"Error parsing mem_avail '{value}': {e}")
            elif OID_MEM_BUFFER in oid:
                try:
                    mem_buffer = float(value)
                    logger.debug(f"Memory buffer: {mem_buffer} KB")
                except ValueError:
                    pass
            elif OID_MEM_CACHED in oid:
                try:
                    mem_cached = float(value)
                    logger.debug(f"Memory cached: {mem_cached} KB")
                except ValueError:
                    pass

        if mem_total and mem_avail is not None:
            # Memória realmente disponível = livre + buffers + cache (como 'free -h' mostra)
            mem_really_avail = mem_avail + mem_buffer + mem_cached
            mem_used_percent = ((mem_total - mem_really_avail) / mem_total) * 100
            mem_used_percent = max(0, min(100, mem_used_percent))  # clamp 0-100
            logger.debug(f"Memory: {mem_used_percent:.1f}% (avail={mem_avail}, buf={mem_buffer}, cached={mem_cached})")
            metrics.append({
                'type': 'memory',
                'name': 'Memória',
                'value': round(mem_used_percent, 2),
                'unit': 'percent',
                'status': 'critical' if mem_used_percent > 95 else ('warning' if mem_used_percent > 80 else 'ok'),
                'server_id': server_id
            })
        else:
            logger.warning(f"Memory data incomplete: total={mem_total}, avail={mem_avail}")

        # Discos (simplificado - pegar primeiro disco)
        for oid, value in data.items():
            if OID_DISK_PERCENT in oid:
                try:
                    disk_percent = float(value)
                    disk_name = "Disco"
                    logger.debug(f"Disk: {disk_percent}%")
                    metrics.append({
                        'type': 'disk',
                        'name': disk_name,
                        'value': disk_percent,
                        'unit': 'percent',
                        'status': 'critical' if disk_percent > 95 else ('warning' if disk_percent > 85 else 'ok'),
                        'server_id': server_id
                    })
                    break  # Apenas primeiro disco por enquanto
                except ValueError:
                    pass

        # Network (simplificado - apenas uptime como proxy)
        # Uptime
        for oid, value in data.items():
            if '1.3.6.1.2.1.1.3.0' in oid:  # sysUpTime
                try:
                    # Converter timeticks para dias
                    timeticks = int(value)
                    uptime_days = timeticks / (100 * 60 * 60 * 24)
                    metrics.append({
                        'type': 'system',
                        'name': 'Uptime',
                        'value': uptime_days,
                        'unit': 'days',
                        'status': 'ok',
                        'server_id': server_id
                    })
                except ValueError:
                    pass

        logger.info(f"Parsed {len(metrics)} metrics from SNMP data")
        if len(metrics) == 0:
            logger.warning(f"No metrics parsed! OIDs in data: {list(data.keys())[:10]}")
        
        return metrics

    
    def _reconnect_api(self):
        """Try to reconnect to API by auto-discovering new URL"""
        logger.warning("🔄 Tentando reconectar ao servidor API...")
        
        # Reload config to get latest settings
        self.config.load_config()
        
        logger.info(f"✅ Reconectado ao servidor em: {self.config.api_url}")
    
    def _send_metrics(self):
        """Send buffered metrics to API"""
        if not self.buffer:
            return
        
        try:
            # Get hostname and IP for this machine (default for local metrics)
            import socket
            local_hostname = socket.gethostname()
            
            # Get local IP address
            try:
                local_ip = socket.gethostbyname(local_hostname)
            except:
                local_ip = "127.0.0.1"
            
            # Get public IP (if available)
            public_ip = None
            try:
                with httpx.Client(timeout=5.0) as client:
                    response = client.get("https://api.ipify.org?format=json")
                    if response.status_code == 200:
                        public_ip = response.json().get("ip")
            except:
                pass  # Public IP is optional
            
            # Format metrics for the new endpoint
            formatted_metrics = []
            for metric in self.buffer:
                # Use hostname from metric if present (remote server), otherwise use local
                hostname = metric.get("hostname", local_hostname)
                
                # Prepare metadata
                metadata = metric.get("metadata", {})
                
                # Add IP information to metadata (only for local machine metrics)
                if hostname == local_hostname:
                    metadata["ip_address"] = local_ip
                    if public_ip:
                        metadata["public_ip"] = public_ip
                
                formatted_metrics.append({
                    "hostname": hostname,
                    "sensor_type": metric.get("sensor_type", metric.get("type", "unknown")),
                    "sensor_name": metric.get("name", "unknown"),
                    "value": metric.get("value", 0),
                    "unit": metric.get("unit"),
                    "status": metric.get("status", "ok"),
                    "timestamp": metric.get("timestamp"),
                    "metadata": metadata
                })
            
            # Debug: log sample metrics
            if formatted_metrics:
                logger.debug(f"Sending {len(formatted_metrics)} metrics")
                logger.debug(f"Sample metric: {formatted_metrics[0]}")
            
            with httpx.Client(timeout=30.0, verify=False) as client:
                response = client.post(
                    f"{self.config.api_url}/api/v1/metrics/probe/bulk",
                    json={
                        "probe_token": self.config.probe_token,
                        "metrics": formatted_metrics
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Sent {len(self.buffer)} metrics successfully")
                    self.buffer = []
                else:
                    logger.error(f"Failed to send metrics: {response.status_code} - {response.text}")
                    
        except (httpx.ConnectTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as e:
            logger.error(f"Connection error sending metrics: {e}")
            # Try to reconnect
            self._reconnect_api()
            # Keep buffer for retry
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size:]
        except Exception as e:
            logger.error(f"Error sending metrics: {e}", exc_info=True)
            # Keep buffer for retry, but limit size
            if len(self.buffer) > self.max_buffer_size:
                self.buffer = self.buffer[-self.max_buffer_size:]
    
    def _auto_register_server(self):
        """Auto-register this server if it doesn't exist"""
        try:
            import socket
            import platform
            
            # Get machine information
            hostname = socket.gethostname()
            
            # Try to get IP address
            try:
                ip_address = socket.gethostbyname(hostname)
            except:
                ip_address = "127.0.0.1"
            
            # Get OS info
            os_info = f"{platform.system()} {platform.release()}"
            
            logger.info(f"🔍 Checking if server '{hostname}' is registered...")
            
            with httpx.Client(timeout=10.0, verify=False) as client:
                # Check if server already exists
                check_response = client.get(
                    f"{self.config.api_url}/api/v1/servers/check",
                    params={
                        "probe_token": self.config.probe_token,
                        "hostname": hostname
                    }
                )
                
                if check_response.status_code == 200:
                    data = check_response.json()
                    if data.get("exists"):
                        logger.info(f"✓ Server '{hostname}' already registered (ID: {data.get('server_id')})")
                        return
                
                # Server doesn't exist, register it
                logger.info(f"📝 Auto-registering server '{hostname}'...")
                
                register_response = client.post(
                    f"{self.config.api_url}/api/v1/servers/auto-register",
                    params={"probe_token": self.config.probe_token},
                    json={
                        "hostname": hostname,
                        "ip_address": ip_address,
                        "os_info": os_info,
                        "description": f"Auto-registered by probe on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                )
                
                if register_response.status_code == 200:
                    server_data = register_response.json()
                    logger.info(f"✅ Server '{hostname}' registered successfully! (ID: {server_data.get('id')})")
                    logger.info(f"   IP: {ip_address}")
                    logger.info(f"   OS: {os_info}")
                else:
                    logger.warning(f"⚠️ Failed to auto-register server: {register_response.status_code}")
                    logger.warning(f"   Response: {register_response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Error in auto-register: {e}")
            # Don't fail the probe if auto-register fails
    
    def _send_heartbeat(self):
        """Send heartbeat to API"""
        try:
            import psutil, os
            cpu_percent = psutil.cpu_percent(interval=None)
            if cpu_percent == 0.0:
                cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_mb = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        except Exception as e:
            logger.warning(f"psutil error: {e}")
            cpu_percent = 0.0
            memory_mb = 0.0

        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                response = client.post(
                    f"{self.config.api_url}/api/v1/probes/heartbeat",
                    params={
                        "probe_token": self.config.probe_token,
                        "version": "1.0.0",
                        "cpu_percent": round(cpu_percent, 1),
                        "memory_mb": round(memory_mb, 1)
                    }
                )
                
                if response.status_code == 200:
                    logger.debug("Heartbeat sent successfully")
                else:
                    logger.warning(f"Heartbeat failed: {response.status_code}")
                    
        except (httpx.ConnectTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as e:
            logger.error(f"Connection error in heartbeat: {e}")
            # Try to reconnect
            self._reconnect_api()
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")

if __name__ == "__main__":
    # Run probe directly
    probe = ProbeCore()
    try:
        probe.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        probe.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
