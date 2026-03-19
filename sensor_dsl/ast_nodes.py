"""
AST Nodes para o Sensor DSL — Coruja Monitor v3.0
"""
from dataclasses import dataclass, field
from typing import Union


@dataclass
class FieldNode:
    name: str
    value: Union[str, int, float]
    line: int = 0


@dataclass
class SensorNode:
    name: str
    fields: list[FieldNode] = field(default_factory=list)
    extends: str | None = None
    line: int = 0

    def get_field(self, name: str):
        for f in self.fields:
            if f.name == name:
                return f.value
        return None
