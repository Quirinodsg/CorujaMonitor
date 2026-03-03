import time
import json
import logging
from datetime import datetime
from pathlib import Path
import httpx
from typing import List, Dict, Any

from collectors.cpu_collector import CPUCollector
from collectors.memory_collector import MemoryCollector
from collectors.disk_collector import DiskCollector
from collectors.network_collector import NetworkCollector
from collectors.service_collector import ServiceCollector
from collectors.hyperv_collector import HyperVCollector
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
            # Service monitoring removed from default sensors
            # Services can be added manually if needed
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
                
                for server in servers:
                    try:
                        hostname = server.get('hostname', '').lower()
                        ip_address = server.get('ip_address', '')
                        
                        # Skip local machine (already collected above)
                        if hostname == local_hostname or ip_address == local_ip:
                            logger.debug(f"Skipping local machine: {hostname}")
                            continue
                        
                        logger.info(f"Collecting from remote server: {hostname} ({ip_address})")
                        
                        # Collect based on protocol
                        protocol = server.get('monitoring_protocol', 'wmi')
                        
                        if protocol == 'wmi' and server.get('wmi_enabled'):
                            logger.info(f"Using WMI for {hostname}")
                            self._collect_wmi_remote(server)
                        elif protocol == 'snmp':
                            logger.info(f"Using SNMP for {hostname}")
                            self._collect_snmp_remote(server)
                        else:
                            # No credentials or SNMP - try PING only
                            logger.info(f"Using PING only for {hostname}")
                            self._collect_ping_only(server)
                            
                    except Exception as e:
                        logger.error(f"Error collecting from {server.get('hostname')}: {e}", exc_info=True)
                        
        except Exception as e:
            logger.error(f"Error fetching remote servers: {e}", exc_info=True)
    
    def _collect_wmi_remote(self, server):
        """Collect metrics from remote Windows server via WMI"""
        try:
            from collectors.wmi_remote_collector import WMIRemoteCollector
            
            hostname = server.get('ip_address') or server.get('hostname')
            username = server.get('wmi_username')
            password = server.get('wmi_password')  # API will decrypt
            domain = server.get('wmi_domain', '')
            
            if not username or not password:
                logger.warning(f"WMI credentials not configured for {hostname}")
                return
            
            collector = WMIRemoteCollector(hostname, username, password, domain)
            
            # Collect all metrics
            timestamp = datetime.now().isoformat()
            
            # CPU
            cpu_metrics = collector.collect_cpu()
            for metric in cpu_metrics:
                metric['timestamp'] = timestamp
                metric['hostname'] = server.get('hostname')
                self.buffer.append(metric)
            
            # Memory
            mem_metrics = collector.collect_memory()
            for metric in mem_metrics:
                metric['timestamp'] = timestamp
                metric['hostname'] = server.get('hostname')
                self.buffer.append(metric)
            
            # Disk
            disk_metrics = collector.collect_disk()
            for metric in disk_metrics:
                metric['timestamp'] = timestamp
                metric['hostname'] = server.get('hostname')
                self.buffer.append(metric)
            
            # Services (if configured)
            if self.config.monitored_services:
                service_metrics = collector.collect_services(self.config.monitored_services)
                for metric in service_metrics:
                    metric['timestamp'] = timestamp
                    metric['hostname'] = server.get('hostname')
                    self.buffer.append(metric)
            
            logger.info(f"Collected WMI metrics from {hostname}")
            
        except Exception as e:
            logger.error(f"WMI collection failed for {server.get('hostname')}: {e}")
    
    def _collect_snmp_remote(self, server):
        """Collect metrics from remote device via SNMP"""
        try:
            from collectors.snmp_collector import SNMPCollector
            
            hostname = server.get('ip_address') or server.get('hostname')
            community = server.get('snmp_community', 'public')
            version = server.get('snmp_version', '2c')
            port = server.get('snmp_port', 161)
            
            logger.info(f"Collecting SNMP metrics from {hostname} (v{version})")
            
            collector = SNMPCollector()
            metrics = []
            
            if version == '2c':
                metrics = collector.collect_snmp_v2c(
                    hostname=hostname,
                    community=community,
                    port=port
                )
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
                self.buffer.append(metric)
            
            logger.info(f"Collected {len(metrics)} SNMP metrics from {hostname}")
            
        except ImportError:
            logger.warning(f"pysnmp not installed, falling back to PING for {server.get('hostname')}")
            self._collect_ping_only(server)
        except Exception as e:
            logger.error(f"SNMP collection failed for {server.get('hostname')}: {e}")
            # Fallback to PING
            self._collect_ping_only(server)
    
    def _collect_ping_only(self, server):
        """Collect only PING metric for servers without credentials"""
        try:
            import subprocess
            import platform
            
            hostname = server.get('ip_address') or server.get('hostname')
            
            # Ping command varies by OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', hostname]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            
            # Parse ping result
            is_online = result.returncode == 0
            latency = 0
            
            if is_online:
                # Extract latency from output
                output = result.stdout
                if 'time=' in output.lower():
                    try:
                        # Windows: "time=12ms" or "time<1ms"
                        # Linux: "time=12.3 ms"
                        import re
                        match = re.search(r'time[=<](\d+\.?\d*)', output.lower())
                        if match:
                            latency = float(match.group(1))
                    except:
                        latency = 1  # Default if can't parse
            
            metric = {
                'type': 'ping',
                'name': 'PING',
                'value': latency if is_online else 0,
                'unit': 'ms',
                'status': 'ok' if is_online else 'critical',
                'timestamp': datetime.now().isoformat(),
                'hostname': server.get('hostname'),
                'metadata': {
                    'target': hostname,
                    'collection_method': 'icmp_ping'
                }
            }
            
            self.buffer.append(metric)
            logger.debug(f"PING {hostname}: {'OK' if is_online else 'OFFLINE'} ({latency}ms)")
            
        except Exception as e:
            logger.error(f"PING failed for {server.get('hostname')}: {e}")
    
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
    
    def _send_heartbeat(self):
        """Send heartbeat to API"""
        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                response = client.post(
                    f"{self.config.api_url}/api/v1/probes/heartbeat",
                    params={
                        "probe_token": self.config.probe_token,
                        "version": "1.0.0"
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
