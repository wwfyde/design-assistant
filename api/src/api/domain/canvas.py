import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from lib import get_current_date


class Canvas(BaseModel):
    id: str | UUID
    name: str
    session_id: str | None = None
    canvas_id: str | None = None
    data: str | dict | None = None  # 画布数据
    messages: list[dict] = None
    system_prompt: str | None = None
    tool_list: list[str] | None = None
    thumbnail: str | None = None
    created_at: str | None = get_current_date()
    updated_at: str | None = get_current_date()

    model_config = ConfigDict(from_attributes=True)

    @field_validator("messages", "data", "tool_list", mode="before")
    @classmethod
    def parse_json_fields(cls, v: Any) -> Any:
        """
        如果输入是字符串（来自数据库），尝试解析为 JSON。
        如果已经是 list（比如手动构造的），则直接返回。
        """
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # 处理空字符串的情况
                if not v.strip():
                    return None
                return json.loads(v)
            except json.JSONDecodeError:
                # 解析失败可以选择抛错，或者返回空列表，视业务需求定
                return []
        return v

    # --- 处理函数 2: 自动格式化时间 ---
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
