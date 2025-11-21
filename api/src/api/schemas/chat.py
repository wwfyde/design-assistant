from typing import Any, List, Optional
from uuid import UUID

from api.domain.model import ModelInfo
from api.domain.tool import ToolInfo
from pydantic import BaseModel, ConfigDict

from lib import get_current_date


class ChatRequest(BaseModel):
    messages: list[dict[str, Any]]
    session_id: str
    canvas_id: str
    name: str | None = None
    text_model: ModelInfo
    tool_list: List[ToolInfo]
    system_prompt: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ChatCreate(BaseModel):
    messages: list[dict[str, Any]]
    session_id: str
    canvas_id: str
    text_model: ModelInfo
    tool_list: List[ToolInfo]
    system_prompt: Optional[str] = None


class SessionCreate(BaseModel):
    id: str | UUID | None = None
    title: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    messages: list[dict] | None = None
    session_id: str | UUID | None = None
    canvas_id: str | UUID | None = None
    created_at: str = get_current_date()
    updated_at: str = get_current_date()

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class MagicCreate(BaseModel):
    canvas_id: str | UUID | None = None
    messages: list[dict] | None = None
    session_id: str | UUID | None = None
    system_prompt: str | None = None
    title: Optional[str] = None


if __name__ == "__main__":
    from api.domain.chat import ChatSession

    session = SessionCreate(
        id="123e4567-e89b-12d3-a456-426614174000",
        title="Test Session",
        model="gpt-4",
        provider="openai",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    session_create = ChatSession.model_validate(session)
    print(session_create)
