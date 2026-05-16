import uuid

import httpx
import pytest
from catalog.schemas import CapabilityCreate, CapabilityUpdate, ToolCreate, ToolUpdate

# --- Unit Tests ---


def test_capability_create_schema():
    data = CapabilityCreate(name="test-cap", description="A test capability", tags=["test"])
    assert data.name == "test-cap"
    assert data.tags == ["test"]
    assert data.agent_id is None


def test_capability_create_defaults():
    data = CapabilityCreate(name="minimal")
    assert data.description is None
    assert data.tags == []
    assert data.input_schema is None
    assert data.output_schema is None


def test_capability_update_partial():
    data = CapabilityUpdate(description="updated")
    assert data.description == "updated"
    assert data.name is None
    assert data.tags is None


def test_tool_create_schema():
    data = ToolCreate(name="test-tool", provider="internal", tags=["dev"])
    assert data.name == "test-tool"
    assert data.provider == "internal"


def test_tool_create_defaults():
    data = ToolCreate(name="minimal-tool")
    assert data.provider is None
    assert data.tags == []
    assert data.input_schema is None


def test_tool_update_partial():
    data = ToolUpdate(provider="external")
    assert data.provider == "external"
    assert data.name is None
    assert data.tags is None


# --- Integration Tests: Capabilities ---


