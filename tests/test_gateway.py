import uuid

import httpx
import pytest

# --- JWT Enforcement Tests ---


@pytest.mark.integration
async def test_gateway_healthz_no_auth(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.get(f"{gateway_url}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_agents_requires_auth(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.get(f"{gateway_url}/v1/agents/")
    assert resp.status_code == 401


@pytest.mark.integration
async def test_catalog_requires_auth(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.get(f"{gateway_url}/v1/catalog/capabilities")
    assert resp.status_code == 401


@pytest.mark.integration
async def test_chat_requires_auth(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.post(f"{gateway_url}/v1/chat", json={"message": "test"})
    assert resp.status_code == 401


@pytest.mark.integration
async def test_conversations_requires_auth(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.get(f"{gateway_url}/v1/conversations")
    assert resp.status_code == 401


@pytest.mark.integration
async def test_events_requires_auth(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.post(
        f"{gateway_url}/v1/events",
        json={"agent_id": str(uuid.uuid4()), "event_type": "test", "data": {}},
    )
    assert resp.status_code == 401


@pytest.mark.integration
async def test_invalid_token_rejected(http_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await http_client.get(
        f"{gateway_url}/v1/agents/",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


# --- Valid Token Access Tests ---


@pytest.mark.integration
async def test_agents_with_token(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.get(f"{gateway_url}/v1/agents/")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_catalog_capabilities_with_token(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.get(f"{gateway_url}/v1/catalog/capabilities")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_catalog_tools_with_token(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.get(f"{gateway_url}/v1/catalog/tools")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_conversations_with_token(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.get(f"{gateway_url}/v1/conversations", headers={"x-user-id": "gateway-test"})
    assert resp.status_code == 200


@pytest.mark.integration
async def test_catalog_search_with_token(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.get(f"{gateway_url}/v1/catalog/search?q=test")
    assert resp.status_code == 200


# --- Routing Correctness Tests ---


@pytest.mark.integration
async def test_create_agent_via_gateway(
    authed_client: httpx.AsyncClient, gateway_url: str, test_agent_data: dict, require_stack
):
    resp = await authed_client.post(f"{gateway_url}/v1/agents/", json=test_agent_data)
    assert resp.status_code == 201
    body = resp.json()
    agent_id = body["id"]
    assert body["name"] == test_agent_data["name"]
    assert body["status"] == "registered"

    await authed_client.delete(f"{gateway_url}/v1/agents/{agent_id}")


@pytest.mark.integration
async def test_create_capability_via_gateway(
    authed_client: httpx.AsyncClient, gateway_url: str, test_capability_data: dict, require_stack
):
    resp = await authed_client.post(f"{gateway_url}/v1/catalog/capabilities", json=test_capability_data)
    assert resp.status_code == 201
    cap_id = resp.json()["id"]

    await authed_client.delete(f"{gateway_url}/v1/catalog/capabilities/{cap_id}")


@pytest.mark.integration
async def test_create_tool_via_gateway(
    authed_client: httpx.AsyncClient, gateway_url: str, test_tool_data: dict, require_stack
):
    resp = await authed_client.post(f"{gateway_url}/v1/catalog/tools", json=test_tool_data)
    assert resp.status_code == 201
    tool_id = resp.json()["id"]

    await authed_client.delete(f"{gateway_url}/v1/catalog/tools/{tool_id}")


@pytest.mark.integration
async def test_post_event_via_gateway(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.post(
        f"{gateway_url}/v1/events",
        json={
            "agent_id": str(uuid.uuid4()),
            "event_type": "gateway_test",
            "data": {"routed": True},
        },
    )
    assert resp.status_code == 202


@pytest.mark.integration
async def test_post_traces_via_gateway(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    resp = await authed_client.post(
        f"{gateway_url}/v1/traces",
        json={"trace_id": "gw-trace-001", "spans": [{"name": "gw-span"}]},
    )
    assert resp.status_code == 202


@pytest.mark.integration
async def test_chat_via_gateway(authed_client: httpx.AsyncClient, gateway_url: str, auth_token: str, require_stack):
    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": "gateway-chat-test"}
    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{gateway_url}/v1/chat",
            json={"message": "Gateway routing test"},
            headers=headers,
        ) as resp,
    ):
        assert resp.status_code == 200
        lines = []
        async for line in resp.aiter_lines():
            lines.append(line)
        assert len(lines) > 0
