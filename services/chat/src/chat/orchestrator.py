import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

import httpx

from chat.langfuse_integration import create_trace


class AgentOrchestrator:
    def __init__(self, registry_url: str, catalog_url: str, ollama_url: str, model: str) -> None:
        self.registry_url = registry_url
        self.catalog_url = catalog_url
        self.ollama_url = ollama_url
        self.model = model
        self._http = httpx.AsyncClient(timeout=30.0)

    async def get_agent_info(self, agent_id: uuid.UUID) -> dict[str, Any] | None:
        try:
            resp = await self._http.get(f"{self.registry_url}/v1/agents/{agent_id}")
            if resp.status_code == 200:
                return resp.json()  # type: ignore[no-any-return]
        except httpx.HTTPError:
            return None
        return None

    async def stream_response(
        self, agent_id: uuid.UUID, message: str, history: list[dict[str, Any]]
    ) -> AsyncIterator[dict[str, Any]]:
        agent_info = await self.get_agent_info(agent_id)
        agent_name = agent_info["name"] if agent_info else "Assistant"

        trace = create_trace(
            name="chat",
            metadata={"agent_id": str(agent_id), "agent_name": agent_name},
            tags=["chat", "stream"],
        )

        generation = None
        if trace is not None:
            generation = trace.generation(
                name="llm-call",
                model=self.model,
                input={"message": message, "history_len": len(history)},
            )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": f"You are {agent_name}, a helpful AI assistant."},
        ]
        messages.extend({"role": m["role"], "content": m["content"]} for m in history)
        messages.append({"role": "user", "content": message})

        full_content = ""
        full_reasoning = ""
        async with self._http.stream(
            "POST",
            f"{self.ollama_url}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "stream": True,
                "enable_thinking": True,
            },
            timeout=120.0,
        ) as resp:
            if resp.status_code != 200:
                error_text = f"LLM error: {resp.status_code}"
                yield {"type": "text_delta", "content": error_text}
                full_content = error_text
            else:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]
                        if reasoning := delta.get("reasoning"):
                            full_reasoning += reasoning
                            yield {"type": "thinking_delta", "content": reasoning}
                        if content := delta.get("content"):
                            full_content += content
                            yield {"type": "text_delta", "content": content}
                    except json.JSONDecodeError, KeyError, IndexError:
                        continue

        if generation is not None:
            generation.end(output={"response": full_content, "reasoning": full_reasoning})
        if trace is not None:
            trace.update(output={"response": full_content})

        yield {
            "type": "done",
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "usage": None,
        }

    async def close(self) -> None:
        await self._http.aclose()
