from typing import Tuple

# Sensores SNMP que são status-based (value=0 = offline/critical, value=1 = ok)
# Identificados pelo nome do sensor — sensores de tráfego de rede são excluídos
_SNMP_NETWORK_KEYWORDS = ('network in', 'network out', 'network_in', 'network_out',
                           'link in', 'link out', 'traffic')


def _is_snmp_status_sensor(sensor) -> bool:
    """Retorna True se o sensor SNMP é status-based (não tráfego de rede)."""
    name_lower = (sensor.name or '').lower()
    # Sensores de tráfego de rede usam thresholds numéricos — não são status-based
    if any(kw in name_lower for kw in _SNMP_NETWORK_KEYWORDS):
        return False
    # Sensores SNMP sem threshold configurado são status-based
    # (Nobreak, Ar-condicionado, Storage, Impressora via SNMP)
    if sensor.threshold_warning is None and sensor.threshold_critical is None:
        return True
    # Sensores SNMP com threshold configurado mas value=0 indicam offline
    # (ex: Nobreak com threshold_w=80, threshold_c=95 — value=0 = sem resposta SNMP)
    return False


def evaluate_thresholds(sensor, value: float) -> Tuple[bool, str]:
    """
    Evaluate if a metric value breaches thresholds.
    Returns: (threshold_breached, severity)
    """
    # ── Service sensors ──
    # value=0 = offline (critical), value=1 = online (ok)
    if sensor.sensor_type == 'service':
        return (True, "critical") if value == 0 else (False, "ok")

    # ── Status-based sensors (conflex, engetron, equallogic, printer) ──
    # value=0 = offline/critical, value>0 = ok
    if sensor.sensor_type in ('conflex', 'engetron', 'equallogic', 'printer'):
        return (True, "critical") if value == 0 else (False, "ok")

    # ── SNMP sensors ──
    # value=0 sempre significa que o SNMP não respondeu (dispositivo offline)
    # independente dos thresholds configurados.
    # Exceção: sensores de tráfego de rede E sensores com thresholds numéricos configurados
    # (ex: Storage com threshold_w=97 usa avaliação numérica, não status-based)
    if sensor.sensor_type in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch'):
        name_lower = (sensor.name or '').lower()
        is_network_traffic = any(kw in name_lower for kw in _SNMP_NETWORK_KEYWORDS)
        # Sensores com thresholds numéricos configurados usam avaliação numérica
        has_numeric_thresholds = (
            sensor.threshold_warning is not None and sensor.threshold_warning > 1
        ) or (
            sensor.threshold_critical is not None and sensor.threshold_critical > 1
        )
        if value == 0 and not is_network_traffic and not has_numeric_thresholds:
            return True, "critical"
        # Sensores com thresholds numéricos e value>0 usam avaliação padrão abaixo

    # ── PING sensor ──
    # value=0 = host DOWN, value>0 = host UP (latência em ms)
    if sensor.sensor_type == 'ping':
        return (True, "critical") if value == 0 else (False, "ok")

    # ── UPTIME/System sensor ──
    # value <= 0.0035 dias (~5 min) = reboot recente
    if sensor.sensor_type == 'system':
        return (True, "warning") if value <= 0.0035 else (False, "ok")

    # ── Network sensors (bytes/s) ──
    if sensor.sensor_type == 'network':
        value_mbps = value / 1024 / 1024
        if sensor.threshold_critical is not None and value_mbps >= sensor.threshold_critical:
            return True, "critical"
        if sensor.threshold_warning is not None and value_mbps >= sensor.threshold_warning:
            return True, "warning"
        return False, "ok"

    # ── Standard threshold evaluation (cpu, memory, disk, snmp com threshold) ──
    w = sensor.threshold_warning
    c = sensor.threshold_critical

    if c is not None and value >= c:
        return True, "critical"
    if w is not None and value >= w:
        return True, "warning"

    return False, "ok"
