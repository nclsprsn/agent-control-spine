import uuid
from typing import Any

from sqlalchemy import cast, func, or_, select
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import Text

from catalog.models import Capability, Tool
from catalog.schemas import CapabilityCreate, CapabilityUpdate, ToolCreate, ToolUpdate


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_capability(self, data: CapabilityCreate) -> Capability:
        cap = Capability(**data.model_dump())
        self.session.add(cap)
        await self.session.flush()
        return cap

    async def get_capability(self, cap_id: uuid.UUID) -> Capability | None:
        return await self.session.get(Capability, cap_id)

    async def list_capabilities(
        self, page: int = 1, page_size: int = 20, tags: list[str] | None = None
    ) -> tuple[list[Capability], int]:
        query = select(Capability)
        count_query = select(func.count()).select_from(Capability)

        if tags:
            tag_array = cast(tags, PG_ARRAY(Text))
            query = query.where(Capability.tags.bool_op("&&")(tag_array))
            count_query = count_query.where(Capability.tags.bool_op("&&")(tag_array))

        total = await self.session.scalar(count_query) or 0
        query = query.offset((page - 1) * page_size).limit(page_size).order_by(Capability.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def update_capability(self, cap_id: uuid.UUID, data: CapabilityUpdate) -> Capability | None:
        cap = await self.get_capability(cap_id)
        if cap is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cap, field, value)
        await self.session.flush()
        await self.session.refresh(cap)
        return cap

    async def delete_capability(self, cap_id: uuid.UUID) -> bool:
        cap = await self.get_capability(cap_id)
        if cap is None:
            return False
        await self.session.delete(cap)
        await self.session.flush()
        return True

    async def create_tool(self, data: ToolCreate) -> Tool:
        tool = Tool(**data.model_dump())
        self.session.add(tool)
        await self.session.flush()
        return tool

    async def get_tool(self, tool_id: uuid.UUID) -> Tool | None:
        return await self.session.get(Tool, tool_id)

    async def list_tools(
        self, page: int = 1, page_size: int = 20, tags: list[str] | None = None
    ) -> tuple[list[Tool], int]:
        query = select(Tool)
        count_query = select(func.count()).select_from(Tool)

        if tags:
            tag_array = cast(tags, PG_ARRAY(Text))
            query = query.where(Tool.tags.bool_op("&&")(tag_array))
            count_query = count_query.where(Tool.tags.bool_op("&&")(tag_array))

        total = await self.session.scalar(count_query) or 0
        query = query.offset((page - 1) * page_size).limit(page_size).order_by(Tool.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def update_tool(self, tool_id: uuid.UUID, data: ToolUpdate) -> Tool | None:
        tool = await self.get_tool(tool_id)
        if tool is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tool, field, value)
        await self.session.flush()
        await self.session.refresh(tool)
        return tool

    async def delete_tool(self, tool_id: uuid.UUID) -> bool:
        tool = await self.get_tool(tool_id)
        if tool is None:
            return False
        await self.session.delete(tool)
        await self.session.flush()
        return True

    async def search(
        self, query: str, tags: list[str] | None = None, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        cap_q = select(Capability).where(
            or_(
                Capability.name.ilike(f"%{query}%"),
                Capability.description.ilike(f"%{query}%"),
            )
        )
        tool_q = select(Tool).where(
            or_(
                Tool.name.ilike(f"%{query}%"),
                Tool.description.ilike(f"%{query}%"),
            )
        )

        if tags:
            tag_array = cast(tags, PG_ARRAY(Text))
            cap_q = cap_q.where(Capability.tags.bool_op("&&")(tag_array))
            tool_q = tool_q.where(Tool.tags.bool_op("&&")(tag_array))

        cap_q = cap_q.limit(page_size).offset((page - 1) * page_size)
        tool_q = tool_q.limit(page_size).offset((page - 1) * page_size)

        cap_result = await self.session.execute(cap_q)
        tool_result = await self.session.execute(tool_q)

        return {
            "capabilities": list(cap_result.scalars().all()),
            "tools": list(tool_result.scalars().all()),
        }
