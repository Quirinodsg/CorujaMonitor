from typing import List, Dict, Any
import subprocess
import time

class UDMCollector:
    def __init__(self, targets: List[str]):
        self.targets = targets
    
    def collect(self) -> List[Dict[str, Any]]:
        """Collect ping status"""
        metrics = []
        
        for target in self.targets:
            try:
                is_up, latency = self._ping_target(target)
                
                # Use simple "PING" as name for the primary target (8.8.8.8)
                # For other targets, use descriptive names
                if target == "8.8.8.8":
                    sensor_name = "PING"
                else:
                    sensor_name = f"ping_{target.replace('.', '_')}"
                
                metrics.append({
                    "type": "ping",
                    "name": sensor_name,
                    "value": latency if is_up else 0,
                    "unit": "ms",
                    "status": "ok" if is_up else "critical",
                    "metadata": {
                        "target": target,
                        "latency_ms": latency,
                        "link_status": "up" if is_up else "down"
                    }
                })
            except Exception as e:
                metrics.append({
                    "type": "ping",
                    "name": "PING" if target == "8.8.8.8" else f"ping_{target.replace('.', '_')}",
                    "value": 0,
                    "unit": "ms",
                    "status": "critical",
                    "metadata": {
                        "target": target,
                        "error": str(e)
                    }
                })
        
        return metrics
    
    def _ping_target(self, target: str) -> tuple:
        """Ping a target and return (is_up, latency_ms)"""
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '1000', target],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Parse latency from output
                for line in result.stdout.split('\n'):
                    if 'time=' in line or 'tempo=' in line:
                        try:
                            latency_str = line.split('time=')[1].split('ms')[0] if 'time=' in line else line.split('tempo=')[1].split('ms')[0]
                            latency = float(latency_str)
                            return True, latency
                        except:
                            pass
                return True, 0
            else:
                return False, None
        except Exception:
            return False, None
