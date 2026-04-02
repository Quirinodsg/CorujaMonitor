"""
Dell EqualLogic Storage Collector — Coruja Monitor
Coleta métricas via SNMP das MIBs proprietárias EqualLogic (enterprise 12740).

Métricas coletadas:
- Capacidade total / usada / livre (MB → GB)
- Espaço de snapshots e réplicas
- Uso percentual
- Modelo, serial, firmware
- Status dos discos físicos
- Interfaces de rede (iSCSI)
- Conexões iSCSI ativas
- Uptime
"""
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from pysnmp.hlapi import (
        SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
        ObjectType, ObjectIdentity, getCmd, nextCmd, bulkCmd
    )
    PYSNMP_OK = True
except ImportError:
    PYSNMP_OK = False

# ── EqualLogic Enterprise OIDs (1.3.6.1.4.1.12740) ──
EQL_BASE = "1.3.6.1.4.1.12740"

# Member MIB (eqlMemberTable = 12740.2.1)
MEMBER_TABLE = f"{EQL_BASE}.2.1"
OID_MEMBER_NAME         = f"{MEMBER_TABLE}.1.9"    # eqlMemberName
OID_MEMBER_MODEL        = f"{MEMBER_TABLE}.1.6"    # eqlMemberModel
OID_MEMBER_SERIAL       = f"{MEMBER_TABLE}.1.8"    # eqlMemberSerialNumber
OID_MEMBER_SVC_TAG      = f"{MEMBER_TABLE}.1.7"    # eqlMemberServiceTag
OID_MEMBER_TOTAL_STOR   = f"{MEMBER_TABLE}.1.10"   # eqlMemberTotalStorage (MB)
OID_MEMBER_USED_STOR    = f"{MEMBER_TABLE}.1.11"   # eqlMemberUsedStorage (MB)
OID_MEMBER_SNAP_STOR    = f"{MEMBER_TABLE}.1.12"   # eqlMemberSnapStorage (MB)
OID_MEMBER_REPL_STOR    = f"{MEMBER_TABLE}.1.13"   # eqlMemberReplStorage (MB)
OID_MEMBER_STATUS       = f"{MEMBER_TABLE}.1.14"   # eqlMemberStatus
OID_MEMBER_HEALTH       = f"{MEMBER_TABLE}.1.5"    # eqlMemberHealthStatus
OID_MEMBER_RAID_STATUS  = f"{MEMBER_TABLE}.1.28"   # eqlMemberRaidStatus
OID_MEMBER_CONN_COUNT   = f"{MEMBER_TABLE}.1.31"   # eqlMemberNumberOfConnections
OID_MEMBER_FW_VER       = f"{MEMBER_TABLE}.1.15"   # eqlMemberControllerMajorVersion

# Disk MIB (eqlDiskTable = 12740.3.1)
DISK_TABLE = f"{EQL_BASE}.3.1"
OID_DISK_STATUS         = f"{DISK_TABLE}.1.8"      # eqlDiskStatus
OID_DISK_SLOT           = f"{DISK_TABLE}.1.4"      # eqlDiskSlot
OID_DISK_MODEL          = f"{DISK_TABLE}.1.6"      # eqlDiskModelNumber
OID_DISK_SERIAL         = f"{DISK_TABLE}.1.5"      # eqlDiskSerialNumber
OID_DISK_SIZE           = f"{DISK_TABLE}.1.7"      # eqlDiskSize (MB)
OID_DISK_ERRORS         = f"{DISK_TABLE}.1.9"      # eqlDiskErrors
OID_DISK_SMART          = f"{DISK_TABLE}.1.12"     # eqlDiskSmartInfoStatus

# Volume MIB (eqliscsiVolumeTable = 12740.5.1.7)
VOL_TABLE = f"{EQL_BASE}.5.1.7"
OID_VOL_NAME            = f"{VOL_TABLE}.1.2"       # eqliscsiVolumeName
OID_VOL_SIZE            = f"{VOL_TABLE}.1.3"       # eqliscsiVolumeSize (MB)
OID_VOL_STATUS          = f"{VOL_TABLE}.1.8"       # eqliscsiVolumeAdminStatus

# Standard MIBs
OID_SYS_DESCR   = "1.3.6.1.2.1.1.1.0"
OID_SYS_NAME    = "1.3.6.1.2.1.1.5.0"
OID_SYS_UPTIME  = "1.3.6.1.2.1.1.3.0"
OID_SYS_CONTACT = "1.3.6.1.2.1.1.4.0"

