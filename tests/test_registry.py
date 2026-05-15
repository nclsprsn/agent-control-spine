from registry.schemas import AgentCreate, AgentResponse


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
