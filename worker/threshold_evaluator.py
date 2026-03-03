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
