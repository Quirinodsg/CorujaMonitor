# Proxy para probe/engine/sensor_engine.py
from probe.engine.sensor_engine import *
from probe.engine.sensor_engine import SensorEngine, SensorDefinition, SensorResult
try:
    from probe.engine.sensor_engine import SensorType
except ImportError:
    pass
