import uuid
from uuid import UUID

from openai import BaseModel
from pydantic import ConfigDict


class Chat(BaseModel):
    id: str | UUID
    name: str
    session_id: str | UUID


class ChatMessage(BaseModel):
    id: str | UUID = str(uuid.uuid4())
    session_id: str | UUID
    chat_id: str | UUID | None = None
    role: str
    message: str | None = None
    content: str | None = None


class ChatSession(BaseModel):
    id: str | UUID
    title: str
    model: str
    provider: str
    canvas_id: str | UUID | None = None
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)
