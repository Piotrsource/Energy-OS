"""
Redis-backed caching for latest sensor readings + pub/sub for WebSocket.
"""

import json
import logging
from uuid import UUID

import redis.asyncio as aioredis

from app.db.redis import redis_client

logger = logging.getLogger("energy_platform")

LATEST_KEY_PREFIX = "device:latest:"
CHANNEL_PREFIX = "channel:building:"
LATEST_TTL = 300  # 5 minutes


class RealtimeService:
    @staticmethod
    async def cache_reading(sensor_id: str, building_id: str, reading: dict) -> None:
        key = f"{LATEST_KEY_PREFIX}{sensor_id}"
        await redis_client.set(key, json.dumps(reading), ex=LATEST_TTL)

    @staticmethod
    async def publish_reading(building_id: str, reading: dict) -> None:
        channel = f"{CHANNEL_PREFIX}{building_id}:telemetry"
        await redis_client.publish(channel, json.dumps(reading))

    @staticmethod
    async def get_latest_readings(building_id: str) -> list[dict]:
        keys = []
        async for key in redis_client.scan_iter(f"{LATEST_KEY_PREFIX}*"):
            keys.append(key)

        if not keys:
            return []

        values = await redis_client.mget(keys)
        results = []
        for val in values:
            if val:
                data = json.loads(val)
                if data.get("building_id") == building_id:
                    results.append(data)
        return results

    @staticmethod
    async def get_device_health(building_id: str) -> list[dict]:
        from datetime import datetime, timezone
        readings = await RealtimeService.get_latest_readings(building_id)
        now = datetime.now(timezone.utc)
        health = []
        for r in readings:
            last_seen = datetime.fromisoformat(r["time"])
            delta = (now - last_seen).total_seconds()
            if delta < 300:
                status = "online"
            elif delta < 1800:
                status = "stale"
            else:
                status = "offline"
            health.append({
                "sensor_id": r["sensor_id"],
                "building_id": r["building_id"],
                "zone_id": r["zone_id"],
                "sensor_type": r["sensor_type"],
                "last_seen": r["time"],
                "last_value": r["value"],
                "status": status,
            })
        return health
