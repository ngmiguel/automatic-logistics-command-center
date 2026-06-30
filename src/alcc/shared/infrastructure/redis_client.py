import json
from typing import Any

import redis.asyncio as aioredis

from alcc.config import get_settings

TELEMETRY_CHANNEL = "alcc:telemetry"
NOTIFICATION_CHANNEL = "alcc:notifications"
EVENTS_CHANNEL = "alcc:events"


class RedisClient:
    def __init__(self, url: str | None = None) -> None:
        self._url = url or get_settings().redis_url
        self._client: aioredis.Redis | None = None
        self._pubsub: aioredis.client.PubSub | None = None

    async def connect(self) -> None:
        self._client = aioredis.from_url(self._url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._pubsub:
            await self._pubsub.close()
        if self._client:
            await self._client.close()

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client not connected")
        return self._client

    async def publish(self, channel: str, data: dict[str, Any]) -> None:
        await self.client.publish(channel, json.dumps(data))

    async def publish_telemetry(self, data: dict[str, Any]) -> None:
        await self.publish(TELEMETRY_CHANNEL, data)
        await self.client.setex(
            f"telemetry:{data['vehicle_id']}",
            10,
            json.dumps(data),
        )

    async def get_telemetry(self, vehicle_id: str) -> dict[str, Any] | None:
        raw = await self.client.get(f"telemetry:{vehicle_id}")
        return json.loads(raw) if raw else None

    async def get_all_telemetry_keys(self) -> list[str]:
        keys = await self.client.keys("telemetry:*")
        return [k.replace("telemetry:", "") for k in keys]

    async def cache_set(self, key: str, value: str, ttl: int = 300) -> None:
        await self.client.setex(key, ttl, value)

    async def cache_get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def subscribe(self, *channels: str) -> aioredis.client.PubSub:
        self._pubsub = self.client.pubsub()
        await self._pubsub.subscribe(*channels)
        return self._pubsub


redis_client = RedisClient()
