"""
Service Monitoring Specs — Coruja Monitor v3
Fonte única da verdade para critérios de aceitação do monitoramento de serviços.

Estas specs são executáveis: cada classe define contratos que os testes verificam.
"""
from dataclasses import dataclass, field
from typing import List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# ServiceDiscoverySpec
# Input:  host_id (str), wmi_connection
# Output: lista de ServiceInfo
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ServiceInfo:
    name: str           # Win32_Service.Name (ex: "Spooler")
    display_name: str   # Win32_Service.DisplayName (ex: "Print Spooler")
    state: str          # "Running" | "Stopped" | "Paused" | ...
    start_mode: str     # "Auto" | "Manual" | "Disabled"


@dataclass
class ServiceDiscoverySpec:
    """
    Acceptance Criteria:
    ✔ Retorna lista não-vazia para host com serviços Auto
    ✔ Cada item tem name, display_name, state, start_mode
    ✔ filter_auto_only=True retorna apenas StartMode='Auto'
    ✔ WMI indisponível → retorna lista vazia (sem exceção)
    ✔ Latência < 5000ms por host
    """
    host_id: str
    filter_auto_only: bool = True

    ACCEPTANCE_CRITERIA = [
        "returns_non_empty_list_for_valid_host",
        "each_item_has_required_fields",
        "filter_auto_only_excludes_manual_services",
        "wmi_unavailable_returns_empty_no_exception",
        "latency_under_5000ms",
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ServiceStatusSpec
# Input:  host + service_name
# Output: status binário (1=running, 0=stopped)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ServiceStatusSpec:
    """
    Acceptance Criteria:
    ✔ Running → value=1, status='ok'
    ✔ Stopped → value=0, status='critical'
    ✔ Qualquer outro estado → value=0, status='critical'
    ✔ value é sempre 0 ou 1 (binário)
    ✔ unit='state'
    ✔ metadata contém service_name, display_name, state, start_mode
    """
    host: str
    service_name: str

    VALID_VALUES = {0, 1}
    RUNNING_STATUS = "ok"
    STOPPED_STATUS = "critical"
    UNIT = "state"
    METRIC_TYPE = "service"

    ACCEPTANCE_CRITERIA = [
        "running_service_value_is_1_status_ok",
        "stopped_service_value_is_0_status_critical",
        "value_is_always_binary",
        "unit_is_state",
        "metadata_has_required_fields",
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ServiceEventSpec
# Regra de transição de estado
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ServiceEventSpec:
    """
    Regras de geração de eventos:
    ✔ Running(1) → Stopped(0): gera evento CRITICAL 'service_down'
    ✔ Stopped(0) → Running(1): gera evento INFO 'service_recovered'
    ✔ Running → Running: NÃO gera evento (idempotência)
    ✔ Stopped → Stopped: NÃO gera evento (idempotência)
    ✔ Primeiro status (sem histórico): gera evento apenas se Stopped
    """
    TRANSITIONS = {
        ("ok", "critical"): ("service_down", "critical"),
        ("critical", "ok"): ("service_recovered", "info"),
        ("ok", "ok"): None,       # sem evento
        ("critical", "critical"): None,  # sem evento
        (None, "critical"): ("service_down", "critical"),  # primeiro status parado
        (None, "ok"): None,       # primeiro status rodando — sem evento
    }

    ACCEPTANCE_CRITERIA = [
        "running_to_stopped_generates_critical_event",
        "stopped_to_running_generates_recovery_event",
        "same_status_no_event",
        "first_stopped_generates_event",
        "first_running_no_event",
        "no_duplicate_events",
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ServiceStreamingSpec
# WebSocket push de status
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ServiceStreamingSpec:
    """
    Acceptance Criteria:
    ✔ Atualização ≤ 5 segundos
    ✔ Payload contém: type, server_id, data[], count, running, stopped
    ✔ Cada item em data tem: sensor_id, server_id, service_name, display_name,
                              state, is_running, status, last_seen
    ✔ Sem flood (não envia se não há mudança — opcional, best-effort)
    ✔ Reconexão automática em caso de queda
    """
    update_interval_seconds: int = 5

    REQUIRED_PAYLOAD_FIELDS = ["type", "server_id", "data", "count", "running", "stopped"]
    REQUIRED_SERVICE_FIELDS = ["sensor_id", "server_id", "service_name", "display_name",
                                "state", "is_running", "status", "last_seen"]

    ACCEPTANCE_CRITERIA = [
        "payload_has_required_fields",
        "each_service_has_required_fields",
        "update_interval_lte_5s",
        "reconnect_on_disconnect",
    ]
