import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.auth.dependencies import get_current_user
from app.auth.jwt import decode_access_token
from app.models.user import User
from app.services.realtime_service import RealtimeService
from app.db.redis import redis_client

logger = logging.getLogger("energy_platform")

router = APIRouter()


@router.get("/latest", summary="Get latest sensor readings from cache (< 10ms)")
async def latest_readings(
    building_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
):
    readings = await RealtimeService.get_latest_readings(str(building_id))
    return {"items": readings, "total_count": len(readings)}


@router.get("/health", summary="Device health — staleness per sensor")
async def device_health(
    building_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
):
    health = await RealtimeService.get_device_health(str(building_id))
    return {"items": health, "total_count": len(health)}


async def _authenticate_ws(websocket: WebSocket) -> bool:
    """
    Authenticate a WebSocket connection using a JWT token from the query string.

    WebSockets cannot use Authorization headers from the browser, so the token
    is passed as ``?token=<jwt>``.  Returns True if valid, False otherwise.
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return False
    try:
        payload = decode_access_token(token)
        if not payload.get("sub"):
            await websocket.close(code=4001, reason="Invalid token payload")
            return False
    except JWTError:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return False
    return True


@router.websocket("/ws/{building_id}")
async def sensor_websocket(websocket: WebSocket, building_id: UUID):
    # Authenticate before accepting the connection
    if not await _authenticate_ws(websocket):
        return

    await websocket.accept()
    pubsub = redis_client.pubsub()
    channel = f"channel:building:{building_id}:telemetry"
    await pubsub.subscribe(channel)
    logger.info("WebSocket connected for building %s", building_id)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for building %s", building_id)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
