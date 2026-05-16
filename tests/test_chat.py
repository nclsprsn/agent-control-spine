import uuid

import httpx
import pytest
from chat.models import MessageRole
from chat.schemas import ChatRequest, DoneEvent, TextDeltaEvent

# --- Unit Tests ---


def test_chat_request_schema():
    agent_id = uuid.uuid4()
    data = ChatRequest(agent_id=agent_id, message="Hello agent")
    assert data.agent_id == agent_id
    assert data.message == "Hello agent"
    assert data.conversation_id is None


def test_chat_request_with_conversation():
    agent_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    data = ChatRequest(agent_id=agent_id, message="Follow up", conversation_id=conv_id)
    assert data.conversation_id == conv_id


def test_text_delta_event():
    event = TextDeltaEvent(content="Hello")
    assert event.type == "text_delta"
    assert event.content == "Hello"


def test_done_event():
    conv_id = uuid.uuid4()
    msg_id = uuid.uuid4()
    event = DoneEvent(conversation_id=conv_id, message_id=msg_id)
    assert event.type == "done"
    assert event.conversation_id == conv_id


def test_message_role_values():
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
    assert MessageRole.TOOL == "tool"


# --- Integration Tests ---


@pytest.mark.integration
async def test_chat_sse_stream(authed_client: httpx.AsyncClient, chat_url: str, require_stack):
    async with authed_client.stream(
        "POST",
        f"{chat_url}/v1/chat",
        json={"message": "Say hello in one word"},
        headers={"x-user-id": "test-user-sse"},
    ) as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")
        events = []
        async for line in resp.aiter_lines():
            line = line.strip()
            if line.startswith("data:"):
                events.append(line[5:].strip())
        assert len(events) > 0


@pytest.mark.integration
async def test_chat_creates_conversation(
    authed_client: httpx.AsyncClient, chat_url: str, auth_token: str, require_stack
):
    user_id = f"test-user-{uuid.uuid4().hex[:8]}"
    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_id}
    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{chat_url}/v1/chat",
            json={"message": "Hello"},
            headers=headers,
        ) as resp,
    ):
        async for _ in resp.aiter_lines():
            pass

    convs = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": user_id})
    assert convs.status_code == 200
    items = convs.json()["items"]
    assert len(items) >= 1

    for conv in items:
        await authed_client.delete(f"{chat_url}/v1/conversations/{conv['id']}", headers={"x-user-id": user_id})


@pytest.mark.integration
async def test_list_conversations(authed_client: httpx.AsyncClient, chat_url: str, require_stack):
    resp = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": "test-list-user"})
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body


@pytest.mark.integration
async def test_list_conversations_pagination(
    authed_client: httpx.AsyncClient, chat_url: str, auth_token: str, require_stack
):
    user_id = f"page-user-{uuid.uuid4().hex[:8]}"
    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_id}
    for body in ("one", "two", "three"):
        async with (
            httpx.AsyncClient(timeout=30.0) as stream_client,
            stream_client.stream("POST", f"{chat_url}/v1/chat", json={"message": body}, headers=headers) as resp,
        ):
            async for _ in resp.aiter_lines():
                pass

    page1 = await authed_client.get(f"{chat_url}/v1/conversations?page=1&page_size=2", headers={"x-user-id": user_id})
    body1 = page1.json()
    assert body1["page"] == 1
    assert body1["page_size"] == 2
    assert len(body1["items"]) == 2
    assert body1["total"] >= 3

    page2 = await authed_client.get(f"{chat_url}/v1/conversations?page=2&page_size=2", headers={"x-user-id": user_id})
    body2 = page2.json()
    assert body2["page"] == 2
    assert len(body2["items"]) >= 1

    page1_ids = {c["id"] for c in body1["items"]}
    page2_ids = {c["id"] for c in body2["items"]}
    assert page1_ids.isdisjoint(page2_ids)

    for conv in body1["items"] + body2["items"]:
        await authed_client.delete(f"{chat_url}/v1/conversations/{conv['id']}", headers={"x-user-id": user_id})


