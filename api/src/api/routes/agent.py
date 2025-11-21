from typing import Optional

from agents.rednote_agent import RednoteContext, RednoteState
from api.deps import get_rednote_agent
from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel
from starlette.requests import Request

router = APIRouter()


class RednoteRequest(BaseModel):
    prompt: str
    aspect_ratio: Optional[str]

    user_id: str
    conversation_id: str


@router.post("/rednote")
async def generate_rednote(
    body: RednoteRequest,
    request: Request,
    agent: CompiledStateGraph = Depends(get_rednote_agent),
):
    """需要支持多轮对话"""

    # 基于会话初始化agent实例

    # TODO 总是从redis中召回对话历史

    agent = request.app.state.rednote_agent
    input: RednoteState = RednoteState(
        messages=[HumanMessage(content=body.prompt)],
        aspect_ratio=body.aspect_ratio,
        preferences={},
        with_figure=None,
        with_tag=None,
    )
    print(body.prompt)
    if body.aspect_ratio:
        input["aspect_ratio"] = body.aspect_ratio

    response = agent.invoke(
        input,
        config=RunnableConfig(configurable={"thread_id": body.conversation_id}),
        context=RednoteContext(
            user_id=body.user_id, conversation_id=body.conversation_id
        ),
    )
    print(response["messages"][-1].content)
    return response
