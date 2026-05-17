import pytest


def _get_rfp_agent():
    """Import rfp_agent, skip test if unavailable (missing Ollama/OpenAI config)."""
    try:
        from agents.rfp import rfp_agent

        return rfp_agent
    except Exception as e:
        pytest.skip(f"Cannot import rfp_agent: {e}")


@pytest.mark.integration
@pytest.mark.ollama
async def test_rfp_structured_output(require_stack, require_ollama):
    rfp_agent = _get_rfp_agent()
    result = await rfp_agent.run("Write an RFP response for a cloud migration project for a mid-size company")
    assert result.output is not None
    assert result.output.executive_summary != ""


@pytest.mark.integration
@pytest.mark.ollama
async def test_rfp_all_fields_populated(require_stack, require_ollama):
    rfp_agent = _get_rfp_agent()
    result = await rfp_agent.run("Write an RFP response for implementing a new CRM system")
    output = result.output
    assert output.executive_summary
    assert output.understanding
    assert output.approach
    assert output.timeline
    assert output.pricing_notes


@pytest.mark.integration
@pytest.mark.ollama
async def test_rfp_sections_list(require_stack, require_ollama):
    rfp_agent = _get_rfp_agent()
    result = await rfp_agent.run("Write an RFP response for a data analytics platform")
    assert isinstance(result.output.sections, list)
    assert len(result.output.sections) > 0
    for section in result.output.sections:
        assert section.title
        assert section.content
