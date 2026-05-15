import uuid

from chat.schemas import ChatRequest


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
