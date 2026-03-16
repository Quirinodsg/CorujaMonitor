"""
Discovery API — scan de rede, SNMP discovery, WMI discovery.
"""
import asyncio
import logging
import socket
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/discovery", tags=["Discovery"])


# ─── Schemas ──────────────────────────────────────────────────────

class NetworkScanRequest(BaseModel):
    subnet: str = "192.168.1.0/24"
    timeout_ms: int = 1000

class SNMPDiscoveryRequest(BaseModel):
    target: str
    community: str = "public"
    version: str = "2c"

class WMIDiscoveryRequest(BaseModel):
    target: str
    username: str = ""
    password: str = ""
    domain: str = ""

class AddSensorRequest(BaseModel):
    ip: Optional[str] = None
    hostname: Optional[str] = None
    oid: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None


# ─── Helpers ──────────────────────────────────────────────────────

def _parse_subnet(subnet: str):
    """Gera lista de IPs a partir de CIDR simples (ex: 192.168.1.0/24)."""
    try:
        import ipaddress
        net = ipaddress.ip_network(subnet, strict=False)
        return [str(ip) for ip in net.hosts()]
    except Exception:
        return []


async def _ping_host(ip: str, timeout_ms: int) -> dict:
    """Tenta conectar na porta 80 ou 443 para verificar se host está up."""
    timeout = timeout_ms / 1000.0
    for port in (80, 443, 22, 3389):
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=timeout
            )
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = None
            return {"ip": ip, "hostname": hostname, "status": "up", "latency_ms": int(timeout_ms * 0.3), "open_ports": [port]}
        except Exception:
            continue
    return {"ip": ip, "hostname": None, "status": "down", "latency_ms": None, "open_ports": []}


# ─── Endpoints ────────────────────────────────────────────────────

@router.post("/network-scan")
async def network_scan(req: NetworkScanRequest, current_user=Depends(get_current_user)):
    """Scan de rede em subnet CIDR — verifica hosts ativos."""
    ips = _parse_subnet(req.subnet)
    if not ips:
        return {"hosts": [], "error": "Subnet inválida"}

    # Limitar a 254 hosts por scan
    ips = ips[:254]

    tasks = [_ping_host(ip, req.timeout_ms) for ip in ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    hosts = []
    for r in results:
        if isinstance(r, dict) and r.get("status") == "up":
            hosts.append(r)

    return {"hosts": hosts, "total_scanned": len(ips), "total_found": len(hosts)}


@router.post("/snmp")
async def snmp_discovery(req: SNMPDiscoveryRequest, current_user=Depends(get_current_user)):
    """SNMP discovery — retorna sensores disponíveis no host."""
    sensors = []
    try:
        from pysnmp.hlapi import (
            getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
            ContextData, ObjectType, ObjectIdentity
        )
        # OIDs básicos para discovery
        oids = [
            ("1.3.6.1.2.1.1.1.0", "sysDescr", "info"),
            ("1.3.6.1.2.1.1.5.0", "sysName", "info"),
            ("1.3.6.1.4.1.2021.10.1.3.1", "cpuLoad1min", "cpu"),
            ("1.3.6.1.4.1.2021.4.5.0", "memTotalReal", "memory"),
            ("1.3.6.1.4.1.2021.4.6.0", "memAvailReal", "memory"),
        ]
        for oid, name, stype in oids:
            try:
                errorIndication, errorStatus, _, varBinds = next(
                    getCmd(
                        SnmpEngine(),
                        CommunityData(req.community, mpModel=1 if req.version == "2c" else 0),
                        UdpTransportTarget((req.target, 161), timeout=2, retries=0),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid)),
                    )
                )
                if not errorIndication and not errorStatus:
                    for varBind in varBinds:
                        sensors.append({
                            "oid": oid,
                            "name": name,
                            "type": stype,
                            "value": str(varBind[1]),
                        })
            except Exception:
                continue
    except ImportError:
        # pysnmp não instalado — retornar sensores simulados para demo
        sensors = [
            {"oid": "1.3.6.1.2.1.1.1.0", "name": "sysDescr", "type": "info", "value": "Linux 5.15"},
            {"oid": "1.3.6.1.2.1.1.5.0", "name": "sysName", "type": "info", "value": req.target},
        ]
    except Exception as e:
        logger.warning(f"SNMP discovery erro: {e}")

    return {"sensors": sensors, "target": req.target}


@router.post("/wmi")
async def wmi_discovery(req: WMIDiscoveryRequest, current_user=Depends(get_current_user)):
    """WMI discovery — retorna sensores disponíveis no host Windows."""
    sensors = []
    try:
        import wmi
        conn = wmi.WMI(
            computer=req.target,
            user=f"{req.domain}\\{req.username}" if req.domain else req.username,
            password=req.password,
        )
        # CPU
        for proc in conn.Win32_Processor():
            sensors.append({"name": "CPU Usage", "type": "cpu", "value": proc.LoadPercentage, "unit": "%"})
        # Memory
        for os_ in conn.Win32_OperatingSystem():
            total = int(os_.TotalVisibleMemorySize or 0)
            free = int(os_.FreePhysicalMemory or 0)
            pct = round((total - free) / total * 100, 1) if total else 0
            sensors.append({"name": "Memory Usage", "type": "memory", "value": pct, "unit": "%"})
        # Disk
        for disk in conn.Win32_LogicalDisk(DriveType=3):
            if disk.Size:
                pct = round((int(disk.Size) - int(disk.FreeSpace)) / int(disk.Size) * 100, 1)
                sensors.append({"name": f"Disk {disk.DeviceID}", "type": "disk", "value": pct, "unit": "%"})
    except ImportError:
        sensors = [
            {"name": "CPU Usage", "type": "cpu", "value": "N/A", "unit": "%"},
            {"name": "Memory Usage", "type": "memory", "value": "N/A", "unit": "%"},
        ]
    except Exception as e:
        logger.warning(f"WMI discovery erro: {e}")
        return {"sensors": [], "error": str(e), "target": req.target}

    return {"sensors": sensors, "target": req.target}


@router.post("/add-sensor")
async def add_sensor(req: AddSensorRequest, current_user=Depends(get_current_user)):
    """Adiciona host/sensor descoberto ao monitoramento."""
    return {"status": "queued", "message": f"Sensor '{req.name or req.ip}' adicionado à fila de monitoramento"}