@pytest.mark.integration
async def test_list_conversations_user_isolation(
    authed_client: httpx.AsyncClient, chat_url: str, auth_token: str, require_stack
):
    user_a = f"user-a-{uuid.uuid4().hex[:8]}"
    user_b = f"user-b-{uuid.uuid4().hex[:8]}"

    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_a}
    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{chat_url}/v1/chat",
            json={"message": "Hello from A"},
            headers=headers,
        ) as resp,
    ):
        async for _ in resp.aiter_lines():
            pass

    convs_b = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": user_b})
    assert convs_b.json()["total"] == 0

    convs_a = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": user_a})
    for conv in convs_a.json()["items"]:
        await authed_client.delete(f"{chat_url}/v1/conversations/{conv['id']}", headers={"x-user-id": user_a})


@pytest.mark.integration
async def test_get_conversation_detail(authed_client: httpx.AsyncClient, chat_url: str, auth_token: str, require_stack):
    user_id = f"test-detail-{uuid.uuid4().hex[:8]}"
    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_id}
    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{chat_url}/v1/chat",
            json={"message": "Detail test"},
            headers=headers,
        ) as resp,
    ):
        async for _ in resp.aiter_lines():
            pass

    convs = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": user_id})
    conv_id = convs.json()["items"][0]["id"]

    detail = await authed_client.get(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_id})
    assert detail.status_code == 200
    assert "messages" in detail.json()
    assert len(detail.json()["messages"]) >= 1

    await authed_client.delete(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_id})


@pytest.mark.integration
async def test_get_conversation_not_found(authed_client: httpx.AsyncClient, chat_url: str, require_stack):
    resp = await authed_client.get(f"{chat_url}/v1/conversations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_delete_conversation(authed_client: httpx.AsyncClient, chat_url: str, auth_token: str, require_stack):
    user_id = f"test-delete-{uuid.uuid4().hex[:8]}"
    headers = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_id}
    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{chat_url}/v1/chat",
            json={"message": "Delete me"},
            headers=headers,
        ) as resp,
    ):
        async for _ in resp.aiter_lines():
            pass

    convs = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": user_id})
    conv_id = convs.json()["items"][0]["id"]

    del_resp = await authed_client.delete(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_id})
    assert del_resp.status_code == 204

    get_resp = await authed_client.get(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_id})
    assert get_resp.status_code == 404


@pytest.mark.integration
async def test_delete_conversation_not_found(authed_client: httpx.AsyncClient, chat_url: str, require_stack):
    resp = await authed_client.delete(f"{chat_url}/v1/conversations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.integration
async def test_conversation_ownership_enforced(
    authed_client: httpx.AsyncClient, chat_url: str, auth_token: str, require_stack
):
    user_a = f"owner-a-{uuid.uuid4().hex[:8]}"
    user_b = f"owner-b-{uuid.uuid4().hex[:8]}"

    headers_a = {"Authorization": f"Bearer {auth_token}", "x-user-id": user_a}
    async with (
        httpx.AsyncClient(timeout=30.0) as stream_client,
        stream_client.stream(
            "POST",
            f"{chat_url}/v1/chat",
            json={"message": "owner-only"},
            headers=headers_a,
        ) as resp,
    ):
        async for _ in resp.aiter_lines():
            pass

    convs_a = await authed_client.get(f"{chat_url}/v1/conversations", headers={"x-user-id": user_a})
    conv_id = convs_a.json()["items"][0]["id"]

    get_b = await authed_client.get(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_b})
    assert get_b.status_code == 404

    del_b = await authed_client.delete(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_b})
    assert del_b.status_code == 404

    still_there = await authed_client.get(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_a})
    assert still_there.status_code == 200

    await authed_client.delete(f"{chat_url}/v1/conversations/{conv_id}", headers={"x-user-id": user_a})


@pytest.mark.integration
async def test_chat_healthz(http_client: httpx.AsyncClient, chat_url: str, require_stack):
    resp = await http_client.get(f"{chat_url}/healthz")
    assert resp.status_code == 200


@pytest.mark.integration
async def test_chat_readyz(http_client: httpx.AsyncClient, chat_url: str, require_stack):
    resp = await http_client.get(f"{chat_url}/readyz")
    assert resp.status_code == 200
