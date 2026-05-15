import pytest


@pytest.mark.integration
async def test_agent_lifecycle():
    """Full agent lifecycle: register -> list -> heartbeat -> deregister.

    Requires running stack (make dev). Run with: make test-int
    """
    pytest.skip("Requires running stack")
