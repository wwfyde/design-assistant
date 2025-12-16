from uuid import UUID
from typing import Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from api.domain.tool import ToolInfo
from api.domain.model import ModelInfo


class CanvasCreate(BaseModel):
    canvas_id: str | UUID
    messages: list[dict] | None = None
    name: str | None = None
    canvas_id: str | UUID | None = None
    session_id: str | UUID | None = None
    user_id: str | None = None
    system_prompt: str | None = None
    text_model: ModelInfo | None = None
    tool_list: list[ToolInfo] | None = None


class CanvasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str | None = None
    name: str | None = None
    user_id: str | None = None
    thumbnail: str | None = None
    canvas_id: str | None = None
    session_id: str | None = None
    created_at: datetime
    updated_at: datetime


class CanvasSave(BaseModel):
    canvas_id: str | UUID
    data: str
    thumbnail: str | None
