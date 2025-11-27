import uuid
from datetime import datetime
from typing import Any
from uuid import UUID

from openai import BaseModel
from pydantic import ConfigDict, Json, field_validator

from lib import get_current_date


class Chat(BaseModel):
    id: str | UUID
    name: str
    session_id: str | UUID

    model_config = ConfigDict(from_attributes=True)


class ChatMessage(BaseModel):
    id: str | UUID = str(uuid.uuid7())
    lc_id: str | UUID | None
    session_id: str | UUID
    chat_id: str | UUID | None = None
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
