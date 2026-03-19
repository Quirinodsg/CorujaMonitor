"""
DSL Compiler — Coruja Monitor v3.0
Converte source DSL → lista de objetos Sensor (Pydantic).
"""
from uuid import uuid4
from typing import Optional

from core.spec.models import Sensor
from core.spec.enums import Protocol
from sensor_dsl.lexer import Lexer, LexerError
from sensor_dsl.parser import Parser, ParseError
from sensor_dsl.ast_nodes import SensorNode

VALID_PROTOCOLS = {p.value for p in Protocol}

# Campos obrigatórios
REQUIRED_FIELDS = {"protocol", "interval"}

# Campos opcionais com tipos esperados
OPTIONAL_FIELDS = {
    "query": str,
    "warning": (int, float),
    "critical": (int, float),
    "timeout": int,
    "retries": int,
    "tags": str,
    "description": str,
}


class DSLSyntaxError(Exception):
    """Erro de sintaxe no DSL com informações de localização."""
    def __init__(self, message: str, line: int = 0, field: str = ""):
        self.line = line
        self.field = field
        location = f"Linha {line}" if line else "DSL"
        field_info = f", campo '{field}'" if field else ""
        super().__init__(f"{location}{field_info}: {message}")


class DSLCompiler:
    """
    Compila source DSL para lista de objetos Sensor Pydantic.
    Fluxo: Lexer → Parser → SensorNode → Sensor
    """

    def __init__(self, templates: Optional[dict[str, SensorNode]] = None):
        """
        templates: dicionário de templates para herança.
        {template_name: SensorNode}
        """
        self._templates = templates or {}

    def compile(self, source: str) -> list[Sensor]:
        """
        Compila source DSL e retorna lista de Sensor.
        Lança DSLSyntaxError em caso de erro.
        """
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(source)
        except LexerError as e:
            raise DSLSyntaxError(str(e), getattr(e, 'line', 0))

        try:
            parser = Parser(tokens)
            sensor_nodes = parser.parse()
        except ParseError as e:
            raise DSLSyntaxError(str(e), getattr(e, 'line', 0))

        sensors = []
        for node in sensor_nodes:
            sensor = self._compile_node(node)
            sensors.append(sensor)

        return sensors

    def _compile_node(self, node: SensorNode) -> Sensor:
        """Converte SensorNode em Sensor Pydantic."""
        # Aplicar herança de template
        fields = {}
        if node.extends:
            template = self._templates.get(node.extends)
            if template:
                for f in template.fields:
                    fields[f.name] = f.value
            else:
                raise DSLSyntaxError(
                    f"Template '{node.extends}' não encontrado",
                    node.line,
                )

        # Sobrescrever com campos do sensor
        for f in node.fields:
            fields[f.name] = f.value

        # Validar campos obrigatórios
        for req in REQUIRED_FIELDS:
            if req not in fields:
                raise DSLSyntaxError(
                    f"Campo obrigatório '{req}' ausente",
                    node.line,
                    field=req,
                )

        # Validar protocolo
        protocol_val = str(fields["protocol"]).lower()
        if protocol_val not in VALID_PROTOCOLS:
            raise DSLSyntaxError(
                f"Protocolo inválido: '{protocol_val}'. "
                f"Válidos: {sorted(VALID_PROTOCOLS)}",
                node.line,
                field="protocol",
            )

        # Construir thresholds
        thresholds = {}
        if "warning" in fields:
            thresholds["warning"] = float(fields["warning"])
        if "critical" in fields:
            thresholds["critical"] = float(fields["critical"])

        # Construir Sensor
        sensor = Sensor(
            host_id=uuid4(),  # placeholder — será substituído ao associar ao host
            type=node.name,
            protocol=Protocol(protocol_val),
            interval=int(fields["interval"]),
            timeout=int(fields.get("timeout", 30)),
            retries=int(fields.get("retries", 3)),
            query=str(fields["query"]) if "query" in fields else None,
            thresholds=thresholds,
        )
        return sensor
