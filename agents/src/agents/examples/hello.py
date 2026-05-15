"""Example Pydantic AI agent demonstrating tool use and structured output."""

from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent


class GreetingResponse(BaseModel):
    message: str
    timestamp: str
    tools_used: list[str]


hello_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=GreetingResponse,
    system_prompt="You are a friendly greeting agent. Always use the current_time tool to include the time in your greeting.",
)


@hello_agent.tool_plain
def current_time() -> str:
    """Get the current UTC time."""
    return datetime.utcnow().isoformat()


@hello_agent.tool_plain
def reverse_text(text: str) -> str:
    """Reverse a given text string."""
    return text[::-1]


async def main() -> None:
    result = await hello_agent.run("Say hello and tell me the time!")
    print(f"Message: {result.output.message}")
    print(f"Time: {result.output.timestamp}")
    print(f"Tools: {result.output.tools_used}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
