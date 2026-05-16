import uuid

import httpx
import pytest
from registry.models import AgentStatus
from registry.schemas import AgentCreate, AgentResponse, AgentUpdate

# --- Unit Tests ---


def test_agent_create_schema():
    data = AgentCreate(name="test-agent", version="1.0.0", owner="test-team")
    assert data.name == "test-agent"
    assert data.version == "1.0.0"
    assert data.owner == "test-team"
    assert data.metadata is None


def test_agent_create_with_metadata():
    data = AgentCreate(
        name="test-agent",
        version="1.0.0",
        owner="test-team",
        metadata={"key": "value"},
        endpoint_url="http://example.com",
    )
    assert data.metadata == {"key": "value"}
    assert data.endpoint_url == "http://example.com"


def test_agent_update_partial():
    data = AgentUpdate(version="2.0.0")
    assert data.version == "2.0.0"
    assert data.name is None
    assert data.status is None


def test_agent_status_values():
    assert AgentStatus.REGISTERED == "registered"
    assert AgentStatus.ACTIVE == "active"
    assert AgentStatus.SUSPENDED == "suspended"
    assert AgentStatus.DEPRECATED == "deprecated"
    assert AgentStatus.TERMINATED == "terminated"


def test_agent_response_from_attributes():
    data = {
        "id": uuid.uuid4(),
        "name": "test",
        "version": "1.0.0",
        "status": AgentStatus.REGISTERED,
        "description": None,
        "owner": "team",
        "endpoint_url": None,
        "auth_config": None,
        "metadata_": {"key": "val"},
        "last_heartbeat_at": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": None,
        "created_by": None,
    }
    resp = AgentResponse.model_validate(data, from_attributes=True)
    assert resp.metadata == {"key": "val"}


def test_agent_update_with_status():
    data = AgentUpdate(status=AgentStatus.SUSPENDED)
    assert data.status == AgentStatus.SUSPENDED


def test_agent_create_all_fields():
    data = AgentCreate(
        name="full-agent",
        version="3.0.0",
        owner="ops",
        description="Full spec",
        endpoint_url="http://agent.internal:9000",
        auth_config={"type": "bearer", "token": "xxx"},
        metadata={"env": "staging"},
    )
    assert data.auth_config == {"type": "bearer", "token": "xxx"}
    assert data.description == "Full spec"


# --- Integration Tests ---


@pytest.mark.integration
async def test_create_agent(authed_client: httpx.AsyncClient, registry_url: str, test_agent_data: dict, require_stack):
    resp = await authed_client.post(f"{registry_url}/v1/agents/", json=test_agent_data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == test_agent_data["name"]
    assert body["status"] == "registered"
    assert body["id"] is not None

    await authed_client.delete(f"{registry_url}/v1/agents/{body['id']}")


@pytest.mark.integration
async def test_get_agent(authed_client: httpx.AsyncClient, registry_url: str, test_agent_data: dict, require_stack):
    create = await authed_client.post(f"{registry_url}/v1/agents/", json=test_agent_data)
    agent_id = create.json()["id"]

    resp = await authed_client.get(f"{registry_url}/v1/agents/{agent_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == agent_id

    await authed_client.delete(f"{registry_url}/v1/agents/{agent_id}")


@pytest.mark.integration
async def test_get_agent_not_found(authed_client: httpx.AsyncClient, registry_url: str, require_stack):
    fake_id = uuid.uuid4()
    resp = await authed_client.get(f"{registry_url}/v1/agents/{fake_id}")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_list_agents(authed_client: httpx.AsyncClient, registry_url: str, require_stack):
    resp = await authed_client.get(f"{registry_url}/v1/agents/")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body


@pytest.mark.integration
async def test_list_agents_pagination(authed_client: httpx.AsyncClient, registry_url: str, require_stack):
    resp = await authed_client.get(f"{registry_url}/v1/agents/?page=1&page_size=2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) <= 2


@pytest.mark.integration
async def test_list_agents_filter_status(
    authed_client: httpx.AsyncClient, registry_url: str, test_agent_data: dict, require_stack
):
    create = await authed_client.post(f"{registry_url}/v1/agents/", json=test_agent_data)
    agent_id = create.json()["id"]

    resp = await authed_client.get(f"{registry_url}/v1/agents/?status=registered")
    assert resp.status_code == 200
    items = resp.json()["items"]
    for item in items:
        assert item["status"] == "registered"

    await authed_client.delete(f"{registry_url}/v1/agents/{agent_id}")


@pytest.mark.integration
async def test_update_agent(authed_client: httpx.AsyncClient, registry_url: str, test_agent_data: dict, require_stack):
    create = await authed_client.post(f"{registry_url}/v1/agents/", json=test_agent_data)
    agent_id = create.json()["id"]

    resp = await authed_client.patch(
        f"{registry_url}/v1/agents/{agent_id}",
        json={"description": "Updated description", "version": "2.0.0"},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"
    assert resp.json()["version"] == "2.0.0"

    await authed_client.delete(f"{registry_url}/v1/agents/{agent_id}")


@pytest.mark.integration
async def test_update_agent_not_found(authed_client: httpx.AsyncClient, registry_url: str, require_stack):
    fake_id = uuid.uuid4()
    resp = await authed_client.patch(f"{registry_url}/v1/agents/{fake_id}", json={"version": "9.9.9"})
    assert resp.status_code == 404


@pytest.mark.integration
async def test_delete_agent(authed_client: httpx.AsyncClient, registry_url: str, test_agent_data: dict, require_stack):
    create = await authed_client.post(f"{registry_url}/v1/agents/", json=test_agent_data)
    agent_id = create.json()["id"]

    resp = await authed_client.delete(f"{registry_url}/v1/agents/{agent_id}")
    assert resp.status_code == 204

    get_resp = await authed_client.get(f"{registry_url}/v1/agents/{agent_id}")
    assert get_resp.status_code == 404


@pytest.mark.integration
async def test_delete_agent_not_found(authed_client: httpx.AsyncClient, registry_url: str, require_stack):
    fake_id = uuid.uuid4()
    resp = await authed_client.delete(f"{registry_url}/v1/agents/{fake_id}")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_heartbeat(authed_client: httpx.AsyncClient, registry_url: str, test_agent_data: dict, require_stack):
    create = await authed_client.post(f"{registry_url}/v1/agents/", json=test_agent_data)
    agent_id = create.json()["id"]

    resp = await authed_client.post(f"{registry_url}/v1/agents/{agent_id}/heartbeat")
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"
    assert resp.json()["last_heartbeat_at"] is not None

    await authed_client.delete(f"{registry_url}/v1/agents/{agent_id}")


@pytest.mark.integration
async def test_heartbeat_not_found(authed_client: httpx.AsyncClient, registry_url: str, require_stack):
    fake_id = uuid.uuid4()
    resp = await authed_client.post(f"{registry_url}/v1/agents/{fake_id}/heartbeat")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_healthz(http_client: httpx.AsyncClient, registry_url: str, require_stack):
    resp = await http_client.get(f"{registry_url}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_readyz(http_client: httpx.AsyncClient, registry_url: str, require_stack):
    resp = await http_client.get(f"{registry_url}/readyz")
    assert resp.status_code == 200
