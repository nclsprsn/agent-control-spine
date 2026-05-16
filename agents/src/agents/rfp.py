"""Pydantic AI agent for generating structured RFP responses."""

import asyncio

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel


class RfpSection(BaseModel):
    title: str
    content: str


class RfpResponse(BaseModel):
    executive_summary: str
    understanding: str
    approach: str
    timeline: str
    pricing_notes: str
    differentiators: str
    sections: list[RfpSection]


model = OpenAIChatModel("qwen3:8b", provider="ollama")

rfp_agent = Agent(
    model,
    output_type=RfpResponse,
    system_prompt=(
        "You are an expert RFP response writer. Given RFP requirements or questions, "
        "produce a professional, structured proposal response.\n\n"
        "Guidelines:\n"
        "- executive_summary: 2-3 sentence high-level overview of the proposal\n"
        "- understanding: demonstrate comprehension of the client's requirements and pain points\n"
        "- approach: describe the proposed methodology, architecture, or solution\n"
        "- timeline: provide milestones with estimated durations\n"
        "- pricing_notes: state pricing assumptions, rate structures, or cost drivers\n"
        "- differentiators: highlight key strengths and competitive advantages\n"
        "- sections: add any additional sections relevant to the specific RFP\n\n"
        "Be specific and quantitative where possible. Write in a confident but measured tone. "
        "Tailor every section to the stated requirements."
    ),
)


async def main() -> None:
    result = await rfp_agent.run(
        "We need a vendor to build a cloud-native data platform for our 500-person fintech company. "
        "Requirements: real-time analytics, SOC 2 compliance, 99.9% uptime SLA, "
        "integration with existing Snowflake and Kafka infrastructure. Budget range $500K-$1M. "
        "Timeline: MVP in 3 months, full rollout in 6 months."
    )
    print(f"Executive Summary:\n{result.output.executive_summary}\n")
    print(f"Understanding:\n{result.output.understanding}\n")
    print(f"Approach:\n{result.output.approach}\n")
    print(f"Timeline:\n{result.output.timeline}\n")
    print(f"Pricing Notes:\n{result.output.pricing_notes}\n")
    print(f"Differentiators:\n{result.output.differentiators}\n")
    for section in result.output.sections:
        print(f"{section.title}:\n{section.content}\n")


if __name__ == "__main__":
    asyncio.run(main())
