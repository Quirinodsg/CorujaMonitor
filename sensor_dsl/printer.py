"""
DSL Printer — Coruja Monitor v3.0
Converte objetos Sensor Pydantic de volta para string DSL formatada.
Property 18: round-trip (parse → print → parse) deve produzir Sensor equivalente.
"""
from core.spec.models import Sensor


class DSLPrinter:
    """Serializa Sensor para string DSL formatada."""

    def print(self, sensor: Sensor) -> str:
        """
        Converte Sensor → DSL string.
        Formato:
          sensor "name" {
            protocol = "wmi"
            interval = 60
            ...
          }
        """
        lines = [f'sensor "{sensor.type}" {{']

        protocol = sensor.protocol if isinstance(sensor.protocol, str) else sensor.protocol.value
        lines.append(f'  protocol = "{protocol}"')
        lines.append(f'  interval = {sensor.interval}')

        if sensor.timeout != 30:
            lines.append(f'  timeout = {sensor.timeout}')

        if sensor.retries != 3:
            lines.append(f'  retries = {sensor.retries}')

        if sensor.query:
            lines.append(f'  query = "{sensor.query}"')

        if sensor.thresholds:
            if "warning" in sensor.thresholds:
                w = sensor.thresholds["warning"]
                # Imprimir como int se for inteiro
                w_str = str(int(w)) if w == int(w) else str(w)
                lines.append(f'  warning = {w_str}')
            if "critical" in sensor.thresholds:
                c = sensor.thresholds["critical"]
                c_str = str(int(c)) if c == int(c) else str(c)
                lines.append(f'  critical = {c_str}')

        lines.append('}')
        return '\n'.join(lines)

    def print_all(self, sensors: list[Sensor]) -> str:
        """Serializa lista de sensores separados por linha em branco."""
        return '\n\n'.join(self.print(s) for s in sensors)