@pytest.mark.integration
async def test_create_capability(
    authed_client: httpx.AsyncClient, catalog_url: str, test_capability_data: dict, require_stack
):
    resp = await authed_client.post(f"{catalog_url}/v1/catalog/capabilities", json=test_capability_data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == test_capability_data["name"]
    assert body["tags"] == ["test", "integration"]
    assert body["id"] is not None

    await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{body['id']}")


@pytest.mark.integration
async def test_get_capability(
    authed_client: httpx.AsyncClient, catalog_url: str, test_capability_data: dict, require_stack
):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/capabilities", json=test_capability_data)
    cap_id = create.json()["id"]

    resp = await authed_client.get(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cap_id

    await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")


@pytest.mark.integration
async def test_get_capability_not_found(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/capabilities/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_list_capabilities(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/capabilities")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body


@pytest.mark.integration
async def test_list_capabilities_pagination(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/capabilities?page=1&page_size=2")
    assert resp.status_code == 200
    body = resp.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) <= 2


@pytest.mark.integration
async def test_list_capabilities_filter_tags(
    authed_client: httpx.AsyncClient, catalog_url: str, test_capability_data: dict, require_stack
):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/capabilities", json=test_capability_data)
    cap_id = create.json()["id"]

    resp = await authed_client.get(f"{catalog_url}/v1/catalog/capabilities?tags=integration")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(cap_id == item["id"] for item in items)

    await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")


@pytest.mark.integration
async def test_update_capability(
    authed_client: httpx.AsyncClient, catalog_url: str, test_capability_data: dict, require_stack
):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/capabilities", json=test_capability_data)
    cap_id = create.json()["id"]

    resp = await authed_client.patch(
        f"{catalog_url}/v1/catalog/capabilities/{cap_id}",
        json={"description": "Updated capability"},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated capability"

    await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")


@pytest.mark.integration
async def test_update_capability_not_found(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.patch(f"{catalog_url}/v1/catalog/capabilities/{uuid.uuid4()}", json={"name": "nope"})
    assert resp.status_code == 404


@pytest.mark.integration
async def test_delete_capability(
    authed_client: httpx.AsyncClient, catalog_url: str, test_capability_data: dict, require_stack
):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/capabilities", json=test_capability_data)
    cap_id = create.json()["id"]

    resp = await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")
    assert resp.status_code == 204

    get_resp = await authed_client.get(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")
    assert get_resp.status_code == 404


@pytest.mark.integration
async def test_delete_capability_not_found(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{uuid.uuid4()}")
    assert resp.status_code == 404


# --- Integration Tests: Tools ---


@pytest.mark.integration
async def test_create_tool(authed_client: httpx.AsyncClient, catalog_url: str, test_tool_data: dict, require_stack):
    resp = await authed_client.post(f"{catalog_url}/v1/catalog/tools", json=test_tool_data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == test_tool_data["name"]
    assert body["provider"] == "test-provider"

    await authed_client.delete(f"{catalog_url}/v1/catalog/tools/{body['id']}")


@pytest.mark.integration
async def test_get_tool(authed_client: httpx.AsyncClient, catalog_url: str, test_tool_data: dict, require_stack):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/tools", json=test_tool_data)
    tool_id = create.json()["id"]

    resp = await authed_client.get(f"{catalog_url}/v1/catalog/tools/{tool_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == tool_id

    await authed_client.delete(f"{catalog_url}/v1/catalog/tools/{tool_id}")


@pytest.mark.integration
async def test_get_tool_not_found(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/tools/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_list_tools(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/tools")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body


@pytest.mark.integration
async def test_update_tool(authed_client: httpx.AsyncClient, catalog_url: str, test_tool_data: dict, require_stack):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/tools", json=test_tool_data)
    tool_id = create.json()["id"]

    resp = await authed_client.patch(
        f"{catalog_url}/v1/catalog/tools/{tool_id}",
        json={"description": "Updated tool"},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated tool"

    await authed_client.delete(f"{catalog_url}/v1/catalog/tools/{tool_id}")


@pytest.mark.integration
async def test_delete_tool(authed_client: httpx.AsyncClient, catalog_url: str, test_tool_data: dict, require_stack):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/tools", json=test_tool_data)
    tool_id = create.json()["id"]

    resp = await authed_client.delete(f"{catalog_url}/v1/catalog/tools/{tool_id}")
    assert resp.status_code == 204

    get_resp = await authed_client.get(f"{catalog_url}/v1/catalog/tools/{tool_id}")
    assert get_resp.status_code == 404


@pytest.mark.integration
async def test_delete_tool_not_found(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.delete(f"{catalog_url}/v1/catalog/tools/{uuid.uuid4()}")
    assert resp.status_code == 404


# --- Integration Tests: Search ---


@pytest.mark.integration
async def test_search_by_name(
    authed_client: httpx.AsyncClient, catalog_url: str, test_capability_data: dict, require_stack
):
    create = await authed_client.post(f"{catalog_url}/v1/catalog/capabilities", json=test_capability_data)
    cap_id = create.json()["id"]
    name = test_capability_data["name"]

    resp = await authed_client.get(f"{catalog_url}/v1/catalog/search?q={name}")
    assert resp.status_code == 200
    body = resp.json()
    assert "capabilities" in body
    assert "tools" in body

    await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{cap_id}")


@pytest.mark.integration
async def test_search_no_results(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/search?q=zzz_nonexistent_zzz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["capabilities"] == []
    assert body["tools"] == []


@pytest.mark.integration
async def test_search_requires_query(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await authed_client.get(f"{catalog_url}/v1/catalog/search")
    assert resp.status_code == 422


@pytest.mark.integration
async def test_search_ranks_name_above_description(authed_client: httpx.AsyncClient, catalog_url: str, require_stack):
    suffix = uuid.uuid4().hex[:8]
    term = f"vorpalblade{suffix}"
    name_match = await authed_client.post(
        f"{catalog_url}/v1/catalog/capabilities",
        json={"name": f"{term}-cap", "description": "unrelated text", "tags": []},
    )
    desc_match = await authed_client.post(
        f"{catalog_url}/v1/catalog/capabilities",
        json={"name": f"other-cap-{suffix}", "description": f"contains {term} inside", "tags": []},
    )
    name_id = name_match.json()["id"]
    desc_id = desc_match.json()["id"]

    try:
        resp = await authed_client.get(f"{catalog_url}/v1/catalog/search?q={term}")
        assert resp.status_code == 200
        items = resp.json()["capabilities"]
        ids = [c["id"] for c in items]
        assert name_id in ids and desc_id in ids
        assert ids.index(name_id) < ids.index(desc_id)
    finally:
        await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{name_id}")
        await authed_client.delete(f"{catalog_url}/v1/catalog/capabilities/{desc_id}")


# --- Health ---


@pytest.mark.integration
async def test_catalog_healthz(http_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await http_client.get(f"{catalog_url}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_catalog_readyz(http_client: httpx.AsyncClient, catalog_url: str, require_stack):
    resp = await http_client.get(f"{catalog_url}/readyz")
    assert resp.status_code == 200
