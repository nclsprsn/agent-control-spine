import json
import uuid
from collections.abc import AsyncIterator

import httpx
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def gateway_url():
    return "http://localhost:8080"


@pytest.fixture(scope="session")
def registry_url():
    return "http://localhost:8081"


@pytest.fixture(scope="session")
def catalog_url():
    return "http://localhost:8082"


@pytest.fixture(scope="session")
def observer_url():
    return "http://localhost:8083"


@pytest.fixture(scope="session")
def chat_url():
    return "http://localhost:8084"


@pytest.fixture(scope="session")
def keycloak_url():
    return "http://localhost:8443"


@pytest.fixture(scope="session")
async def auth_token(keycloak_url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{keycloak_url}/realms/spine/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "spine-services",
                "client_secret": "change-me-in-production",
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


@pytest.fixture
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
async def authed_client(auth_token: str) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        timeout=30.0,
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def require_stack(registry_url: str):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{registry_url}/healthz", timeout=3.0)
            if resp.status_code != 200:
                pytest.skip("Docker stack not running")
    except httpx.ConnectError, httpx.TimeoutException:
        pytest.skip("Docker stack not running")


@pytest.fixture(scope="session")
async def require_ollama():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434/api/tags", timeout=3.0)
            if resp.status_code != 200:
                pytest.skip("Ollama not running")
    except httpx.ConnectError, httpx.TimeoutException:
        pytest.skip("Ollama not running")


@pytest.fixture
def test_agent_data() -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"test-agent-{suffix}",
        "version": "1.0.0",
        "owner": "test-team",
        "description": "Integration test agent",
        "metadata": {"test": True},
    }


@pytest.fixture
def test_capability_data() -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"test-cap-{suffix}",
        "description": "Integration test capability",
        "tags": ["test", "integration"],
        "input_schema": {"type": "object", "properties": {"input": {"type": "string"}}},
    }


@pytest.fixture
def test_tool_data() -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"test-tool-{suffix}",
        "description": "Integration test tool",
        "provider": "test-provider",
        "tags": ["test", "integration"],
    }


async def collect_sse_events(resp: httpx.Response) -> list[dict]:
    events = []
    async for line in resp.aiter_lines():
        line = line.strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if data:
                events.append(json.loads(data))
    return events
