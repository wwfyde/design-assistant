import uuid_utils as uuid
from pydantic import Json
from sqlalchemy import UUID, Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    name = mapped_column(String, index=True, nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatSession(Base):
    __tablename__ = "chat_session"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    canvas_id: Mapped[str | None] = mapped_column(String, nullable=True)
    title = mapped_column(String, index=True, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    messages: Mapped[str | None] = mapped_column(String, nullable=True)
    completed = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_message"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid7,
        server_default=text("uuidv7()"),  # noqa F821
    )
    lc_id: Mapped[str] = mapped_column(String, nullable=True, comment="langchain run id", unique=True, index=True)
    chat_id: Mapped[str | None] = mapped_column(String, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[Json | None] = mapped_column(String, nullable=True)
    content: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
