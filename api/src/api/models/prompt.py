import uuid_utils as uuid
from api.models import Base
from sqlalchemy import UUID, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column


class Prompt(Base):
    __tablename__ = "prompt"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid7,
        server_default=text("uuidv7()"),
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text))
    title: Mapped[str | None] = mapped_column(Text, nullable=True, comment="标题")
    image: Mapped[str | None] = mapped_column(Text, nullable=True, comment="图片")
    source: Mapped[str | None] = mapped_column(Text, nullable=True, comment="来源")
    prompt_en: Mapped[str | None] = mapped_column(Text, nullable=True, comment="英文Prompt")
    prompt_zh: Mapped[str | None] = mapped_column(Text, nullable=True, comment="中文Prompt")
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True, comment="来源链接")
