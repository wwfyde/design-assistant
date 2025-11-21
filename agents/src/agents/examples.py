from pprint import pprint

from langchain.agents import AgentState, create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolRuntime
from starlette.middleware.sessions import SessionMiddleware

init_chat_model(model="openai:gpt-5-mini")


SessionMiddleware


class RequestState(AgentState):
    """短期记忆, 会话级别"""

    preferences: dict  # 用户偏好, 用于更新用户会话级别的记忆
    aspect_ratio: str  #
    with_figure: bool
    with_tag: bool
    username: str


@tool
def get_state(runtime: ToolRuntime[RequestState]) -> str:
    """获取当前状态信息"""
    state = runtime.state
    state["username"] = "王二麻子"
    return f"{state.get('preferences', None)}, {state.get('aspect_ratio', None)}, {state.get('username', None)}"


if __name__ == "__main__":
    agent: CompiledStateGraph = create_agent(
        model=init_chat_model(model="openai:gpt-5-mini"),
        state_schema=RequestState,
        system_prompt="""你是一名AI助手. 能调用工具, 根据get_state工具获取当前状态信息""",
        tools=[get_state],
        checkpointer=InMemorySaver(),
    )

    s = agent.invoke(
        {
            "messages": HumanMessage("get state"),
            "preferences": {"style": "简约"},
            "aspect_ratio": "16:9",
            "with_figure": True,
            "with_tag": False,
        },
        config={"configurable": {"thread_id": "1"}},
    )
    s2 = agent.invoke(
        {"messages": HumanMessage("你好, 我之前获取到了哪些用户状态信息?, 我是谁")},
        {"configurable": {"thread_id": "1"}},
    )

    s3 = agent.invoke(
        {"messages": HumanMessage("你好, 我之前获取到了哪些用户状态信息?, 我是谁")},
        {"configurable": {"thread_id": "2"}},
    )
    s4 = agent.invoke(
        {"messages": HumanMessage("你好, 我之前获取到了哪些用户状态信息?, 我是谁")},
        {"configurable": {"thread_id": "1"}},
    )
    pprint(s["messages"])
    print()
    pprint(s2["messages"])
    print()
    pprint(s3["messages"])
