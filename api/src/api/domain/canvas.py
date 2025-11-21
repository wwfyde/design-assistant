from uuid import UUID

from pydantic import BaseModel

from lib import get_current_date


class Canvas(BaseModel):
    id: str | UUID
    name: str
    session_id: str | None = None
    canvas_id: str | None = None
    data: str | None = None  # 画布数据
    messages: list[dict] = None
    system_prompt: str | None = None
    tool_list: list[str] = None
    thumbnail: str | None = None
    created_at: str | None = get_current_date()
    updated_at: str | None = get_current_date()
