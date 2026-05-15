import json
import uuid
from collections.abc import AsyncIterator

import httpx


class AgentOrchestrator:
    def __init__(self, registry_url: str, catalog_url: str) -> None:
        self.registry_url = registry_url
        self.catalog_url = catalog_url
        self._http = httpx.AsyncClient(timeout=30.0)

    async def get_agent_info(self, agent_id: uuid.UUID) -> dict | None:
        try:
            resp = await self._http.get(f"{self.registry_url}/v1/agents/{agent_id}")
            if resp.status_code == 200:
                return resp.json()
        except httpx.HTTPError:
            pass
        return None

    async def stream_response(
        self, agent_id: uuid.UUID, message: str, history: list[dict]
    ) -> AsyncIterator[dict]:
        agent_info = await self.get_agent_info(agent_id)
        agent_name = agent_info["name"] if agent_info else "Unknown Agent"

        yield {
            "type": "text_delta",
            "content": f"[{agent_name}] Received your message: {message}\n\n",
        }
        yield {
            "type": "text_delta",
            "content": "This is a placeholder response. Connect a real LLM provider via AgentGateway to get actual agent responses.",
        }

        yield {
            "type": "done",
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "usage": None,
        }

    async def close(self) -> None:
        await self._http.aclose()
