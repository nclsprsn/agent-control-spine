import json
from typing import Any

import nats
from nats.aio.client import Client as NATSClient


class NATSExporter:
    def __init__(self) -> None:
        self._nc: NATSClient | None = None

    async def connect(self, nats_url: str) -> None:
        self._nc = await nats.connect(nats_url)

    async def publish(self, subject: str, data: dict[str, Any]) -> None:
        if self._nc is None:
            return
        payload = json.dumps(data).encode()
        await self._nc.publish(subject, payload)

    async def close(self) -> None:
        if self._nc is not None:
            await self._nc.drain()
