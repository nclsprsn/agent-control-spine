import uuid

import httpx
import pytest


@pytest.mark.integration
async def test_agent_full_lifecycle(
    authed_client: httpx.AsyncClient, gateway_url: str, test_agent_data: dict, require_stack
):
    create = await authed_client.post(f"{gateway_url}/v1/agents/", json=test_agent_data)
    assert create.status_code == 201
    agent_id = create.json()["id"]

    list_resp = await authed_client.get(f"{gateway_url}/v1/agents/")
    assert any(a["id"] == agent_id for a in list_resp.json()["items"])

    hb = await authed_client.post(f"{gateway_url}/v1/agents/{agent_id}/heartbeat")
    assert hb.status_code == 200
    assert hb.json()["status"] == "active"

    update = await authed_client.patch(f"{gateway_url}/v1/agents/{agent_id}", json={"version": "2.0.0"})
    assert update.status_code == 200
    assert update.json()["version"] == "2.0.0"

    delete = await authed_client.delete(f"{gateway_url}/v1/agents/{agent_id}")
    assert delete.status_code == 204

    get_after = await authed_client.get(f"{gateway_url}/v1/agents/{agent_id}")
    assert get_after.status_code == 404


@pytest.mark.integration
async def test_catalog_capability_workflow(
    authed_client: httpx.AsyncClient, gateway_url: str, test_capability_data: dict, require_stack
):
    create = await authed_client.post(f"{gateway_url}/v1/catalog/capabilities", json=test_capability_data)
    assert create.status_code == 201
    cap_id = create.json()["id"]

    search = await authed_client.get(f"{gateway_url}/v1/catalog/search?q={test_capability_data['name']}")
    assert search.status_code == 200

    update = await authed_client.patch(
        f"{gateway_url}/v1/catalog/capabilities/{cap_id}",
        json={"description": "E2E updated"},
    )
    assert update.status_code == 200

    delete = await authed_client.delete(f"{gateway_url}/v1/catalog/capabilities/{cap_id}")
    assert delete.status_code == 204


@pytest.mark.integration
async def test_chat_conversation_flow(
    authed_client: httpx.AsyncClient, gateway_url: str, auth_token: str, require_stack
):
    user_id = f"e2e-user-{uuid.uuid4().hex[:8]}"
    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_id}

    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{gateway_url}/v1/chat",
            json={"message": "E2E test message"},
            headers=headers,
        ) as resp,
    ):
        assert resp.status_code == 200
        async for _ in resp.aiter_lines():
            pass

    convs = await authed_client.get(f"{gateway_url}/v1/conversations", headers={"x-user-id": user_id})
    assert convs.status_code == 200
    items = convs.json()["items"]
    assert len(items) >= 1
    conv_id = items[0]["id"]

    detail = await authed_client.get(f"{gateway_url}/v1/conversations/{conv_id}")
    assert detail.status_code == 200
    assert len(detail.json()["messages"]) >= 1

    delete = await authed_client.delete(f"{gateway_url}/v1/conversations/{conv_id}")
    assert delete.status_code == 204


@pytest.mark.integration
async def test_cross_service_integration(
    authed_client: httpx.AsyncClient, gateway_url: str, test_agent_data: dict, require_stack
):
    agent = await authed_client.post(f"{gateway_url}/v1/agents/", json=test_agent_data)
    assert agent.status_code == 201
    agent_id = agent.json()["id"]

    cap_data = {
        "name": f"cap-for-{test_agent_data['name']}",
        "description": "Cross-service test",
        "agent_id": agent_id,
        "tags": ["e2e"],
    }
    cap = await authed_client.post(f"{gateway_url}/v1/catalog/capabilities", json=cap_data)
    assert cap.status_code == 201
    cap_id = cap.json()["id"]

    event_resp = await authed_client.post(
        f"{gateway_url}/v1/events",
        json={
            "agent_id": agent_id,
            "event_type": "capability_registered",
            "data": {"capability_id": cap_id},
        },
    )
    assert event_resp.status_code == 202

    await authed_client.delete(f"{gateway_url}/v1/catalog/capabilities/{cap_id}")
    await authed_client.delete(f"{gateway_url}/v1/agents/{agent_id}")


@pytest.mark.integration
async def test_dashboard_data_contract(authed_client: httpx.AsyncClient, gateway_url: str, require_stack):
    agents = await authed_client.get(f"{gateway_url}/v1/agents/")
    assert agents.status_code == 200
    body = agents.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body

    caps = await authed_client.get(f"{gateway_url}/v1/catalog/capabilities")
    assert caps.status_code == 200
    assert "items" in caps.json()

    tools = await authed_client.get(f"{gateway_url}/v1/catalog/tools")
    assert tools.status_code == 200
    assert "items" in tools.json()


@pytest.mark.integration
async def test_observability_event_flow(
    authed_client: httpx.AsyncClient, gateway_url: str, test_agent_data: dict, require_stack
):
    agent = await authed_client.post(f"{gateway_url}/v1/agents/", json=test_agent_data)
    agent_id = agent.json()["id"]

    await authed_client.post(f"{gateway_url}/v1/agents/{agent_id}/heartbeat")

    event = await authed_client.post(
        f"{gateway_url}/v1/events",
        json={
            "agent_id": agent_id,
            "event_type": "heartbeat",
            "data": {"status": "active"},
        },
    )
    assert event.status_code == 202

    trace = await authed_client.post(
        f"{gateway_url}/v1/traces",
        json={
            "trace_id": f"trace-{uuid.uuid4().hex[:8]}",
            "spans": [{"name": "heartbeat_handler", "duration_ms": 5}],
        },
    )
    assert trace.status_code == 202

    await authed_client.delete(f"{gateway_url}/v1/agents/{agent_id}")
