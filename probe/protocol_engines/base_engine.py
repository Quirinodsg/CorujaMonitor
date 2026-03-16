"""
Base Protocol Engine - Interface abstrata para todos os protocol engines
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class EngineResult:
    """Resultado padronizado de qualquer protocol engine"""
    status: str                          # "ok", "warning", "critical", "unknown"
    value: float = 0.0                   # valor principal (latência, %, etc.)
    unit: str = ""                       # "ms", "%", "state", etc.
    error: Optional[str] = None          # código de erro se status != ok
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"

    @property
    def is_available(self) -> bool:
        return self.error != "engine_unavailable"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "value": self.value,
            "unit": self.unit,
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseProtocolEngine(ABC):
    """
    Interface abstrata para protocol engines.
    Cada engine encapsula um protocolo de coleta (ICMP, TCP, SNMP, WMI, etc.)
    """

    @abstractmethod
    def execute(self, host: str, **kwargs) -> EngineResult:
        """
        Executa a coleta para o host especificado.

        Args:
            host: IP ou hostname alvo
            **kwargs: Parâmetros específicos do protocolo

        Returns:
            EngineResult com status, valor e metadados
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se o engine está disponível (dependências instaladas).

        Returns:
            True se o engine pode ser usado, False caso contrário
        """
        ...

    def _unavailable_result(self, reason: str = "engine_unavailable") -> EngineResult:
        """Helper para retornar resultado padrão quando engine não está disponível"""
        return EngineResult(
            status="unknown",
            value=0.0,
            unit="",
            error=reason,
            metadata={"available": False},
        )
