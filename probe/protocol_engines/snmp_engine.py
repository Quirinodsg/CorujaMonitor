"""
SNMP Engine - Suporte v1/v2c/v3 com GetBulk e fallback GetNext
"""
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from .base_engine import BaseProtocolEngine, EngineResult

logger = logging.getLogger(__name__)

# --- Importação pysnmp (suporta 7.x asyncio e 4.x legacy) ---
_PYSNMP_AVAILABLE = False
_PYSNMP_VERSION = 0
getCmd = bulkCmd = nextCmd = None
SnmpEngine = CommunityData = UdpTransportTarget = None
ContextData = ObjectType = ObjectIdentity = None

try:
    # pysnmp 7.x — API v3arch asyncio (snake_case)
    from pysnmp.hlapi.v3arch.asyncio import (
        get_cmd as getCmd, bulk_cmd as bulkCmd, next_cmd as nextCmd,
        SnmpEngine, CommunityData, UdpTransportTarget,
        ContextData, ObjectType, ObjectIdentity,
    )
    _PYSNMP_AVAILABLE = True
    _PYSNMP_VERSION = 7
except ImportError:
    try:
        # pysnmp 4.x legacy
        from pysnmp.hlapi import (
            getCmd, bulkCmd, nextCmd,
            SnmpEngine, CommunityData, UdpTransportTarget,
            ContextData, ObjectType, ObjectIdentity,
        )
        _PYSNMP_AVAILABLE = True
        _PYSNMP_VERSION = 4
    except ImportError:
        pass

# OIDs padrão
OID_SYSUPTIME   = "1.3.6.1.2.1.1.3.0"
OID_SYSDESCR    = "1.3.6.1.2.1.1.1.0"
OID_IFTABLE     = "1.3.6.1.2.1.2.2"       # ifTable
OID_CPU_IDLE    = "1.3.6.1.4.1.2021.11.11.0"
OID_MEM_TOTAL   = "1.3.6.1.4.1.2021.4.5.0"
OID_MEM_AVAIL   = "1.3.6.1.4.1.2021.4.6.0"
OID_DSK_PERCENT = "1.3.6.1.4.1.2021.9.1.9"

BULK_MAX_REPETITIONS = 25


