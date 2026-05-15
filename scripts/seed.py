"""Seed database with sample agents, capabilities, and tools."""

import asyncio
import httpx

REGISTRY_URL = "http://localhost:8081"
CATALOG_URL = "http://localhost:8082"

SAMPLE_AGENTS = [
    {
        "name": "code-reviewer",
        "version": "1.0.0",
        "description": "Reviews code for quality, security, and best practices",
        "owner": "platform-team",
        "endpoint_url": "http://localhost:9001",
        "metadata": {"language": "python", "category": "development"},
    },
    {
        "name": "data-analyst",
        "version": "1.0.0",
        "description": "Analyzes datasets and generates insights",
        "owner": "data-team",
        "endpoint_url": "http://localhost:9002",
        "metadata": {"category": "analytics"},
    },
    {
        "name": "support-bot",
        "version": "2.1.0",
        "description": "Handles customer support queries with knowledge base lookup",
        "owner": "support-team",
        "metadata": {"category": "support", "tier": "L1"},
    },
]

SAMPLE_CAPABILITIES = [
    {
        "name": "code-review",
        "description": "Review code for quality and security issues",
        "tags": ["code", "review", "security"],
        "input_schema": {"type": "object", "properties": {"code": {"type": "string"}, "language": {"type": "string"}}},
    },
    {
        "name": "data-analysis",
        "description": "Analyze tabular data and generate statistical summaries",
        "tags": ["data", "analytics", "statistics"],
    },
    {
        "name": "knowledge-lookup",
        "description": "Search knowledge base for relevant articles",
        "tags": ["search", "knowledge", "support"],
    },
]

SAMPLE_TOOLS = [
    {
        "name": "web-search",
        "description": "Search the web for information",
        "provider": "google",
        "tags": ["search", "web"],
    },
    {
        "name": "code-executor",
        "description": "Execute code in a sandboxed environment",
        "provider": "internal",
        "tags": ["code", "execution", "sandbox"],
    },
]


async def seed() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("Seeding agents...")
        for agent in SAMPLE_AGENTS:
            resp = await client.post(f"{REGISTRY_URL}/v1/agents/", json=agent)
            if resp.status_code == 201:
                print(f"  Created agent: {agent['name']}")
            else:
                print(f"  Skipped {agent['name']}: {resp.status_code}")

        print("Seeding capabilities...")
        for cap in SAMPLE_CAPABILITIES:
            resp = await client.post(f"{CATALOG_URL}/v1/catalog/capabilities", json=cap)
            if resp.status_code == 201:
                print(f"  Created capability: {cap['name']}")
            else:
                print(f"  Skipped {cap['name']}: {resp.status_code}")

        print("Seeding tools...")
        for tool in SAMPLE_TOOLS:
            resp = await client.post(f"{CATALOG_URL}/v1/catalog/tools", json=tool)
            if resp.status_code == 201:
                print(f"  Created tool: {tool['name']}")
            else:
                print(f"  Skipped {tool['name']}: {resp.status_code}")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(seed())
