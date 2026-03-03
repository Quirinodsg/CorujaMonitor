import psutil
from typing import List, Dict, Any

class NetworkCollector:
    def __init__(self):
        self.last_stats = None
    
    def collect(self) -> List[Dict[str, Any]]:
        """Collect network metrics"""
        metrics = []
        
        net_io = psutil.net_io_counters()
        
        if self.last_stats:
            bytes_sent_rate = net_io.bytes_sent - self.last_stats.bytes_sent
            bytes_recv_rate = net_io.bytes_recv - self.last_stats.bytes_recv
        else:
            bytes_sent_rate = 0
            bytes_recv_rate = 0
        
        self.last_stats = net_io
        
        # Network IN (received)
        metrics.append({
            "type": "network",
            "name": "Network IN",
            "value": bytes_recv_rate,
            "unit": "bytes/s",
            "status": "ok",
            "metadata": {
                "bytes_recv": net_io.bytes_recv,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin
            }
        })
        
        # Network OUT (sent)
        metrics.append({
            "type": "network",
            "name": "Network OUT",
            "value": bytes_sent_rate,
            "unit": "bytes/s",
            "status": "ok",
            "metadata": {
                "bytes_sent": net_io.bytes_sent,
                "packets_sent": net_io.packets_sent,
                "errout": net_io.errout
            }
        })
        
        return metrics
