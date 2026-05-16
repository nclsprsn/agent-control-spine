import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chat.models import Conversation, Message, MessageRole


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: str, agent_id: uuid.UUID, title: str | None = None) -> Conversation:
        conv = Conversation(user_id=user_id, agent_id=agent_id, title=title)
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def get(self, conversation_id: uuid.UUID) -> Conversation | None:
        query = (
            select(Conversation).where(Conversation.id == conversation_id).options(selectinload(Conversation.messages))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[tuple[Conversation, int]], int]:
        count_query = select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        total = await self.session.scalar(count_query) or 0

        msg_count = (
            select(func.count())
            .where(Message.conversation_id == Conversation.id)
            .correlate(Conversation)
            .scalar_subquery()
            .label("message_count")
        )
        query = (
            select(Conversation, msg_count)
            .where(Conversation.user_id == user_id)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(Conversation.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.all()), total

    async def delete(self, conversation_id: uuid.UUID) -> bool:
        conv = await self.session.get(Conversation, conversation_id)
        if conv is None:
            return False
        await self.session.delete(conv)
        await self.session.flush()
        return True

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: MessageRole,
        content: str,
        tool_calls: dict[str, Any] | None = None,
        token_usage: dict[str, Any] | None = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            token_usage=token_usage,
        )
        self.session.add(msg)
        await self.session.flush()
        return msg
