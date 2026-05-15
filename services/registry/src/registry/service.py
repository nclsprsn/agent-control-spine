import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from registry.models import Agent, AgentStatus, AgentVersion
from registry.schemas import AgentCreate, AgentUpdate


class AgentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: AgentCreate) -> Agent:
        agent = Agent(
            name=data.name,
            version=data.version,
            description=data.description,
            owner=data.owner,
            endpoint_url=data.endpoint_url,
            auth_config=data.auth_config,
            metadata_=data.metadata,
        )
        self.session.add(agent)
        await self.session.flush()

        version = AgentVersion(agent_id=agent.id, version=data.version)
        self.session.add(version)
        await self.session.flush()

        return agent

    async def get(self, agent_id: uuid.UUID) -> Agent | None:
        return await self.session.get(Agent, agent_id)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: AgentStatus | None = None,
    ) -> tuple[list[Agent], int]:
        query = select(Agent)
        count_query = select(func.count()).select_from(Agent)

        if status_filter:
            query = query.where(Agent.status == status_filter)
            count_query = count_query.where(Agent.status == status_filter)

        total = await self.session.scalar(count_query) or 0

        query = query.offset((page - 1) * page_size).limit(page_size).order_by(Agent.created_at.desc())
        result = await self.session.execute(query)
        agents = list(result.scalars().all())

        return agents, total

    async def update(self, agent_id: uuid.UUID, data: AgentUpdate) -> Agent | None:
        agent = await self.get(agent_id)
        if agent is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            update_data["metadata_"] = update_data.pop("metadata")

        for field, value in update_data.items():
            setattr(agent, field, value)

        if data.version is not None and data.version != agent.version:
            version = AgentVersion(agent_id=agent.id, version=data.version)
            self.session.add(version)

        await self.session.flush()
        return agent

    async def delete(self, agent_id: uuid.UUID) -> bool:
        agent = await self.get(agent_id)
        if agent is None:
            return False
        await self.session.delete(agent)
        await self.session.flush()
        return True

    async def heartbeat(self, agent_id: uuid.UUID) -> Agent | None:
        agent = await self.get(agent_id)
        if agent is None:
            return None
        agent.last_heartbeat_at = datetime.now(UTC)
        if agent.status == AgentStatus.REGISTERED:
            agent.status = AgentStatus.ACTIVE
        await self.session.flush()
        return agent
