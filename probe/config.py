import yaml
import socket
import httpx
from pathlib import Path
from typing import List, Dict, Optional

class ProbeConfig:
    def __init__(self, config_file: str = "config.yaml"):
        # Try to find config file in multiple locations
        possible_paths = [
            Path(config_file),  # Current directory
            Path("probe") / config_file,  # probe subdirectory
            Path(__file__).parent / config_file,  # Same directory as this file
        ]
        
        self.config_file = None
        for path in possible_paths:
            if path.exists():
                self.config_file = path
                break
        
        if self.config_file is None:
            # Use default location (same directory as this file)
            self.config_file = Path(__file__).parent / config_file
        
        self.load_config()
    
    def _get_local_ips(self) -> List[str]:
        """Get all local IP addresses"""
        ips = ['localhost', '127.0.0.1']
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip not in ips:
                ips.append(local_ip)
        except:
            pass
        return ips
    
    def _test_api_connection(self, url: str, token: str) -> bool:
        """Test if API is reachable at given URL"""
        try:
            with httpx.Client(timeout=3.0, verify=False) as client:
                response = client.post(
                    f"{url}/api/v1/probes/heartbeat",
                    params={"probe_token": token, "version": "1.0.0"}
                )
                return response.status_code == 200
        except:
            return False
    
    def _auto_discover_api(self, token: str) -> Optional[str]:
        """Auto-discover API URL by trying common addresses"""
        print("🔍 Auto-descobrindo servidor API...")
        
        # Try common addresses
        candidates = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        
        # Add local network IPs
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            candidates.append(f"http://{local_ip}:8000")
        except:
            pass
        
        # Try each candidate
        for url in candidates:
            print(f"   Tentando: {url}")
            if self._test_api_connection(url, token):
                print(f"✅ Servidor encontrado em: {url}")
                return url
        
        print("❌ Servidor não encontrado em nenhum endereço")
        return None
    
    def load_config(self):
        """Load configuration from file"""
        print(f"🔍 Procurando configuração em: {self.config_file}")
        if self.config_file.exists():
            print(f"✅ Configuração encontrada: {self.config_file}")
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            print(f"⚠️  Configuração não encontrada, criando padrão em: {self.config_file}")
            config = self.get_default_config()
            self.save_config(config)
        
        # Read from YAML structure
        server_config = config.get('server', {})
        self.api_url = f"{server_config.get('protocol', 'http')}://{server_config.get('host', 'localhost')}:{server_config.get('port', 8000)}"
        self.probe_token = config.get('token', '')
        self.collection_interval = config.get('collection_interval', 60)
        self.monitored_services = config.get('monitored_services', [])
        self.udm_targets = config.get('udm_targets', [])
        
        # Auto-discover API if current URL doesn't work
        if self.probe_token:
            print(f"📡 Testando API URL: {self.api_url}")
            if not self._test_api_connection(self.api_url, self.probe_token):
                print(f"⚠️  API não acessível em {self.api_url}")
                discovered_url = self._auto_discover_api(self.probe_token)
                if discovered_url and discovered_url != self.api_url:
                    print(f"🔄 Atualizando URL de {self.api_url} para {discovered_url}")
                    self.api_url = discovered_url
                    # Update config
                    from urllib.parse import urlparse
                    parsed = urlparse(discovered_url)
                    server_config['protocol'] = parsed.scheme
                    server_config['host'] = parsed.hostname
                    server_config['port'] = parsed.port or 8000
                    config['server'] = server_config
                    self.save_config(config)
            else:
                print(f"✅ API acessível em {self.api_url}")
        
        print(f"📡 API URL: {self.api_url}")
        print(f"🔑 Token: {self.probe_token[:10] if self.probe_token else '(vazio)'}...")
        print(f"⏱️  Intervalo: {self.collection_interval}s")
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "server": {
                "host": "localhost",
                "port": 8000,
                "protocol": "http"
            },
            "token": "",
            "probe": {
                "name": "PROBE001",
                "location": ""
            },
            "collection_interval": 60,
            "logging": {
                "level": "INFO",
                "file": "logs/probe.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "collectors": {
                "system": True,
                "ping": True,
                "snmp": True,
                "docker": False,
                "kubernetes": False,
                "wmi_remote": False
            },
            "monitored_services": [],
            "udm_targets": []
        }
