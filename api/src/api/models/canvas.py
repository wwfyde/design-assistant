from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Canvas(Base):
    __tablename__ = "canvas"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, comment="画布名")
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    canvas_id: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[str | None] = mapped_column(String, nullable=True, comment="画布数据")
    messages: Mapped[str | None] = mapped_column(String, nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(String, nullable=True)
    tool_list: Mapped[str | None] = mapped_column(String, nullable=True)
    thumbnail: Mapped[str | None] = mapped_column(String, nullable=True)
    completed = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