# IF-MIB para interfaces de rede
OID_IF_DESCR    = "1.3.6.1.2.1.2.2.1.2"
OID_IF_SPEED    = "1.3.6.1.2.1.31.1.1.1.15"  # ifHighSpeed (Mbps)
OID_IF_STATUS   = "1.3.6.1.2.1.2.2.1.8"      # ifOperStatus
OID_IF_IN_OCT   = "1.3.6.1.2.1.31.1.1.1.6"   # ifHCInOctets
OID_IF_OUT_OCT  = "1.3.6.1.2.1.31.1.1.1.10"  # ifHCOutOctets
OID_IF_IN_ERR   = "1.3.6.1.2.1.2.2.1.14"     # ifInErrors
OID_IF_OUT_ERR  = "1.3.6.1.2.1.2.2.1.20"     # ifOutErrors

# TCP connections (iSCSI)
OID_TCP_CURR_ESTAB = "1.3.6.1.2.1.6.9.0"     # tcpCurrEstab


class EqualLogicCollector:
    """Coleta métricas de Dell EqualLogic via SNMP v2c."""

    def __init__(self, ip: str, community: str = "public", port: int = 161):
        self.ip = ip
        self.community = community
        self.port = port

    def collect(self) -> List[Dict[str, Any]]:
        """Coleta todas as métricas do storage. Retorna lista de métricas."""
        if not PYSNMP_OK:
            logger.error("pysnmp não disponível para EqualLogic collector")
            return [self._metric("status", 0, "status", "critical")]

        start = time.time()
        metrics = []

        try:
            # 1. Info básica (GET)
            basic = self._snmp_get_multi([
                OID_SYS_DESCR, OID_SYS_NAME, OID_SYS_UPTIME, OID_TCP_CURR_ESTAB
            ])
            elapsed = (time.time() - start) * 1000

            uptime_ticks = self._to_int(basic.get(OID_SYS_UPTIME, "0"))
            uptime_days = round(uptime_ticks / 8640000, 1) if uptime_ticks else 0
            metrics.append(self._metric("uptime", uptime_days, "dias", "ok"))

            tcp_conn = self._to_int(basic.get(OID_TCP_CURR_ESTAB, "0"))
            metrics.append(self._metric("iscsi_connections", tcp_conn, "conn", "ok"))

            # 2. Member storage (WALK)
            member_data = self._snmp_walk(MEMBER_TABLE)
            storage_metrics = self._parse_member_storage(member_data)
            metrics.extend(storage_metrics)

            # 3. Discos físicos (WALK)
            disk_data = self._snmp_walk(DISK_TABLE)
            disk_metrics = self._parse_disks(disk_data)
            metrics.extend(disk_metrics)

            # 4. Volumes (WALK)
            vol_data = self._snmp_walk(VOL_TABLE)
            vol_metrics = self._parse_volumes(vol_data)
            metrics.extend(vol_metrics)

            # 5. Interfaces de rede
            net_metrics = self._parse_interfaces()
            metrics.extend(net_metrics)

            # Latência SNMP
            metrics.append(self._metric("latency", round(elapsed, 1), "ms", "ok"))

            # Status geral: ok se conseguiu coletar métricas básicas (uptime, interfaces)
            has_data = len(metrics) > 2  # mais que só uptime e connections
            has_storage = any(m["name"].startswith("EqualLogic storage") for m in metrics)
            has_critical = any(m["status"] == "critical" and m["name"] != "EqualLogic status" for m in metrics)

            if has_critical:
                overall = "critical"
            elif has_storage:
                overall = "ok"
            elif has_data:
                overall = "ok"  # Sem MIBs proprietárias mas SNMP respondeu
            else:
                overall = "warning"

            metrics.append(self._metric("status", 1 if overall == "ok" else 0, "status", overall))

            logger.info(f"EqualLogic {self.ip}: {len(metrics)} metrics, {elapsed:.0f}ms")

        except Exception as e:
            logger.error(f"EqualLogic {self.ip} error: {e}", exc_info=True)
            metrics.append(self._metric("status", 0, "status", "critical"))

        return metrics

    def _parse_member_storage(self, data: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse member storage OIDs into metrics."""
        metrics = []
        # Extrair valores por suffix (member index)
        total_mb = used_mb = snap_mb = repl_mb = 0
        model = serial = svc_tag = fw_ver = ""
        health = conn_count = 0

        for oid, val in data.items():
            tail = oid.split(".")[-1] if "." in oid else ""
            if f".{MEMBER_TABLE.split('.')[-1]}.1.10." in oid or oid.startswith(OID_MEMBER_TOTAL_STOR):
                total_mb = max(total_mb, self._to_int(val))
            elif f".{MEMBER_TABLE.split('.')[-1]}.1.11." in oid or oid.startswith(OID_MEMBER_USED_STOR):
                used_mb = max(used_mb, self._to_int(val))
            elif f".{MEMBER_TABLE.split('.')[-1]}.1.12." in oid or oid.startswith(OID_MEMBER_SNAP_STOR):
                snap_mb += self._to_int(val)
            elif f".{MEMBER_TABLE.split('.')[-1]}.1.13." in oid or oid.startswith(OID_MEMBER_REPL_STOR):
                repl_mb += self._to_int(val)
            elif oid.startswith(OID_MEMBER_MODEL):
                model = val
            elif oid.startswith(OID_MEMBER_SERIAL):
                serial = val
            elif oid.startswith(OID_MEMBER_SVC_TAG):
                svc_tag = val
            elif oid.startswith(OID_MEMBER_HEALTH):
                health = self._to_int(val)
            elif oid.startswith(OID_MEMBER_CONN_COUNT):
                conn_count = self._to_int(val)

        if total_mb > 0:
            total_gb = round(total_mb / 1024, 2)
            used_gb = round(used_mb / 1024, 2)
            free_gb = round((total_mb - used_mb) / 1024, 2)
            snap_gb = round(snap_mb / 1024, 2)
            repl_gb = round(repl_mb / 1024, 2)
            pct_used = round((used_mb / total_mb) * 100, 1) if total_mb > 0 else 0

            status = "critical" if pct_used > 97 else "warning" if pct_used > 90 else "ok"

            metrics.append(self._metric("storage_total", total_gb, "GB", "ok"))
            metrics.append(self._metric("storage_used", used_gb, "GB", status))
            metrics.append(self._metric("storage_free", free_gb, "GB", status))
            metrics.append(self._metric("storage_percent", pct_used, "%", status))
            metrics.append(self._metric("storage_snapshots", snap_gb, "GB", "ok"))
            metrics.append(self._metric("storage_replicas", repl_gb, "GB", "ok"))

        if model:
            metrics.append(self._metric("model", 0, model, "ok"))
        if serial:
            metrics.append(self._metric("serial", 0, serial, "ok"))
        if health:
            # 1=normal, 2=warning, 3=critical
            h_status = "ok" if health == 1 else "warning" if health == 2 else "critical"
            metrics.append(self._metric("health", health, "status", h_status))
        if conn_count:
            metrics.append(self._metric("connections", conn_count, "conn", "ok"))

        return metrics

    def _parse_disks(self, data: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse disk OIDs into metrics."""
        metrics = []
        # Agrupar por disk index
        disks = {}
        for oid, val in data.items():
            parts = oid.split(".")
            if len(parts) < 2:
                continue
            # O index do disco é o último componente
            disk_idx = parts[-1]
            if oid.startswith(OID_DISK_STATUS):
                disks.setdefault(disk_idx, {})["status"] = self._to_int(val)
            elif oid.startswith(OID_DISK_SLOT):
                disks.setdefault(disk_idx, {})["slot"] = self._to_int(val)
            elif oid.startswith(OID_DISK_SIZE):
                disks.setdefault(disk_idx, {})["size_mb"] = self._to_int(val)
            elif oid.startswith(OID_DISK_ERRORS):
                disks.setdefault(disk_idx, {})["errors"] = self._to_int(val)

        total_disks = len(disks)
        online_disks = sum(1 for d in disks.values() if d.get("status") == 1)
        failed_disks = sum(1 for d in disks.values() if d.get("status", 0) not in (0, 1))
        total_errors = sum(d.get("errors", 0) for d in disks.values())
        total_size_gb = round(sum(d.get("size_mb", 0) for d in disks.values()) / 1024, 1)

        if total_disks > 0:
            metrics.append(self._metric("disks_total", total_disks, "discos", "ok"))
            metrics.append(self._metric("disks_online", online_disks, "discos",
                                        "ok" if online_disks == total_disks else "warning"))
            if failed_disks > 0:
                metrics.append(self._metric("disks_failed", failed_disks, "discos", "critical"))
            metrics.append(self._metric("disks_raw_capacity", total_size_gb, "GB", "ok"))
            if total_errors > 0:
                metrics.append(self._metric("disk_errors", total_errors, "erros",
                                            "warning" if total_errors < 10 else "critical"))

        return metrics

    def _parse_volumes(self, data: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse volume OIDs into metrics."""
        metrics = []
        volumes = {}
        for oid, val in data.items():
            parts = oid.split(".")
            if len(parts) < 2:
                continue
            vol_idx = parts[-1]
            if oid.startswith(OID_VOL_NAME):
                volumes.setdefault(vol_idx, {})["name"] = val
            elif oid.startswith(OID_VOL_SIZE):
                volumes.setdefault(vol_idx, {})["size_mb"] = self._to_int(val)

        total_vols = len(volumes)
        total_vol_gb = round(sum(v.get("size_mb", 0) for v in volumes.values()) / 1024, 1)

        if total_vols > 0:
            metrics.append(self._metric("volumes_count", total_vols, "volumes", "ok"))
            metrics.append(self._metric("volumes_total_size", total_vol_gb, "GB", "ok"))

        return metrics

    def _parse_interfaces(self) -> List[Dict[str, Any]]:
        """Parse interface metrics."""
        metrics = []
        try:
            if_data = self._snmp_walk("1.3.6.1.2.1.2.2.1")
            ifaces = {}
            for oid, val in if_data.items():
                parts = oid.split(".")
                if_idx = parts[-1]
                col = ".".join(parts[:-1])
                if col.endswith(".2"):  # ifDescr
                    ifaces.setdefault(if_idx, {})["name"] = val
                elif col.endswith(".8"):  # ifOperStatus
                    ifaces.setdefault(if_idx, {})["status"] = self._to_int(val)
                elif col.endswith(".14"):  # ifInErrors
                    ifaces.setdefault(if_idx, {})["in_errors"] = self._to_int(val)
                elif col.endswith(".20"):  # ifOutErrors
                    ifaces.setdefault(if_idx, {})["out_errors"] = self._to_int(val)

            for idx, iface in ifaces.items():
                name = iface.get("name", f"if{idx}")
                status = iface.get("status", 0)
                in_err = iface.get("in_errors", 0)
                out_err = iface.get("out_errors", 0)
                if status == 1:  # up
                    s = "ok"
                elif status == 2:  # down
                    s = "warning"  # Interface down pode ser normal (não usada)
                else:
                    s = "warning"
                metrics.append(self._metric(f"iface_{name}_status", status, "status", s))
                if in_err + out_err > 0:
                    metrics.append(self._metric(f"iface_{name}_errors",
                                                in_err + out_err, "erros",
                                                "warning" if in_err + out_err < 1000 else "critical"))
        except Exception as e:
            logger.debug(f"EqualLogic interfaces error: {e}")
        return metrics

    # ── SNMP helpers ──

    def _snmp_get_multi(self, oids: List[str]) -> Dict[str, str]:
        """SNMP GET para múltiplos OIDs."""
        results = {}
        for oid in oids:
            try:
                it = getCmd(
                    SnmpEngine(),
                    CommunityData(self.community, mpModel=1),
                    UdpTransportTarget((self.ip, self.port), timeout=5, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
                err_ind, err_st, err_idx, var_binds = next(it)
                if not err_ind and not err_st:
                    for vb in var_binds:
                        results[str(vb[0])] = str(vb[1])
            except Exception as e:
                logger.debug(f"SNMP GET {oid} error: {e}")
        return results

    def _snmp_walk(self, base_oid: str) -> Dict[str, str]:
        """SNMP WALK (GETNEXT) de uma sub-árvore."""
        results = {}
        try:
            for err_ind, err_st, err_idx, var_binds in nextCmd(
                SnmpEngine(),
                CommunityData(self.community, mpModel=1),
                UdpTransportTarget((self.ip, self.port), timeout=8, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(base_oid)),
                lexicographicMode=False
            ):
                if err_ind or err_st:
                    break
                for vb in var_binds:
                    oid_str = str(vb[0])
                    if not oid_str.startswith(base_oid):
                        return results
                    results[oid_str] = str(vb[1])
        except Exception as e:
            logger.debug(f"SNMP WALK {base_oid} error: {e}")
        return results

    def _to_int(self, val) -> int:
        try:
            return int(str(val).strip())
        except (ValueError, TypeError):
            return 0

    def _metric(self, name: str, value, unit: str, status: str) -> Dict[str, Any]:
        return {
            "sensor_type": "equallogic",
            "sensor_name": f"EqualLogic {name}",
            "name": f"EqualLogic {name}",
            "value": value,
            "unit": unit,
            "status": status,
        }
