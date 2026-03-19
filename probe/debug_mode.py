"""
FASE 3 — Debug Mode: Coruja Monitor v3.0
Loga execução de sensores com logs estruturados JSON.
Uso: python probe/debug_mode.py --sensor http --host http://example.com
"""
import json
import time
import logging
import argparse
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Structured JSON logger
class StructuredLogger:
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)

    def log(self, level: str, event: str, **fields):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
            **fields,
        }
        print(json.dumps(record, default=str))


log = StructuredLogger("coruja.debug")


def run_sensor_debug(sensor_type: str, host: str, **kwargs) -> Dict[str, Any]:
    """Executa sensor em modo debug com logs estruturados."""
    log.log("INFO", "sensor_start", sensor_id=kwargs.get("sensor_id", "debug"),
            host=host, protocol=sensor_type)

    start = time.monotonic()
    result = {}
    error = None

    try:
        if sensor_type == "icmp":
            sys.path.insert(0, os.path.dirname(__file__))
            from collectors.icmp_sensor import ICMPSensor
            sensor = ICMPSensor(host, timeout=kwargs.get("timeout", 3))
            result = sensor.collect()

        elif sensor_type == "tcp":
            from collectors.tcp_port_sensor import TCPPortSensor
            port = int(kwargs.get("port", 80))
            sensor = TCPPortSensor(host, port, timeout=kwargs.get("timeout", 3.0))
            result = sensor.collect()

        elif sensor_type == "http":
            from collectors.http_sensor import HTTPSensor
            sensor = HTTPSensor(host, timeout=kwargs.get("timeout", 10.0))
            result = sensor.collect()

        else:
            result = {"status": "critical", "error": f"Unknown sensor type: {sensor_type}"}

    except Exception as e:
        error = str(e)
        result = {"status": "critical", "error": error}

    latency_ms = (time.monotonic() - start) * 1000

    log.log(
        "INFO" if result.get("status") == "ok" else "ERROR",
        "sensor_result",
        sensor_id=kwargs.get("sensor_id", "debug"),
        host=host,
        protocol=sensor_type,
        status=result.get("status", "unknown"),
        error=result.get("error"),
        latency_ms=round(latency_ms, 2),
        value=result.get("value"),
        unit=result.get("unit"),
    )

    return result


def simulate_redis_publish(result: Dict[str, Any], sensor_id: str = "debug"):
    """Simula publicação no Redis Stream com log estruturado."""
    log.log("INFO", "redis_publish_attempt",
            sensor_id=sensor_id,
            stream_key="metrics:raw",
            status=result.get("status"))

    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
        r.ping()

        entry = {
            "sensor_id": sensor_id,
            "value": str(result.get("value", 0)),
            "status": result.get("status", "unknown"),
            "timestamp": str(time.time()),
        }
        msg_id = r.xadd("metrics:raw", entry, maxlen=100000, approximate=True)

        log.log("INFO", "redis_publish_ok", sensor_id=sensor_id, msg_id=msg_id)
        return msg_id

    except Exception as e:
        log.log("ERROR", "redis_publish_failed", sensor_id=sensor_id, error=str(e))
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coruja Monitor — Debug Mode")
    parser.add_argument("--sensor", choices=["icmp", "tcp", "http"], required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--redis", action="store_true", help="Testar publicação no Redis")
    args = parser.parse_args()

    result = run_sensor_debug(args.sensor, args.host, port=args.port, timeout=args.timeout)

    if args.redis:
        simulate_redis_publish(result)

    print("\n--- RESULTADO FINAL ---")
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result.get("status") == "ok" else 1)
