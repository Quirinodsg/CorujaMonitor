import psutil
from typing import List, Dict, Any

class MemoryCollector:
    def collect(self) -> List[Dict[str, Any]]:
        """Collect memory metrics"""
        memory = psutil.virtual_memory()
        
        metrics = [
            {
                "type": "memory",
                "name": "Memória",
                "value": memory.percent,
                "unit": "percent",
                "status": self._get_status(memory.percent, 85, 95),
                "metadata": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used
                }
            }
        ]
        
        return metrics
    
    def _get_status(self, value: float, warning: float, critical: float) -> str:
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
