from typing import Any, Optional

from agents.types import Messages
from api.domain.model import ModelInfo
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from tools.images import image_create_with_seedream

from lib import settings


class Context(BaseModel):
    session_id: str
    user_id: str
    canvas_id: Optional[str] = None


async def create_multi_agent(
    state: Any,
    *,
    context: type[BaseModel],
    tools: list[Any],
    system_prompt: str,
    messages: list[type[Messages]] = None,
    text_model: Optional[ModelInfo] = None,
) -> CompiledStateGraph:
    openai_model_config = settings.providers.openai
    if text_model:
        # TODO: use custom model
        pass
    model = ChatOpenAI(
        name=openai_model_config.model or "gpt-4.1-mini",
        openai_api_key=openai_model_config.api_key,
    )

    return create_agent(model, tools, context_schema=context, system_prompt=system_prompt)
    pass


async def main():
    b = await create_multi_agent(
        "",
        context=Context,
        tools=[image_create_with_seedream],
        system_prompt="你是一名图像设计agent. 支持调用seedream工具, 创建或编辑图像",
    )
    res = b.invoke(
        input=HumanMessage("帮我创建一张日出风景图, 宽高比3:4"),
        context=Context(user_id="11", session_id="22", canvas_id="11"),
    )
    print(b)


if __name__ == "__main__":
    main()
