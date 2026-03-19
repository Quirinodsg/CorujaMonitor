# Proxy para probe/engine/adaptive_monitor.py
from probe.engine.adaptive_monitor import *
from probe.engine.adaptive_monitor import AdaptiveMonitor
try:
    from probe.engine.adaptive_monitor import INTERVAL_CRITICAL, INTERVAL_WARNING, INTERVAL_NORMAL, OK_CYCLES_TO_RESTORE
except ImportError:
    pass
