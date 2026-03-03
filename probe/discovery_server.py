"""
Discovery Server for Probe
Provides HTTP endpoints for real-time service and disk discovery
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

# Import WMI collector for remote discovery
try:
    from collectors.wmi_remote_collector import WMIRemoteCollector
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logging.warning("WMI Remote Collector not available")

app = FastAPI(title="Coruja Probe Discovery Server")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscoveryRequest(BaseModel):
    hostname: str
    username: str
    password: str
    domain: Optional[str] = ""

class ServiceInfo(BaseModel):
    name: str
    display_name: str
    status: str  # running, stopped, paused
    start_type: str  # auto, manual, disabled

class DiskInfo(BaseModel):
    name: str
    display_name: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float

@app.post("/discover/services")
async def discover_services(request: DiscoveryRequest):
    """
    Discover all Windows services on a remote server
    Returns list of services with their current status
    """
    if not WMI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="WMI is not available on this probe"
        )
    
    try:
        logger.info(f"Discovering services on {request.hostname}")
        
        # Create WMI collector
        collector = WMIRemoteCollector(
            hostname=request.hostname,
            username=request.username,
            password=request.password,
            domain=request.domain
        )
        
        # Get all services
        services = collector.discover_services()
        
        logger.info(f"Found {len(services)} services on {request.hostname}")
        
        return {
            "hostname": request.hostname,
            "services": services,
            "count": len(services)
        }
        
    except Exception as e:
        logger.error(f"Error discovering services on {request.hostname}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to discover services: {str(e)}"
        )

@app.post("/discover/disks")
async def discover_disks(request: DiscoveryRequest):
    """
    Discover all disk drives on a remote server
    Returns list of disks with their usage information
    """
    if not WMI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="WMI is not available on this probe"
        )
    
    try:
        logger.info(f"Discovering disks on {request.hostname}")
        
        # Create WMI collector
        collector = WMIRemoteCollector(
            hostname=request.hostname,
            username=request.username,
            password=request.password,
            domain=request.domain
        )
        
        # Get all disks
        disks = collector.discover_disks()
        
        logger.info(f"Found {len(disks)} disks on {request.hostname}")
        
        return {
            "hostname": request.hostname,
            "disks": disks,
            "count": len(disks)
        }
        
    except Exception as e:
        logger.error(f"Error discovering disks on {request.hostname}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to discover disks: {str(e)}"
        )

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "wmi_available": WMI_AVAILABLE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
