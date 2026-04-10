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
        # Placeholder — será atualizado após parsear tensões de entrada
        status_metric = self._metric("status", 1 if status_txt == "ok" else 0, "status", status_txt)
        m.append(status_metric)

        uptime_match = re.search(r"opera.*?(\d+)\s*dias", html)
        if uptime_match:
            m.append(self._metric("uptime_dias", int(uptime_match.group(1)), "dias", "ok"))

        faltas = val(r"mero de faltas.*?(\d+)", html)
        if faltas is not None:
            m.append(self._metric("faltas", faltas, "count", "ok"))

        # Entrada — Tensão Fase A/B/C (3 valores consecutivos após "Tensão")
        tensao_match = re.search(r"Entrada.*?Tens[^<]*o</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V", html, re.DOTALL)
        queda_de_fase = False
        tensoes_entrada = []
        if tensao_match:
            for i, fase in enumerate(["A", "B", "C"]):
                v = float(tensao_match.group(i + 1))
                tensoes_entrada.append(v)
                fase_status = "critical" if v < 100 else "ok"
                if fase_status == "critical":
                    queda_de_fase = True
                m.append(self._metric(f"tensao_entrada_fase{fase}", v, "V", fase_status))

        # Entrada — Corrente Fase A/B/C
        # O WBRC reporta em dA (deciamperes) — converter para A dividindo por 10
        corrente_match = re.search(r"Entrada.*?Corrente</td>\s*<td class=tdv>\s*([\d.]+)\s*[dD]?[Aa]</td>\s*<td class=tdv>\s*([\d.]+)\s*[dD]?[Aa]</td>\s*<td class=tdv>\s*([\d.]+)\s*[dD]?[Aa]", html, re.DOTALL)
        correntes_entrada = []
        if corrente_match:
            for i, fase in enumerate(["A", "B", "C"]):
                raw = float(corrente_match.group(i + 1))
                # Se valor parece estar em dA (deciamperes), converter para A
                # Valores típicos em dA: 6 dA = 0.6 A; 144 dA = 14.4 A
                c = raw / 10.0 if raw > 20 else raw
                correntes_entrada.append(raw)  # guardar valor raw para detecção de zero
                m.append(self._metric(f"corrente_entrada_fase{fase}", c, "A", "ok"))

        # Detecção de sequência de fase no bypass:
        # Fase com tensão normal (>= 100V) mas corrente de entrada zero indica
        # erro de sequência de fase no bypass (mesmo alarme que o Zabbix WBRC reporta)
        erro_sequencia_fase = False
        if tensoes_entrada and correntes_entrada and len(tensoes_entrada) == 3 and len(correntes_entrada) == 3:
            for i, fase in enumerate(["A", "B", "C"]):
                if tensoes_entrada[i] >= 100 and correntes_entrada[i] == 0:
                    erro_sequencia_fase = True
                    logger.warning(
                        f"Engetron {self.ip}: ERRO SEQUÊNCIA DE FASE no bypass — "
                        f"Fase {fase}: tensão={tensoes_entrada[i]}V, corrente=0A"
                    )

        # Queda de fase eleva o status geral do sensor para critical
        # para garantir criação de incidente e disparo de notificações
        if queda_de_fase:
            status_metric["status"] = "critical"
            logger.warning(f"Engetron {self.ip}: QUEDA DE FASE detectada — status elevado para critical")

        # Erro de sequência de fase no bypass também eleva para critical
        if erro_sequencia_fase:
            status_metric["status"] = "critical"
            logger.warning(f"Engetron {self.ip}: ERRO SEQUÊNCIA DE FASE BYPASS — status elevado para critical")

        # Saída — Tensão Fase A/B/C
        tensao_saida_match = re.search(r"Sa.*?Tens[^<]*o</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V</td>\s*<td class=tdv>\s*([\d.]+)\s*V", html, re.DOTALL)
        if tensao_saida_match:
            for i, fase in enumerate(["A", "B", "C"]):
                m.append(self._metric(f"tensao_saida_fase{fase}", float(tensao_saida_match.group(i + 1)), "V", "ok"))

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