class SNMPEngine(BaseProtocolEngine):
    """
    Engine SNMP com suporte a v1/v2c/v3, GetBulk e fallback GetNext.

    kwargs esperados em execute():
        community (str): community string (padrão: "public")
        port (int): porta UDP (padrão: 161)
        version (str): "1" | "2c" | "3" (padrão: "2c")
        timeout (int): timeout em segundos (padrão: 5)
        retries (int): tentativas (padrão: 2)
        oids (list): lista de OIDs para GET simples
        # SNMPv3
        username (str): usuário v3
        auth_key (str): chave de autenticação
        priv_key (str): chave de privacidade
        auth_protocol (str): "SHA" | "MD5"
        priv_protocol (str): "AES" | "DES"
    """

    def is_available(self) -> bool:
        return _PYSNMP_AVAILABLE

    def execute(self, host: str, **kwargs) -> EngineResult:
        if not _PYSNMP_AVAILABLE:
            return self._unavailable_result()

        oids: List[str] = kwargs.get("oids", [OID_SYSUPTIME, OID_SYSDESCR])
        version: str = str(kwargs.get("version", "2c"))
        community: str = kwargs.get("community", "public")
        port: int = int(kwargs.get("port", 161))
        timeout: int = int(kwargs.get("timeout", 5))
        retries: int = int(kwargs.get("retries", 2))

        start = time.monotonic()
        try:
            auth = self._build_auth(version, community, kwargs)
            transport = UdpTransportTarget((host, port), timeout=timeout, retries=retries)
            results = self._get(auth, transport, oids)
            latency_ms = (time.monotonic() - start) * 1000

            if not results:
                return EngineResult(
                    status="unknown",
                    error="no_response",
                    metadata={"host": host, "version": version},
                )

            return EngineResult(
                status="ok",
                value=round(latency_ms, 2),
                unit="ms",
                metadata={
                    "host": host,
                    "version": version,
                    "latency_ms": round(latency_ms, 2),
                    "oids_collected": len(results),
                    "data": results,
                },
            )
        except Exception as e:
            logger.warning(f"SNMPEngine error for {host}: {e}")
            return EngineResult(
                status="unknown",
                error=str(e),
                metadata={"host": host},
            )

    # ------------------------------------------------------------------
    # Bulk / Walk
    # ------------------------------------------------------------------

    def collect_bulk(self, host: str, oid: str, community: str = "public",
                     port: int = 161, version: str = "2c",
                     timeout: int = 5, retries: int = 2) -> List[Dict[str, str]]:
        """GetBulk com max-repetitions=25. Fallback para GetNext se v1."""
        if not _PYSNMP_AVAILABLE:
            return []
        try:
            auth = self._build_auth(version, community, {})
            transport = UdpTransportTarget((host, port), timeout=timeout, retries=retries)
            if version == "1":
                return self._walk_getnext(auth, transport, oid)
            return self._walk_bulk(auth, transport, oid)
        except Exception as e:
            logger.warning(f"SNMPEngine collect_bulk error for {host}/{oid}: {e}")
            return []

    def collect_interface_table(self, host: str, community: str = "public",
                                port: int = 161, version: str = "2c") -> List[Dict]:
        """Walk na ifTable (OID 1.3.6.1.2.1.2.2) via GetBulk."""
        rows = self.collect_bulk(host, OID_IFTABLE, community, port, version)
        return rows

    def collect_cpu(self, host: str, community: str = "public",
                    port: int = 161, version: str = "2c") -> Optional[float]:
        """Retorna % CPU (100 - idle). None se não disponível."""
        if not _PYSNMP_AVAILABLE:
            return None
        try:
            auth = self._build_auth(version, community, {})
            transport = UdpTransportTarget((host, port), timeout=5, retries=2)
            results = self._get(auth, transport, [OID_CPU_IDLE])
            idle_str = results.get(OID_CPU_IDLE)
            if idle_str is not None:
                return round(100.0 - float(idle_str), 2)
        except Exception as e:
            logger.debug(f"SNMPEngine collect_cpu error: {e}")
        return None

    def collect_memory(self, host: str, community: str = "public",
                       port: int = 161, version: str = "2c") -> Optional[Dict]:
        """Retorna dict com total_kb, available_kb, used_pct."""
        if not _PYSNMP_AVAILABLE:
            return None
        try:
            auth = self._build_auth(version, community, {})
            transport = UdpTransportTarget((host, port), timeout=5, retries=2)
            results = self._get(auth, transport, [OID_MEM_TOTAL, OID_MEM_AVAIL])
            total = results.get(OID_MEM_TOTAL)
            avail = results.get(OID_MEM_AVAIL)
            if total and avail:
                total_kb = int(total)
                avail_kb = int(avail)
                used_pct = round((1 - avail_kb / max(total_kb, 1)) * 100, 2)
                return {"total_kb": total_kb, "available_kb": avail_kb, "used_pct": used_pct}
        except Exception as e:
            logger.debug(f"SNMPEngine collect_memory error: {e}")
        return None

    def collect_disk(self, host: str, community: str = "public",
                     port: int = 161, version: str = "2c") -> List[Dict]:
        """Retorna lista de discos com uso %."""
        rows = self.collect_bulk(host, OID_DSK_PERCENT, community, port, version)
        disks = []
        for row in rows:
            try:
                disks.append({"oid": row["oid"], "used_pct": float(row["value"])})
            except (ValueError, KeyError):
                pass
        return disks

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_auth(self, version: str, community: str, kwargs: dict):
        """Constrói objeto de autenticação SNMP"""
        if version == "3":
            from pysnmp.hlapi import UsmUserData
            try:
                from pysnmp.hlapi import (
                    usmHMACSHAAuthProtocol, usmHMACMD5AuthProtocol,
                    usmAesCfb128Protocol, usmDESPrivProtocol,
                )
            except ImportError:
                from pysnmp.hlapi.v1arch.asyncio.sync import (
                    usmHMACSHAAuthProtocol, usmHMACMD5AuthProtocol,
                    usmAesCfb128Protocol, usmDESPrivProtocol,
                )
            auth_proto = (usmHMACSHAAuthProtocol
                          if kwargs.get("auth_protocol", "SHA").upper() == "SHA"
                          else usmHMACMD5AuthProtocol)
            priv_proto = (usmAesCfb128Protocol
                          if kwargs.get("priv_protocol", "AES").upper() == "AES"
                          else usmDESPrivProtocol)
            return UsmUserData(
                kwargs.get("username", ""),
                authKey=kwargs.get("auth_key", ""),
                privKey=kwargs.get("priv_key", ""),
                authProtocol=auth_proto,
                privProtocol=priv_proto,
            )
        mp_model = 0 if version == "1" else 1
        return CommunityData(community, mpModel=mp_model)

    def _get(self, auth, transport, oids: List[str]) -> Dict[str, str]:
        """Executa SNMP GET para lista de OIDs. Retorna {oid: value}."""
        results = {}
        for oid in oids:
            try:
                iterator = getCmd(
                    SnmpEngine(), auth, transport, ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
                err_ind, err_status, _, var_binds = next(iterator)
                if not err_ind and not err_status:
                    for vb in var_binds:
                        results[oid] = str(vb[1])
            except Exception as e:
                logger.debug(f"SNMP GET error for OID {oid}: {e}")
        return results

    def _walk_bulk(self, auth, transport, oid: str) -> List[Dict[str, str]]:
        """GetBulk walk. Fallback para GetNext se falhar."""
        results = []
        try:
            for err_ind, err_status, _, var_binds in bulkCmd(
                SnmpEngine(), auth, transport, ContextData(),
                0, BULK_MAX_REPETITIONS,
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
            ):
                if err_ind or err_status:
                    break
                for vb in var_binds:
                    results.append({"oid": str(vb[0]), "value": str(vb[1])})
        except Exception as e:
            logger.debug(f"GetBulk failed, falling back to GetNext: {e}")
            return self._walk_getnext(auth, transport, oid)
        return results

    def _walk_getnext(self, auth, transport, oid: str) -> List[Dict[str, str]]:
        """GetNext walk (fallback para v1 ou quando GetBulk falha)."""
        results = []
        try:
            for err_ind, err_status, _, var_binds in nextCmd(
                SnmpEngine(), auth, transport, ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False,
            ):
                if err_ind or err_status:
                    break
                for vb in var_binds:
                    results.append({"oid": str(vb[0]), "value": str(vb[1])})
        except Exception as e:
            logger.debug(f"GetNext walk error: {e}")
        return results
