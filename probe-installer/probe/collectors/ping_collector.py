import subprocess
import platform
import re
from typing import List, Dict, Any

class PingCollector:
    """Collector for PING metrics (localhost connectivity test)"""
    
    def __init__(self, target: str = "8.8.8.8"):
        """
        Initialize PING collector
        
        Args:
            target: IP or hostname to ping (default: 8.8.8.8 - Google DNS)
        """
        self.target = target
    
    def collect(self) -> List[Dict[str, Any]]:
        """Collect PING metrics"""
        metrics = []
        
        try:
            # Ping command varies by OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', self.target]
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            # Parse ping result
            is_online = result.returncode == 0
            latency = 0
            packet_loss = 100
            
            if is_online:
                output = result.stdout
                
                # Extract latency from output
                if 'time=' in output.lower() or 'time<' in output.lower():
                    try:
                        # Windows: "time=12ms" or "time<1ms"
                        # Linux: "time=12.3 ms"
                        match = re.search(r'time[=<](\d+\.?\d*)', output.lower())
                        if match:
                            latency = float(match.group(1))
                        else:
                            latency = 1  # Default if can't parse but ping succeeded
                    except:
                        latency = 1
                
                packet_loss = 0  # Successful ping = 0% loss
            
            # Determine status — PRTG/Zabbix style:
            # Ping ONLY alerts on DOWN (no response / timeout).
            # High latency is just a metric value, NEVER changes status.
            if not is_online:
                status = "critical"
            else:
                status = "ok"
            
            metrics.append({
                "type": "ping",
                "name": "Ping",
                "value": latency,
                "unit": "ms",
                "status": status,
                "metadata": {
                    "target": self.target,
                    "packet_loss": packet_loss,
                    "is_online": is_online
                }
            })
            
        except subprocess.TimeoutExpired:
            # Timeout = offline
            metrics.append({
                "type": "ping",
                "name": "Ping",
                "value": 0,
                "unit": "ms",
                "status": "critical",
                "metadata": {
                    "target": self.target,
                    "packet_loss": 100,
                    "is_online": False,
                    "error": "timeout"
                }
            })
            
        except Exception as e:
            # Error = offline
            metrics.append({
                "type": "ping",
                "name": "Ping",
                "value": 0,
                "unit": "ms",
                "status": "critical",
                "metadata": {
                    "target": self.target,
                    "packet_loss": 100,
                    "is_online": False,
                    "error": str(e)
                }
            })
        
        return metrics
