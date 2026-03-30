from typing import Tuple

def evaluate_thresholds(sensor, value: float) -> Tuple[bool, str]:
    """
    Evaluate if a metric value breaches thresholds
    Returns: (threshold_breached, severity)
    """
    # Special handling for service sensors
    # Service sensors: value=0 means offline (critical), value=1 means online (ok)
    if sensor.sensor_type == 'service':
        if value == 0:
            return True, "critical"
        else:
            return False, "ok"
    
    # ── PING sensor (Zabbix/PRTG style) ──
    # ONLY alert on DOWN (no response / timeout). value=0 means no response.
    # High latency (300ms, 500ms) is just a metric — NEVER creates an incident.
    # This matches how Zabbix "ICMP ping" and PRTG "Ping" sensors work:
    # they only alert on "Request timed out", not on slow response.
    if sensor.sensor_type == 'ping':
        if value == 0:
            return True, "critical"  # Host DOWN — no response
        # Any response (even slow) = host is UP = OK
        return False, "ok"

    # ── UPTIME/System sensor (Zabbix style) ──
    # Alert ONLY on reboot detection: uptime near 0.
    # Uses a VERY tight window (< 2 minutes = 0.0014 days) to fire only ONCE.
    # After 2 min uptime, it's OK and the incident auto-resolves.
    # Combined with 30-min cooldown in tasks.py, this ensures 1 incident per reboot.
    if sensor.sensor_type == 'system':
        if value <= 0.0014:  # ~2 minutes — just rebooted
            return True, "warning"
        return False, "ok"
    
    # Special handling for network sensors
    # Network sensors: value is in bytes/s, thresholds are in MB/s
    if sensor.sensor_type == 'network':
        # Convert bytes/s to MB/s
        value_mbps = value / 1024 / 1024
        
        if sensor.threshold_critical is not None and value_mbps >= sensor.threshold_critical:
            return True, "critical"
        
        if sensor.threshold_warning is not None and value_mbps >= sensor.threshold_warning:
            return True, "warning"
        
        return False, "ok"
    
    # Standard threshold evaluation for other sensor types (cpu, memory, disk)
    if sensor.threshold_critical is not None and value >= sensor.threshold_critical:
        return True, "critical"
    
    if sensor.threshold_warning is not None and value >= sensor.threshold_warning:
        return True, "warning"
    
    return False, "ok"
