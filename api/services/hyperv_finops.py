"""
Hyper-V FinOps Engine.

Analyzes Hyper-V metrics for cost optimization:
  - Overprovisioned VM detection (avg CPU < 20% for 7 consecutive days)
  - Idle VM detection (avg CPU < 5% for 30 consecutive minutes)
  - Per-VM cost estimation
  - Host density metrics
  - Recommendation generation

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


class HyperVFinOpsEngine:
    """Analyzes Hyper-V metrics for cost optimization."""

    # Default unit rates (monthly)
    DEFAULT_RATES: Dict[str, float] = {
        "rate_vcpu": 15.0,
        "rate_mem": 5.0,
        "rate_storage": 0.10,
    }

    def detect_overprovisioned(self, vm_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect VMs with avg CPU < 20% for 7 consecutive days.

        Args:
            vm_metrics: List of dicts with keys:
                - vm_name (str)
                - host_name (str)
                - daily_avg_cpu (list[float]): daily CPU averages, most recent last,
                  each entry represents one day.

        Returns:
            List of overprovisioned VM dicts with vm_name, host_name, avg_cpu, days.
        """
        results: List[Dict[str, Any]] = []
        for vm in vm_metrics:
            daily = vm.get("daily_avg_cpu", [])
            if len(daily) < 7:
                continue
            # Check last 7 consecutive days
            last_7 = daily[-7:]
            if all(avg < 20.0 for avg in last_7):
                overall_avg = sum(last_7) / 7.0
                results.append({
                    "vm_name": vm["vm_name"],
                    "host_name": vm["host_name"],
                    "avg_cpu": round(overall_avg, 2),
                    "days": 7,
                    "category": "overprovisioned",
                })
        return results

    def detect_idle(self, vm_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect VMs with avg CPU < 5% for 30 consecutive minutes.

        Args:
            vm_metrics: List of dicts with keys:
                - vm_name (str)
                - host_name (str)
                - cpu_samples (list[float]): CPU samples taken at regular intervals
                  covering at least 30 minutes. Each sample represents one minute.

        Returns:
            List of idle VM dicts with vm_name, host_name, avg_cpu, minutes.
        """
        results: List[Dict[str, Any]] = []
        for vm in vm_metrics:
            samples = vm.get("cpu_samples", [])
            if len(samples) < 30:
                continue
            # Check last 30 consecutive samples (minutes)
            last_30 = samples[-30:]
            if all(s < 5.0 for s in last_30):
                overall_avg = sum(last_30) / 30.0
                results.append({
                    "vm_name": vm["vm_name"],
                    "host_name": vm["host_name"],
                    "avg_cpu": round(overall_avg, 2),
                    "minutes": 30,
                    "category": "idle",
                })
        return results

    def estimate_vm_cost(
        self,
        vm: Dict[str, Any],
        rates: Optional[Dict[str, float]] = None,
    ) -> float:
        """Estimate monthly cost for a VM.

        Formula: vcpus * rate_vcpu + memory_gb * rate_mem + storage_gb * rate_storage

        Args:
            vm: Dict with keys vcpus (int), memory_gb (float), storage_gb (float).
            rates: Optional dict with rate_vcpu, rate_mem, rate_storage.
                   Falls back to DEFAULT_RATES.

        Returns:
            Estimated monthly cost (>= 0).
        """
        r = rates if rates is not None else self.DEFAULT_RATES
        vcpus = vm.get("vcpus", 0)
        memory_gb = vm.get("memory_gb", 0.0)
        storage_gb = vm.get("storage_gb", 0.0)

        cost = (
            vcpus * r.get("rate_vcpu", 0.0)
            + memory_gb * r.get("rate_mem", 0.0)
            + storage_gb * r.get("rate_storage", 0.0)
        )
        return max(0.0, cost)

    def compute_density(self, host: Dict[str, Any]) -> Dict[str, Any]:
        """Compute host density metrics.

        Args:
            host: Dict with keys:
                - total_cpus (int): Physical CPU count (> 0)
                - total_memory_gb (float): Physical memory in GB (> 0)
                - vms (list[dict]): Each VM has vcpus (int) and memory_gb (float)

        Returns:
            Dict with vms_per_host, vcpu_overcommit_ratio, memory_overcommit_ratio.
        """
        vms = host.get("vms", [])
        total_cpus = host.get("total_cpus", 1)
        total_memory_gb = host.get("total_memory_gb", 1.0)

        total_vm_vcpus = sum(vm.get("vcpus", 0) for vm in vms)
        total_vm_memory = sum(vm.get("memory_gb", 0.0) for vm in vms)

        return {
            "vms_per_host": len(vms),
            "vcpu_overcommit_ratio": round(total_vm_vcpus / total_cpus, 2) if total_cpus > 0 else 0.0,
            "memory_overcommit_ratio": round(total_vm_memory / total_memory_gb, 2) if total_memory_gb > 0 else 0.0,
        }

    def generate_recommendations(
        self,
        overprovisioned: Optional[List[Dict[str, Any]]] = None,
        idle: Optional[List[Dict[str, Any]]] = None,
        density: Optional[Dict[str, Any]] = None,
        cost_data: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate FinOps recommendations.

        Categories: overprovisioned, idle, right-size, rebalance.

        Args:
            overprovisioned: Output from detect_overprovisioned.
            idle: Output from detect_idle.
            density: Output from compute_density (for rebalance hints).
            cost_data: List of dicts with vm_name, host_name, monthly_cost, vcpus,
                       memory_gb, storage_gb for right-size analysis.

        Returns:
            List of recommendation dicts with category, vm_name, host_name,
            description, suggested_action, estimated_savings.
        """
        recommendations: List[Dict[str, Any]] = []

        # Overprovisioned recommendations
        for vm in (overprovisioned or []):
            recommendations.append({
                "category": "overprovisioned",
                "vm_name": vm["vm_name"],
                "host_name": vm["host_name"],
                "description": (
                    f"VM {vm['vm_name']} has avg CPU {vm['avg_cpu']}% "
                    f"over the last {vm['days']} days"
                ),
                "suggested_action": (
                    f"Reduce allocated vCPUs for {vm['vm_name']} or consolidate workloads"
                ),
                "estimated_savings": None,
            })

        # Idle recommendations
        for vm in (idle or []):
            recommendations.append({
                "category": "idle",
                "vm_name": vm["vm_name"],
                "host_name": vm["host_name"],
                "description": (
                    f"VM {vm['vm_name']} has avg CPU {vm['avg_cpu']}% "
                    f"over the last {vm['minutes']} minutes"
                ),
                "suggested_action": (
                    f"Consider shutting down {vm['vm_name']} or scheduling auto-shutdown"
                ),
                "estimated_savings": None,
            })

        # Right-size recommendations from cost data
        for vm in (cost_data or []):
            if vm.get("monthly_cost", 0) > 0:
                recommendations.append({
                    "category": "right-size",
                    "vm_name": vm["vm_name"],
                    "host_name": vm["host_name"],
                    "description": (
                        f"VM {vm['vm_name']} costs ${vm['monthly_cost']:.2f}/month "
                        f"({vm.get('vcpus', 0)} vCPUs, {vm.get('memory_gb', 0)}GB RAM, "
                        f"{vm.get('storage_gb', 0)}GB storage)"
                    ),
                    "suggested_action": (
                        f"Review resource allocation for {vm['vm_name']} to match actual usage"
                    ),
                    "estimated_savings": vm.get("estimated_savings"),
                })

        # Rebalance recommendation if density data shows imbalance
        if density and density.get("vcpu_overcommit_ratio", 0) > 4.0:
            recommendations.append({
                "category": "rebalance",
                "vm_name": "",
                "host_name": density.get("host_name", ""),
                "description": (
                    f"Host {density.get('host_name', '')} has vCPU overcommit ratio "
                    f"of {density.get('vcpu_overcommit_ratio', 0)}:1"
                ),
                "suggested_action": "Migrate VMs to less loaded hosts to reduce overcommit",
                "estimated_savings": None,
            })

        if density and density.get("memory_overcommit_ratio", 0) > 1.5:
            recommendations.append({
                "category": "rebalance",
                "vm_name": "",
                "host_name": density.get("host_name", ""),
                "description": (
                    f"Host {density.get('host_name', '')} has memory overcommit ratio "
                    f"of {density.get('memory_overcommit_ratio', 0)}:1"
                ),
                "suggested_action": "Migrate VMs to hosts with available memory capacity",
                "estimated_savings": None,
            })

        return recommendations
