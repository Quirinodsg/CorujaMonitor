"""
Hyper-V Health Score Engine.

Computes a health score (0-100) for Hyper-V hosts using weighted factors:
  CPU:      0.30 weight (critical penalty if > 90%)
  Memory:   0.25 weight (critical penalty if > 95%)
  Storage:  0.20 weight
  VM ratio: 0.15 weight
  Alerts:   0.10 weight (penalty per alert)

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""


def compute_health_score(
    cpu_percent: float,
    memory_percent: float,
    storage_percent: float,
    vm_ratio: float,
    alert_count: int,
) -> float:
    """Compute health score (0-100) using weighted factors.

    Args:
        cpu_percent: CPU utilization 0-100.
        memory_percent: Memory utilization 0-100.
        storage_percent: Storage utilization 0-100.
        vm_ratio: Ratio of running VMs to total VMs (0.0-1.0).
        alert_count: Number of active alerts (>= 0).

    Returns:
        Health score clamped to [0, 100].
    """
    # CPU component (weight 0.30) — critical penalty caps at 10 when > 90%
    cpu_score = 30.0 * (1.0 - cpu_percent / 100.0)
    if cpu_percent > 90.0:
        cpu_score = max(10.0, cpu_score)

    # Memory component (weight 0.25) — critical penalty caps at 5 when > 95%
    mem_score = 25.0 * (1.0 - memory_percent / 100.0)
    if memory_percent > 95.0:
        mem_score = max(5.0, mem_score)

    # Storage component (weight 0.20)
    storage_score = 20.0 * (1.0 - storage_percent / 100.0)

    # VM ratio component (weight 0.15)
    vm_score = 15.0 * vm_ratio

    # Alert penalty component (weight 0.10)
    alert_score = max(0.0, 10.0 - alert_count * 2.0)

    health = cpu_score + mem_score + storage_score + vm_score + alert_score

    # Clamp to [0, 100]
    return max(0.0, min(100.0, health))
