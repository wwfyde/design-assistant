from typing import Optional

from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from pydantic import BaseModel

from agents import rednote_agent


class RednoteArgs(BaseModel):
    title: Optional[str]
    pass


@tool("rednote_tool", args_schema=RednoteArgs)
async def call_rednote_agent(query: str, runtime: ToolRuntime) -> str:
    messages = runtime.state["messages"]
    result = await rednote_agent.ainvoke(
        {
            "messages": [{"role": "user", "content": query}],
            "aspect_ratio": runtime.state["aspect_ratio"],
        }
    )

    return result["messages"][-1].content
