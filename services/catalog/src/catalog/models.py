import uuid

from sqlalchemy import ARRAY, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from spine_common.models import AuditMixin, Base


class Capability(AuditMixin, Base):
    __tablename__ = "capabilities"

    agent_id: Mapped[uuid.UUID | None] = mapped_column()
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    input_schema: Mapped[dict | None] = mapped_column(JSONB)
    output_schema: Mapped[dict | None] = mapped_column(JSONB)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    __table_args__ = (
        Index("ix_capabilities_tags", "tags", postgresql_using="gin"),
    )


class Tool(AuditMixin, Base):
    __tablename__ = "tools"

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(255))
    input_schema: Mapped[dict | None] = mapped_column(JSONB)
    output_schema: Mapped[dict | None] = mapped_column(JSONB)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    __table_args__ = (
        Index("ix_tools_tags", "tags", postgresql_using="gin"),
    )
