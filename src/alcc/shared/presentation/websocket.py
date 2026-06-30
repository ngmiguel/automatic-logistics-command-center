import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from alcc.shared.infrastructure.logging import get_logger
from alcc.shared.infrastructure.redis_client import NOTIFICATION_CHANNEL, TELEMETRY_CHANNEL, redis_client

logger = get_logger(__name__)
router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self.active.append(ws)
        logger.info("ws_connected", total=len(self.active))

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            if ws in self.active:
                self.active.remove(ws)
        logger.info("ws_disconnected", total=len(self.active))

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        async with self._lock:
            clients = self.active.copy()
        for ws in clients:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)


manager = ConnectionManager()


async def _redis_listener() -> None:
    pubsub = await redis_client.subscribe(TELEMETRY_CHANNEL, NOTIFICATION_CHANNEL)
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            data = json.loads(message["data"])
            channel = message["channel"]
            await manager.broadcast({"channel": channel, "data": data})
        except Exception as e:
            logger.error("ws_broadcast_error", error=str(e))


_listener_task: asyncio.Task | None = None


def start_ws_listener() -> None:
    global _listener_task
    if _listener_task is None or _listener_task.done():
        _listener_task = asyncio.create_task(_redis_listener())


@router.websocket("/ws/telemetry")
async def telemetry_ws(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)


@router.websocket("/ws/dashboard")
async def dashboard_ws(ws: WebSocket) -> None:
    await manager.connect(ws)
    vehicle_ids = await redis_client.get_all_telemetry_keys()
    for vid in vehicle_ids[:100]:
        data = await redis_client.get_telemetry(vid)
        if data:
            await ws.send_json({"channel": TELEMETRY_CHANNEL, "data": data})
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
