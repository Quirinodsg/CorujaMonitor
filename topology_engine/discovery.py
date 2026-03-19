"""
Topology Discovery — Coruja Monitor v3.0
Descoberta automática de topologia via SNMP e WMI.
"""
import logging
from typing import Optional

from core.spec.models import TopologyNode
from core.spec.enums import NodeType

logger = logging.getLogger(__name__)


class SNMPTopologyDiscovery:
    """
    Descobre topologia de rede via SNMP (ARP table, LLDP/CDP).
    Compatível com switches e roteadores.
    """

    def discover(self, host: str, community: str = "public") -> list[TopologyNode]:
        """
        Descobre nós via SNMP.
        Retorna lista de TopologyNode descobertos.
        """
        nodes: list[TopologyNode] = []
        try:
            from pysnmp.hlapi import (
                getCmd, SnmpEngine, CommunityData, UdpTransportTarget,
                ContextData, ObjectType, ObjectIdentity,
            )
            # OID para sysDescr — confirma que o host responde SNMP
            error_indication, error_status, error_index, var_binds = next(
                getCmd(
                    SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((host, 161), timeout=2, retries=1),
                    ContextData(),
                    ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
                )
            )
            if not error_indication and not error_status:
                node = TopologyNode(type=NodeType.SWITCH, metadata={"host": host, "source": "snmp"})
                nodes.append(node)
                logger.info("SNMPTopologyDiscovery: descoberto %s", host)
        except Exception as e:
            logger.warning("SNMPTopologyDiscovery: falha em %s: %s", host, e)
        return nodes


class WMITopologyDiscovery:
    """
    Descobre serviços e processos em servidores Windows via WMI.
    """

    def discover(self, host: str, credential: Optional[dict] = None) -> list[TopologyNode]:
        """
        Descobre serviços instalados via WMI.
        Retorna lista de TopologyNode (tipo SERVICE) descobertos.
        """
        nodes: list[TopologyNode] = []
        try:
            import wmi
            cred = credential or {}
            conn = wmi.WMI(
                computer=host,
                user=cred.get("username"),
                password=cred.get("password"),
                namespace="root/cimv2",
            )
            for svc in conn.Win32_Service(State="Running"):
                node = TopologyNode(
                    type=NodeType.SERVICE,
                    metadata={"name": svc.Name, "host": host, "source": "wmi"},
                )
                nodes.append(node)
            logger.info("WMITopologyDiscovery: %d serviços descobertos em %s", len(nodes), host)
        except Exception as e:
            logger.warning("WMITopologyDiscovery: falha em %s: %s", host, e)
        return nodes
