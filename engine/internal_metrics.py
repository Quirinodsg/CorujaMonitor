# Proxy para probe/engine/internal_metrics.py
from probe.engine.internal_metrics import *
try:
    from probe.engine.internal_metrics import InternalMetricsCollector
except ImportError:
    pass
