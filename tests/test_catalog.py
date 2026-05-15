from catalog.schemas import CapabilityCreate, ToolCreate


def test_capability_create_schema():
    data = CapabilityCreate(name="test-cap", description="A test capability", tags=["test"])
    assert data.name == "test-cap"
    assert data.tags == ["test"]
    assert data.agent_id is None


def test_tool_create_schema():
    data = ToolCreate(name="test-tool", provider="internal", tags=["dev"])
    assert data.name == "test-tool"
    assert data.provider == "internal"
