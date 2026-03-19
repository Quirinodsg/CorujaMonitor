# Proxy para probe/engine/prometheus_exporter.py
from probe.engine.prometheus_exporter import *
try:
    from probe.engine.prometheus_exporter import PrometheusExporter
except ImportError:
    pass
