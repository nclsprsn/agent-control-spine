from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from langfuse import Langfuse

if TYPE_CHECKING:
    from chat.config import ChatSettings

_langfuse: Langfuse | None = None


def init_langfuse(settings: ChatSettings) -> Langfuse | None:
    global _langfuse
    if not settings.langfuse_enabled:
        return None
    _langfuse = Langfuse(
        public_key=settings.langfuse_public_key or None,
        secret_key=settings.langfuse_secret_key or None,
        host=settings.langfuse_host,
    )
    return _langfuse


def get_langfuse() -> Langfuse | None:
    return _langfuse


def create_trace(
    *,
    name: str,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
):
    if _langfuse is None:
        return None
    return _langfuse.trace(
        id=str(uuid.uuid4()),
        name=name,
        user_id=user_id,
        session_id=session_id,
        metadata=metadata,
        tags=tags or [],
    )


def flush() -> None:
    if _langfuse is not None:
        _langfuse.flush()


def shutdown() -> None:
    if _langfuse is not None:
        _langfuse.shutdown()
