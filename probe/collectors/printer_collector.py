"""
Printer SNMP Collector — Coruja Monitor
Coleta métricas de impressoras via SNMP (Printer MIB padrão).
Compatível com Samsung, HP, Canon, Epson, Brother, etc.

OIDs:
  .1.3.6.1.2.1.43.11.1.1.9.1.1  = Nível toner atual
  .1.3.6.1.2.1.43.11.1.1.8.1.1  = Capacidade máxima toner
  .1.3.6.1.2.1.43.10.2.1.4.1.1  = Total páginas impressas
  .1.3.6.1.2.1.25.3.5.1.1.1     = Status impressora
  .1.3.6.1.2.1.25.3.2.1.3.1     = Modelo
  .1.3.6.1.2.1.1.3.0             = Uptime
"""
import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

PRINTER_OIDS = {
    "1.3.6.1.2.1.43.11.1.1.9.1.1": "toner_level",
    "1.3.6.1.2.1.43.11.1.1.8.1.1": "toner_max",
    "1.3.6.1.2.1.43.10.2.1.4.1.1": "total_pages",
    "1.3.6.1.2.1.25.3.5.1.1.1": "printer_status",
    "1.3.6.1.2.1.25.3.2.1.3.1": "model",
    "1.3.6.1.2.1.1.3.0": "uptime",
}

STATUS_MAP = {1: "other", 2: "unknown", 3: "idle", 4: "printing", 5: "warmup"}


class PrinterCollector:
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
            result = collector.collect_snmp_v2c(self.ip, self.community, self.port, oids=list(PRINTER_OIDS.keys()))

            if not result or result.get('status') != 'success' or not result.get('data'):
                return [self._m("status", 0, "status", "critical")]

            data = result['data']
            elapsed = (time.time() - start) * 1000
            vals = {}
            for oid, name in PRINTER_OIDS.items():
                for k, v in data.items():
                    if oid in k or k.endswith(oid.split('.')[-1]):
                        vals[name] = v
                        break

            toner_level = self._int(vals.get("toner_level"))
            toner_max = self._int(vals.get("toner_max"))
            total_pages = self._int(vals.get("total_pages"))
            printer_status = self._int(vals.get("printer_status"))
            model = str(vals.get("model", "")).strip('"')

            toner_pct = round(toner_level / toner_max * 100) if toner_max and toner_max > 0 else 0
            toner_st = "critical" if toner_pct <= 10 else "warning" if toner_pct <= 20 else "ok"
            overall = toner_st

            metrics.append(self._m("toner", toner_pct, "%", toner_st, f"Toner: {toner_pct}%"))
            metrics.append(self._m("toner_level", toner_level or 0, "units", "ok"))
            metrics.append(self._m("toner_max", toner_max or 0, "units", "ok"))
            metrics.append(self._m("total_pages", total_pages or 0, "pages", "ok"))
            metrics.append(self._m("printer_status", printer_status or 0, "status", "ok", STATUS_MAP.get(printer_status, "unknown")))
            if model:
                metrics.append(self._m("model", 0, "text", "ok", model))
            metrics.append(self._m("latency", round(elapsed, 1), "ms", "ok"))
            metrics.insert(0, self._m("status", 1, "status", overall))

            logger.info(f"Printer {self.ip}: toner={toner_pct}%, pages={total_pages}, {elapsed:.0f}ms")
            return metrics
        except Exception as e:
            logger.warning(f"Printer {self.ip} error: {e}")
            return [self._m("status", 0, "status", "critical")]

    def _int(self, v):
        try: return int(str(v).strip('"'))
        except: return None

    def _m(self, name, value, unit, status, label=None):
        return {"sensor_type": "printer", "name": f"Printer {name}", "value": value, "unit": unit, "status": status, "label": label or name}
