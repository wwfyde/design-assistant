from typing import Optional, TypedDict

from langchain_core.tools import BaseTool
from pydantic import BaseModel


class ToolInfoRequired(TypedDict):
    tool_function: BaseTool
    provider: str


class ToolInfoOptional(TypedDict, total=False):
    display_name: Optional[str]
    type: Optional[str]


class ToolInfo(BaseModel):
    id: str
    display_name: Optional[str]
    type: Optional[str]
    # tool_function: BaseTool | None = None  # 不可序列化
    provider: str

    pass


class ToolInfoJsonRequired(TypedDict):
    provider: str
    id: str


class ToolInfoJson(ToolInfoJsonRequired, ToolInfoOptional):
    pass
