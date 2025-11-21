from typing import Optional

from pydantic import BaseModel, Field


class Tool(BaseModel):
    id: str
    display_name: str
    provider: Optional[str] = Field(None, description="工具提供商")
    type: Optional[str] = Field(None, description="工具类型")
    agent_name: str
    description: str
    args: dict[str, str] | BaseModel


class Agent(BaseModel):
    tools: list[Tool] = Field(..., description="Agent使用的工具列表")
    name: str = Field(..., description="Agent名称")
    system_prompt: Optional[str] = Field(None, description="系统提示")
    handoffs: Optional[list[str]] = Field(None, description="交接信息")
