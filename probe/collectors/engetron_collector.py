"""
Engetron UPS/Nobreak Collector — Coruja Monitor
Coleta métricas via HTTP scraping da interface WBRC (Web Based Remote Control).
Equivalente ao template Zabbix "Nobreak Engetron SNMP v1" mas via HTTP.

Métricas coletadas:
- Tensão entrada/saída (Fase A/B/C)
- Corrente entrada/saída
- Carga utilizada (%)
- Bateria: tensão, autonomia, corrente carga/descarga
- Temperatura interna
- Status (ligado/desligado)
- Potência ativa/aparente
"""
import re
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EngetronCollector:
    """Coleta métricas de Nobreak Engetron via HTTP (WBRC)."""

    def __init__(self, ip: str, password: str = "Eng3tr0n"):
        self.ip = ip
        self.password = password
        self.base_url = f"http://{ip}"

    def collect(self) -> List[Dict[str, Any]]:
        """Coleta todas as métricas do nobreak. Retorna lista de métricas."""
        import httpx
        start = time.time()
        try:
            # Login (seta sessão por IP no nobreak)
            httpx.post(f"{self.base_url}/passwd.htm",
                       data={"password": self.password}, timeout=10, verify=False)
            # Buscar página de supervisão
            r = httpx.get(f"{self.base_url}/virtua3.htm", timeout=10, verify=False)
            if r.status_code != 200:
                logger.warning(f"Engetron {self.ip}: HTTP {r.status_code}")
                return self._offline_metrics()

            elapsed = (time.time() - start) * 1000
            html = r.text
            metrics = self._parse_html(html)
            metrics.append(self._metric("latency", round(elapsed, 1), "ms", "ok"))
            logger.info(f"Engetron {self.ip}: {len(metrics)} metrics, {elapsed:.0f}ms")
            return metrics

        except Exception as e:
            logger.warning(f"Engetron {self.ip} error: {e}")
            return self._offline_metrics()

    def _parse_html(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML da página virtua3.htm e extrai métricas."""
        m = []
        val = lambda pattern, text: self._extract_value(pattern, text)

        # Informações gerais
        temp = val(r"Temperatura interna</td>\s*<td class=tdv>\s*(\d+)", html)
        if temp is not None:
            status = "critical" if temp > 38 else "warning" if temp > 35 else "ok"
            m.append(self._metric("temperatura", temp, "°C", status))

        status_txt = "ok" if "LIGADO" in html else "critical"
        m.append(self._metric("status", 1 if status_txt == "ok" else 0, "status", status_txt))

        uptime_match = re.search(r"opera.*?(\d+)\s*dias", html)
        if uptime_match:
            m.append(self._metric("uptime_dias", int(uptime_match.group(1)), "dias", "ok"))

        faltas = val(r"mero de faltas.*?(\d+)", html)
        if faltas is not None:
            m.append(self._metric("faltas", faltas, "count", "ok"))

        # Entrada — Tensão Fase A/B/C
        tensoes_in = re.findall(r"Tens[^<]*o</td>\s*<td class=tdv>\s*([\d.]+)\s*V", html)
        if len(tensoes_in) >= 3:
            for i, fase in enumerate(["A", "B", "C"]):
                v = float(tensoes_in[i])
                status = "critical" if v < 100 else "ok"
                m.append(self._metric(f"tensao_entrada_fase{fase}", v, "V", status))

        # Saída — Tensão, Corrente, Potência, Carga
        # Encontrar seção de saída
        saida_idx = html.find("Sa")
        saida = html[saida_idx:] if saida_idx > 0 else ""

        tensoes_out = re.findall(r"Tens[^<]*o</td>\s*<td class=tdv>\s*([\d.]+)\s*V", saida)
        if len(tensoes_out) >= 3:
            for i, fase in enumerate(["A", "B", "C"]):
                m.append(self._metric(f"tensao_saida_fase{fase}", float(tensoes_out[i]), "V", "ok"))

        cargas = re.findall(r"Carga Utilizada</td>\s*<td class=tdv>\s*(\d+)\s*%", html)
        if cargas:
            for i, fase in enumerate(["A", "B", "C"][:len(cargas)]):
                v = int(cargas[i])
                status = "critical" if v > 90 else "warning" if v > 80 else "ok"
                m.append(self._metric(f"carga_fase{fase}", v, "%", status))
            # Carga máxima como métrica principal
            max_carga = max(int(c) for c in cargas)
            m.append(self._metric("carga_max", max_carga, "%",
                                  "critical" if max_carga > 90 else "warning" if max_carga > 80 else "ok"))

        pot_ativa = re.findall(r"ncia Ativa</td>\s*<td class=tdv>\s*(\d+)\s*W", html)
        if pot_ativa:
            total_w = sum(int(p) for p in pot_ativa)
            m.append(self._metric("potencia_ativa_total", total_w, "W", "ok"))

        # Bateria
        bat_tensao = val(r"Bateria.*?Tens.*?o.*?([\d.]+)\s*V", html)
        if bat_tensao is not None:
            m.append(self._metric("bateria_tensao", bat_tensao, "V", "ok"))

        autonomia = val(r"Autonomia.*?(\d+)\s*minutos", html)
        if autonomia is not None:
            status = "critical" if autonomia < 5 else "warning" if autonomia < 10 else "ok"
            m.append(self._metric("bateria_autonomia", autonomia, "min", status))

        descarga = val(r"descarga.*?([\d.]+)\s*A", html)
        if descarga is not None:
            m.append(self._metric("bateria_corrente_descarga", descarga, "A", "ok"))

        return m

    def _extract_value(self, pattern: str, text: str) -> Optional[float]:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                return None
        return None

    def _metric(self, name: str, value: float, unit: str, status: str) -> Dict[str, Any]:
        return {
            "sensor_type": "engetron",
            "sensor_name": f"Engetron {name}",
            "name": f"Engetron {name}",
            "value": value,
            "unit": unit,
            "status": status,
        }

    def _offline_metrics(self) -> List[Dict[str, Any]]:
        return [self._metric("status", 0, "status", "critical")]
