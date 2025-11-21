from uuid import UUID

from api.domain.model import ModelInfo
from api.domain.tool import ToolInfo
from pydantic import BaseModel


class CanvasCreate(BaseModel):
    canvas_id: str | UUID
    messages: list[dict] | None = None
    name: str | None = None
    canvas_id: str | UUID | None = None
    session_id: str | UUID | None = None
    system_prompt: str | None = None
    text_model: ModelInfo | None = None
    tool_list: list[ToolInfo] | None = None


class CanvasResponse(BaseModel):
    id: str | UUID


class CanvasSave(BaseModel):
    canvas_id: str | UUID
    data: str
    thumbnail: str | None
