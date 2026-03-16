"""
TCP Port Sensor - Verifica conectividade TCP em portas específicas
Inclui validação de firewall para RPC (porta 135 + portas dinâmicas)
"""
import socket
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Portas RPC padrão
RPC_ENDPOINT_MAPPER_PORT = 135
RPC_DYNAMIC_PORTS = range(49152, 65536)

# Portas comuns para validação
COMMON_PORTS = {
    "rpc_epm": 135,
    "smb": 445,
    "rdp": 3389,
    "winrm_http": 5985,
    "winrm_https": 5986,
    "wmi_fixed": 24158,  # WMI fixed port (se configurado via GPO)
}


class TCPPortSensor:
    """
    Sensor TCP Port - verifica se porta está aberta e mede latência de conexão
    """

    def __init__(self, host: str, port: int, timeout: float = 3.0, retries: int = 2):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries

    def collect(self) -> Dict[str, Any]:
        """Testa conectividade TCP na porta especificada"""
        last_error = None

        for attempt in range(self.retries + 1):
            try:
                start = time.monotonic()
                with socket.create_connection((self.host, self.port), timeout=self.timeout):
                    elapsed_ms = (time.monotonic() - start) * 1000

                return {
                    "type": "tcp_port",
                    "name": f"TCP Port {self.port}",
                    "host": self.host,
                    "port": self.port,
                    "status": "ok",
                    "is_open": True,
                    "latency_ms": round(elapsed_ms, 2),
                    "value": round(elapsed_ms, 2),
                    "unit": "ms",
                    "metadata": {
                        "attempts": attempt + 1,
                        "collection_method": "tcp_connect",
                    },
                }

            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                last_error = str(e)
                if attempt < self.retries:
                    time.sleep(0.5)
                    continue

        return {
            "type": "tcp_port",
            "name": f"TCP Port {self.port}",
            "host": self.host,
            "port": self.port,
            "status": "critical",
            "is_open": False,
            "latency_ms": 0.0,
            "value": 0.0,
            "unit": "ms",
            "metadata": {
                "attempts": self.retries + 1,
                "error": last_error,
                "collection_method": "tcp_connect",
            },
        }


class RPCFirewallValidator:
    """
    Valida se as portas necessárias para WMI/RPC estão abertas.
    Fluxo: TCP 135 (RPC EPM) → porta dinâmica RPC (49152-65535)
    """

    def __init__(self, host: str, timeout: float = 3.0):
        self.host = host
        self.timeout = timeout

    def validate(self) -> Dict[str, Any]:
        """Valida conectividade RPC completa"""
        results = {}

        # 1. Testar porta 135 (RPC Endpoint Mapper) - OBRIGATÓRIA
        epm_sensor = TCPPortSensor(self.host, RPC_ENDPOINT_MAPPER_PORT, self.timeout)
        epm_result = epm_sensor.collect()
        results["rpc_endpoint_mapper_135"] = epm_result

        # 2. Testar SMB 445 (necessário para WMI em alguns cenários)
        smb_sensor = TCPPortSensor(self.host, 445, self.timeout)
        results["smb_445"] = smb_sensor.collect()

        # 3. Testar amostra de portas dinâmicas RPC (49152-65535)
        # Não testamos todas - apenas verificamos se a faixa está acessível
        dynamic_sample_ports = [49152, 49153, 49154, 49155]
        dynamic_open = []
        for port in dynamic_sample_ports:
            sensor = TCPPortSensor(self.host, port, timeout=1.0, retries=0)
            r = sensor.collect()
            if r["is_open"]:
                dynamic_open.append(port)

        results["dynamic_rpc_ports_sample"] = {
            "tested_ports": dynamic_sample_ports,
            "open_ports": dynamic_open,
            "status": "ok" if dynamic_open else "warning",
        }

        # Status geral
        epm_ok = epm_result["is_open"]
        overall_status = "ok" if epm_ok else "critical"

        return {
            "host": self.host,
            "overall_status": overall_status,
            "rpc_endpoint_mapper_open": epm_ok,
            "dynamic_ports_accessible": len(dynamic_open) > 0,
            "details": results,
            "recommendation": (
                "RPC/WMI firewall OK"
                if epm_ok
                else "Abrir porta TCP 135 e faixa 49152-65535 no firewall do host alvo"
            ),
        }

    def check_wmi_ports(self) -> List[Dict[str, Any]]:
        """Retorna lista de métricas de portas WMI para o sensor engine"""
        metrics = []
        validation = self.validate()

        metrics.append({
            "type": "tcp_port",
            "name": "RPC Endpoint Mapper (135)",
            "host": self.host,
            "port": 135,
            "status": "ok" if validation["rpc_endpoint_mapper_open"] else "critical",
            "is_open": validation["rpc_endpoint_mapper_open"],
            "value": 1 if validation["rpc_endpoint_mapper_open"] else 0,
            "unit": "state",
            "metadata": {"collection_method": "rpc_firewall_check"},
        })

        return metrics
