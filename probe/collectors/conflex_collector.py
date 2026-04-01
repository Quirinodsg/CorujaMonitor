"""
Conflex HVAC/Ar-Condicionado Collector — Coruja Monitor
Coleta métricas via SNMP de automação Conflex (enterprise OID 42588).

OIDs Temperatura (.3.4.4.X.0) — valores ×10:
  0 = Temperatura Interna (sala)
  6 = Temperatura Retorno Máq 1
  7 = Temperatura Insuflamento Máq 1
  8 = Temperatura Retorno Máq 2
  9 = Temperatura Insuflamento Máq 2

OIDs Status (.3.1.1/2/3.X.0):
  0 = Alarme Temperatura Alta
  1 = Alarme Defeito Máquinas
  2 = Status PLC
  4 = Habilita Máquina 1
  5 = Habilita Máquina 2

OIDs Info (.3.2.1.X.0):
  0 = Sistema em Automático
  2 = Falha Rede Geral
  3 = Máquina em Automático Máq 1
  4 = Máquina em Automático Máq 2
"""
import logging
import time
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

ENT = "1.3.6.1.4.1.42588"

# Temperatura OIDs (valores ×10)
TEMP_OIDS = {
    f"{ENT}.3.4.4.0.0": {"name": "temp_interna", "label": "Temperatura Interna", "icon": "🌡️"},
    f"{ENT}.3.4.4.6.0": {"name": "temp_retorno_maq1", "label": "Retorno Máq 1", "icon": "❄️"},
    f"{ENT}.3.4.4.7.0": {"name": "temp_insuf_maq1", "label": "Insuflamento Máq 1", "icon": "💨"},
    f"{ENT}.3.4.4.8.0": {"name": "temp_retorno_maq2", "label": "Retorno Máq 2", "icon": "❄️"},
    f"{ENT}.3.4.4.9.0": {"name": "temp_insuf_maq2", "label": "Insuflamento Máq 2", "icon": "💨"},
}

# Status ON/OFF OIDs
STATUS_OIDS = {
    f"{ENT}.3.1.2.0.0": {"name": "alarme_temp_alta", "label": "Alarme Temp Alta", "alarm": True},
    f"{ENT}.3.1.2.1.0": {"name": "alarme_defeito", "label": "Alarme Defeito", "alarm": True},
    f"{ENT}.3.1.2.2.0": {"name": "status_plc", "label": "Status PLC", "alarm": False},
    f"{ENT}.3.1.2.4.0": {"name": "maquina_1", "label": "Máquina 1", "alarm": False},
    f"{ENT}.3.1.2.5.0": {"name": "maquina_2", "label": "Máquina 2", "alarm": False},
}

# Info OIDs (texto)
INFO_OIDS = {
    f"{ENT}.3.2.1.0.0": {"name": "sistema_auto", "label": "Sistema Automático"},
    f"{ENT}.3.2.1.2.0": {"name": "falha_rede", "label": "Falha Rede Geral"},
    f"{ENT}.3.2.1.3.0": {"name": "maq1_auto", "label": "Máq 1 Automático"},
    f"{ENT}.3.2.1.4.0": {"name": "maq2_auto", "label": "Máq 2 Automático"},
}


class ConflexCollector:
    def __init__(self, ip: str, community: str = "public", port: int = 161):
        self.ip = ip
        self.community = community
        self.port = port

    def collect(self) -> List[Dict[str, Any]]:
        metrics = []
        start = time.time()
        try:
            from collectors.snmp_collector import SNMPCollector
            collector = SNMPCollector()

            all_oids = list(TEMP_OIDS.keys()) + list(STATUS_OIDS.keys()) + list(INFO_OIDS.keys())
            result = collector.collect_snmp_v2c(self.ip, self.community, self.port, oids=all_oids)

            if not result or result.get('status') != 'success' or not result.get('data'):
                logger.warning(f"Conflex {self.ip}: SNMP failed")
                return [self._m("status", 0, "status", "critical")]

            data = result['data']
            elapsed = (time.time() - start) * 1000
            overall = "ok"

            # ── Temperaturas (valor ×10) ──
            for oid, info in TEMP_OIDS.items():
                val_str = self._find_oid(data, oid)
                if val_str:
                    num = self._parse_temp(val_str)
                    if num is not None:
                        temp = round(num / 10.0, 1)
                        st = "ok"
                        if info["name"] == "temp_interna":
                            if temp >= 30: st = "critical"; overall = "critical"
                            elif temp >= 26: st = "warning"; overall = max(overall, "warning", key=lambda x: ["ok","warning","critical"].index(x))
                        metrics.append(self._m(info["name"], temp, "°C", st, info["label"], info["icon"]))

            # ── Status ON/OFF ──
            for oid, info in STATUS_OIDS.items():
                val_str = self._find_oid(data, oid)
                if val_str:
                    is_on = val_str.strip('"').lower() in ("on", "1")
                    if info["alarm"]:
                        st = "critical" if is_on else "ok"
                        if is_on: overall = "critical"
                    else:
                        st = "ok" if is_on else "warning"
                        if not is_on and info["name"] in ("maquina_1", "maquina_2", "status_plc"):
                            overall = max(overall, "warning", key=lambda x: ["ok","warning","critical"].index(x))
                    metrics.append(self._m(info["name"], 1 if is_on else 0, "on/off", st, info["label"]))

            # ── Info (texto) ──
            for oid, info in INFO_OIDS.items():
                val_str = self._find_oid(data, oid)
                if val_str:
                    txt = val_str.strip('"')
                    has_falha = "falha" in txt.lower()
                    if has_falha: overall = "critical"
                    metrics.append(self._m(info["name"], 1 if not has_falha else 0, "text", "critical" if has_falha else "ok", txt))

            metrics.insert(0, self._m("status", 1 if overall != "critical" else 0, "status", overall))
            metrics.append(self._m("latency", round(elapsed, 1), "ms", "ok"))

            logger.info(f"Conflex {self.ip}: {len(metrics)} metrics, status={overall}, {elapsed:.0f}ms")
            return metrics

        except Exception as e:
            logger.warning(f"Conflex {self.ip} error: {e}")
            return [self._m("status", 0, "status", "critical")]

    def _find_oid(self, data, target_oid):
        """Find OID value in SNMP data (handles partial OID matching)."""
        for oid, val in data.items():
            # Match by last segments
            target_tail = target_oid.split("42588.")[-1]
            if target_tail in oid or oid.endswith(target_tail):
                return val
        return None

    def _parse_temp(self, val_str):
        """Extract numeric value from 'NNN - Description' format."""
        val = val_str.strip('"')
        match = re.match(r'(\d+)', val)
        return int(match.group(1)) if match else None

    def _m(self, name, value, unit, status, label=None, icon=None):
        return {
            "sensor_type": "conflex", "name": f"Conflex {name}",
            "value": value, "unit": unit, "status": status,
            "label": label or name, "icon": icon or "📊",
        }
