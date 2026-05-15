import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spine_common.models import AuditMixin, Base


class AgentStatus(str, enum.Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    TERMINATED = "terminated"


class Agent(AuditMixin, Base):
    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50))
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), default=AgentStatus.REGISTERED)
    description: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(255))
    endpoint_url: Mapped[str | None] = mapped_column(String(2048))
    auth_config: Mapped[dict | None] = mapped_column(JSONB)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    versions: Mapped[list["AgentVersion"]] = relationship(back_populates="agent", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_agents_status", "status"),)


class AgentVersion(AuditMixin, Base):
    __tablename__ = "agent_versions"

    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"))
    version: Mapped[str] = mapped_column(String(50))
    changelog: Mapped[str | None] = mapped_column(Text)
    config_snapshot: Mapped[dict | None] = mapped_column(JSONB)

    agent: Mapped["Agent"] = relationship(back_populates="versions")

    __table_args__ = (Index("ix_agent_versions_agent_id", "agent_id"),)
