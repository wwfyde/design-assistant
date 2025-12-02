from uuid import UUID

import uuid_utils as uuid
from pydantic import BaseModel, ConfigDict, Field


class Prompt(BaseModel):
    config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid.uuid7, title="id")
    tags: list[str] = Field()
    source: str = Field()
    title: str = Field()
    image: str | None = Field(None)
    prompt_en: str | None = Field(None, title="英文Prompt")
    prompt_zh: str | None = Field(None, title="中文Prompt")
    source_url: str | None = Field(default=None)
