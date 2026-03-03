import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import sys
import os
import logging
from pathlib import Path

class CorujaProbeService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CorujaProbe"
    _svc_display_name_ = "Coruja Monitor Probe"
    _svc_description_ = "Distributed monitoring probe for Coruja Monitor platform"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.probe = None
        socket.setdefaulttimeout(60)
        
        # Setup logging to file
        self.log_file = Path(__file__).parent / "probe_service.log"
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(str(self.log_file)),
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def SvcStop(self):
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.probe:
            try:
                self.probe.stop()
            except Exception as e:
                self.logger.error(f"Error stopping probe: {e}")
    
    def SvcDoRun(self):
        self.logger.info("Service starting...")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
    
    def main(self):
        try:
            self.logger.info("Initializing probe core...")
            
            # Get the directory where the service executable is located
            if hasattr(sys, 'frozen'):
                # Running as compiled service
                probe_dir = Path(sys.executable).parent
            else:
                # Running as script
                probe_dir = Path(__file__).parent.resolve()
            
            self.logger.info(f"Probe directory: {probe_dir}")
            
            # Change to probe directory
            os.chdir(str(probe_dir))
            self.logger.info(f"Working directory: {os.getcwd()}")
            
            # Add current directory to path
            if str(probe_dir) not in sys.path:
                sys.path.insert(0, str(probe_dir))
            
            # Import and initialize probe
            self.logger.info("Importing ProbeCore...")
            from probe_core import ProbeCore
            self.logger.info("ProbeCore imported successfully")
            
            self.probe = ProbeCore()
            self.logger.info("ProbeCore initialized successfully")
            
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, 'Probe core started')
            )
            
            # Start probe in main thread
            self.logger.info("Starting probe...")
            self.probe.start()
            
        except Exception as e:
            error_msg = f"Probe service error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            servicemanager.LogErrorMsg(error_msg)
            # Don't raise - let service stay running for debugging
            time.sleep(10)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CorujaProbeService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CorujaProbeService)
