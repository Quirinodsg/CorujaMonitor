"""
Hyper-V WebSocket Router — Coruja Monitor
Real-time Hyper-V metric updates with per-client subscription filters.
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Hyper-V WebSocket"])

PING_INTERVAL = 60  # seconds


class HyperVClient:
    """Represents a connected WebSocket client with optional subscription filters."""

    __slots__ = ("ws", "filters")

    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.filters: Dict[str, str] = {}

    def matches(self, message: Dict[str, Any]) -> bool:
        """Check if a broadcast message matches this client's filters."""
        if not self.filters:
            return True
        data = message.get("data", {})
        for key, value in self.filters.items():
            if key in data and str(data[key]) != str(value):
                return False
        return True


class HyperVConnectionManager:
    """Manages WebSocket connections with per-client subscription filters."""

    def __init__(self):
        self._clients: List[HyperVClient] = []

    async def connect(self, ws: WebSocket) -> HyperVClient:
        await ws.accept()
        client = HyperVClient(ws)
        self._clients.append(client)
        logger.info("Hyper-V WS client connected (%d total)", len(self._clients))
        return client

    def disconnect(self, client: HyperVClient):
        if client in self._clients:
            self._clients.remove(client)
        logger.info("Hyper-V WS client disconnected (%d remaining)", len(self._clients))

    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all clients whose filters match."""
        dead: List[HyperVClient] = []
        for client in self._clients:
            if client.matches(message):
                try:
                    await client.ws.send_json(message)
                except Exception:
                    dead.append(client)
        for client in dead:
            self.disconnect(client)

    @property
    def client_count(self) -> int:
        return len(self._clients)


manager = HyperVConnectionManager()


def _build_message(msg_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a standard broadcast message."""
    return {
        "type": msg_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


@router.websocket("/api/v1/ws/hyperv")
async def ws_hyperv(websocket: WebSocket):
    """
    Real-time Hyper-V updates.

    Client → Server:
      {"action": "subscribe", "filters": {"host_id": "uuid", "status": "running"}}

    Server → Client:
      {"type": "overview_update"|"host_update"|"vm_update"|"alert_update",
       "timestamp": "ISO8601", "data": {...}}
    """
    client = await manager.connect(websocket)
    ping_task: Optional[asyncio.Task] = None

    async def _ping_loop():
        """Send ping frames to detect idle connections."""
        try:
            while True:
                await asyncio.sleep(PING_INTERVAL)
                try:
                    await websocket.send_json({"type": "ping", "timestamp": datetime.now(timezone.utc).isoformat()})
                except Exception:
                    break
        except asyncio.CancelledError:
            pass

    try:
        ping_task = asyncio.create_task(_ping_loop())

        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            action = msg.get("action")
            if action == "subscribe":
                filters = msg.get("filters", {})
                client.filters = {k: str(v) for k, v in filters.items() if v is not None}
                await websocket.send_json({
                    "type": "subscribed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "filters": client.filters,
                })
            elif action == "pong":
                pass  # client responded to ping
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.debug("Hyper-V WS error: %s", e)
    finally:
        if ping_task:
            ping_task.cancel()
        manager.disconnect(client)
