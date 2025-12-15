from uuid import UUID

from pydantic import BaseModel

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
    id: str | UUID


class CanvasSave(BaseModel):
    canvas_id: str | UUID
    data: str
    thumbnail: str | None
