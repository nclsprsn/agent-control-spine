import uuid

import pytest
from chat.models import MessageRole
from chat.service import ConversationService


@pytest.mark.asyncio
async def test_get_returns_conversation_when_user_matches(db_session):
    svc = ConversationService(db_session)
    conv = await svc.create(user_id="alice", agent_id=uuid.uuid4(), title="hi")
    await db_session.commit()

    fetched = await svc.get(conv.id, user_id="alice")
    assert fetched is not None
    assert fetched.id == conv.id


@pytest.mark.asyncio
async def test_get_returns_none_when_user_mismatch(db_session):
    svc = ConversationService(db_session)
    conv = await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await db_session.commit()

    assert await svc.get(conv.id, user_id="mallory") is None


@pytest.mark.asyncio
async def test_get_without_user_filter_returns_any(db_session):
    svc = ConversationService(db_session)
    conv = await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await db_session.commit()

    assert await svc.get(conv.id) is not None


@pytest.mark.asyncio
async def test_delete_refuses_other_user(db_session):
    svc = ConversationService(db_session)
    conv = await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await db_session.commit()

    deleted = await svc.delete(conv.id, user_id="mallory")
    assert deleted is False
    assert await svc.get(conv.id) is not None


@pytest.mark.asyncio
async def test_delete_succeeds_for_owner(db_session):
    svc = ConversationService(db_session)
    conv = await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await db_session.commit()

    assert await svc.delete(conv.id, user_id="alice") is True
    await db_session.commit()
    assert await svc.get(conv.id) is None


@pytest.mark.asyncio
async def test_delete_returns_false_for_missing_id(db_session):
    svc = ConversationService(db_session)
    assert await svc.delete(uuid.uuid4(), user_id="alice") is False


@pytest.mark.asyncio
async def test_list_for_user_is_isolated(db_session):
    svc = ConversationService(db_session)
    await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await svc.create(user_id="bob", agent_id=uuid.uuid4())
    await db_session.commit()

    rows, total_a = await svc.list_for_user("alice")
    assert total_a == 2
    assert len(rows) == 2

    rows_b, total_b = await svc.list_for_user("bob")
    assert total_b == 1
    assert len(rows_b) == 1


@pytest.mark.asyncio
async def test_list_includes_message_count(db_session):
    svc = ConversationService(db_session)
    conv = await svc.create(user_id="alice", agent_id=uuid.uuid4())
    await svc.add_message(conv.id, MessageRole.USER, "hi")
    await svc.add_message(conv.id, MessageRole.ASSISTANT, "hello")
    await db_session.commit()

    rows, _ = await svc.list_for_user("alice")
    assert rows[0][1] == 2
