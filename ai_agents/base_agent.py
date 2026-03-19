"""
Base Agent — Coruja Monitor v3.0
Contrato base para todos os agentes de IA do pipeline.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from core.spec.models import Event, Metric
from topology_engine.graph import TopologyGraph


@dataclass
class AgentContext:
    events: list[Event] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    topology: Optional[TopologyGraph] = None
    feedback_history: list[dict] = field(default_factory=list)
    # Resultados acumulados dos agentes anteriores no pipeline
    pipeline_data: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    output: dict = field(default_factory=dict)
    error: Optional[str] = None


class BaseAgent(ABC):
    """Contrato base para todos os agentes de IA."""

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def process(self, context: AgentContext) -> AgentResult:
        """Processa o contexto e retorna resultado."""
        ...
