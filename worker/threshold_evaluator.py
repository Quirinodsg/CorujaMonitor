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
    
    # Special handling for ping sensors
    # Ping sensors: value=0 means offline (critical), otherwise check latency thresholds
    if sensor.sensor_type == 'ping':
        if value == 0:
            return True, "critical"
        # Check latency thresholds
        if sensor.threshold_critical is not None and value >= sensor.threshold_critical:
            return True, "critical"
        if sensor.threshold_warning is not None and value >= sensor.threshold_warning:
            return True, "warning"
        return False, "ok"

    # Special handling for uptime/system sensors
    # Uptime value is in DAYS. A reboot is detected when uptime drops below threshold.
    # Default: warning if uptime < 0.5 days (12h), critical if uptime < 0.083 days (2h)
    # This catches reboots — server comes back with uptime near 0.
    if sensor.sensor_type == 'system':
        warn_threshold = sensor.threshold_warning if sensor.threshold_warning is not None else 0.5
        crit_threshold = sensor.threshold_critical if sensor.threshold_critical is not None else 0.083
        if value <= crit_threshold:
            return True, "critical"
        if value <= warn_threshold:
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
