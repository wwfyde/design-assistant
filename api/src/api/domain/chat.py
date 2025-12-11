from uuid import UUID
from typing import Any
from datetime import datetime

import uuid_utils as uuid
from openai import BaseModel
from pydantic import Json, Field, ConfigDict, field_validator

from lib import get_current_date


class Chat(BaseModel):
    id: str | UUID
    name: str
    session_id: str

    model_config = ConfigDict(from_attributes=True)


class ChatMessage(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid7)
    lc_id: str | None = Field(default=None)
    session_id: str
    chat_id: str | None = None
    role: str
    message: Json | None = None
    content: str | None = None
    created_at: str = get_current_date()
    updated_at: str = get_current_date()

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def format_datetime(cls, v: Any) -> Any:
        """
        如果输入是 datetime 对象（来自数据库），转换为字符串。
        """
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.astimezone().isoformat(timespec="seconds")
        return v


class ChatSession(BaseModel):
    id: str | UUID
    title: str
    model: str
    provider: str
    canvas_id: str | UUID | None = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def format_datetime(cls, v: Any) -> Any:
        """
        如果输入是 datetime 对象（来自数据库），转换为字符串。
        """
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.astimezone().isoformat(timespec="seconds")
        return v
