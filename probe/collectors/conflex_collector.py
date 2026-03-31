"""
Conflex HVAC/Ar-Condicionado Collector — Coruja Monitor
Coleta métricas via SNMP de automação Conflex (enterprise OID 42588).

OIDs:
  .1.3.6.1.4.1.42588.3.1.1.X.0 = Nome da função
  .1.3.6.1.4.1.42588.3.1.2.X.0 = Status (on/off)
  .1.3.6.1.4.1.42588.3.1.3.X.0 = Valor numérico (0/1)
  .1.3.6.1.4.1.42588.3.1.4.X.0 = Status combinado
"""
import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

BASE_OID = "1.3.6.1.4.1.42588.3.1"

# Mapeamento dos índices conhecidos
CONFLEX_ITEMS = {
    0: {"name": "alarme_temp_alta", "label": "Alarme Temperatura Alta", "icon": "🌡️", "alarm": True},
    1: {"name": "alarme_defeito", "label": "Alarme Defeito Máquinas", "icon": "⚠️", "alarm": True},
    2: {"name": "status_plc", "label": "Status PLC", "icon": "🔌", "alarm": False},
    4: {"name": "maquina_1", "label": "Máquina 1", "icon": "❄️", "alarm": False},
    5: {"name": "maquina_2", "label": "Máquina 2", "icon": "❄️", "alarm": False},
}


class ConflexCollector:
    def __init__(self, ip: str, community: str = "public", port: int = 161):
        self.ip = ip
        self.community = community
        self.port = port

    def collect(self) -> List[Dict[str, Any]]:
        """Coleta todas as métricas do Conflex via SNMP."""
        metrics = []
        start = time.time()

        try:
            from collectors.snmp_collector import SNMPCollector
            collector = SNMPCollector()

            # Coletar status de cada item
            oids_status = [f"{BASE_OID}.2.{i}.0" for i in range(12)]
            oids_names = [f"{BASE_OID}.1.{i}.0" for i in range(12)]
            all_oids = oids_status + oids_names

            result = collector.collect_snmp_v2c(self.ip, self.community, self.port, oids=all_oids)

            if not result or result.get('status') != 'success' or not result.get('data'):
                logger.warning(f"Conflex {self.ip}: SNMP failed")
                return [self._metric("status", 0, "status", "critical")]

            data = result['data']
            elapsed = (time.time() - start) * 1000

            # Parse nomes e status
            names = {}
            statuses = {}
            for oid, val in data.items():
                oid_parts = oid.split('.')
                if len(oid_parts) < 2:
                    continue
                idx_str = oid_parts[-2]  # penúltimo = índice
                try:
                    idx = int(idx_str)
                except ValueError:
                    continue

                # Detectar se é nome (.1.X.0) ou status (.2.X.0)
                if f".1.{idx}.0" in oid:
                    names[idx] = val.strip('"')
                elif f".2.{idx}.0" in oid:
                    statuses[idx] = val.strip('"').lower()

            # Gerar métricas para itens conhecidos
            overall_status = "ok"
            for idx, item in CONFLEX_ITEMS.items():
                st = statuses.get(idx, "unknown")
                is_on = st == "on" or st == '"on"'
                name_label = names.get(idx, item["label"])

                if item["alarm"]:
                    # Alarmes: on = problema, off = ok
                    sensor_status = "critical" if is_on else "ok"
                    if is_on:
                        overall_status = "critical"
                else:
                    # Funções: on = ok, off = problema
                    sensor_status = "ok" if is_on else "warning"
                    if not is_on and item["name"] in ("status_plc", "maquina_1", "maquina_2"):
                        if overall_status != "critical":
                            overall_status = "warning"

                metrics.append(self._metric(
                    item["name"],
                    1 if is_on else 0,
                    "on/off",
                    sensor_status,
                    label=name_label,
                    icon=item["icon"]
                ))

            # Coletar todos os outros itens (3-11) que não são "Sem Funcao"
            for idx in range(12):
                if idx in CONFLEX_ITEMS:
                    continue
                name = names.get(idx, "")
                if not name or "sem funcao" in name.lower():
                    continue
                st = statuses.get(idx, "off")
                is_on = st == "on"
                metrics.append(self._metric(
                    f"funcao_{idx}",
                    1 if is_on else 0,
                    "on/off",
                    "ok" if is_on else "warning",
                    label=name,
                    icon="📊"
                ))

            # Métrica geral
            metrics.insert(0, self._metric("status", 1, "status", overall_status))
            metrics.append(self._metric("latency", round(elapsed, 1), "ms", "ok"))

            logger.info(f"Conflex {self.ip}: {len(metrics)} metrics, status={overall_status}, {elapsed:.0f}ms")
            return metrics

        except Exception as e:
            logger.warning(f"Conflex {self.ip} error: {e}")
            return [self._metric("status", 0, "status", "critical")]

    def _metric(self, name, value, unit, status, label=None, icon=None):
        return {
            "sensor_type": "conflex",
            "sensor_name": f"Conflex {name}",
            "name": f"Conflex {name}",
            "value": value,
            "unit": unit,
            "status": status,
            "label": label or name,
            "icon": icon or "📊",
        }
