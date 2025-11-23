from typing import NotRequired, Optional

from api.core.memory import memory_checkpointer
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, dynamic_prompt
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from langgraph_tools.images import image_create_with_seedream
from pydantic import BaseModel, Field

from lib import settings


class CreativeAssistantState(AgentState):
    """短期记忆, 会话级别"""

    aspect_ratio: NotRequired[str]


class ResponseFormat(BaseModel):
    content: str
    title: Optional[str] = Field(None, title="标题", description="标题")
    images: Optional[list[str]] = Field(
        None, title="生成的图片url", description="生成的图片URL列表"
    )
    # preferences: Optional[dict]
    # tags: list[str]
    # with_emoji: bool = Field(
    #     False, title="包含表情符号", description="内容是否包含表情符号"
    # )


class RednoteContext(BaseModel):
    user_id: str
    conversation_id: str = Field(title="对话ID")
    session_id: Optional[str] = Field(None, title="会话ID")
    profile_id: Optional[str] = Field(None, title="用户资料ID")
    canvas_id: Optional[str] = None


class CustomMiddleware(AgentMiddleware):
    state_schema = CreativeAssistantState

    # def before_model(
    #     self, state: AgentState[RednoteState], runtime: Runtime[ResponseFormat]
    # ) -> dict[str, Any] | None:
    #     prefrences = state.get("preferences", None)
    #     if not prefrences:
    #         # TODO: 未初始化用户偏好
    #         pass
    #     pass


@dynamic_prompt
def creative_dynamic_system_prompt(request: ModelRequest):
    state: CreativeAssistantState = request.state
    aspect_ratio = state.get("aspect_ratio", "1:1")
    base_prompt = """
    # 身份

    你是一名小红书文案助手. 支持生成文案, 也支持生成配图.

    输出格式为Markdown, 用Markdown风格预览图片
    """

    tool_prompt = """
    ## 工具说明

    > You have access to these tools below:

    - image_create_with_seedream: 图像生成工具, 可以为小红书生成配图
    """
    constraint = """"""
    if aspect_ratio:
        constraint = f"""
            - 请根据用户提供的宽高比为{aspect_ratio}，生成适合该宽高比的文案内容\n
    """
    if state.get("with_figure", False):
        constraint += " - 请生成插图\n"

    if state.get("with_tag", False):
        constraint += " - 请返回标签\n"

    return "\n".join([base_prompt, tool_prompt, constraint])


rednote_prompt = """你是一名AI助手,请和我聊天"""


creative_system_prompt = """
# 角色（Role）

你是创意设计Agent.

# 工具
你可以使用一下工具:

- image_create_with_seedream: 图像创作, 图像生成图像编辑


# IMAGE INPUT DETECTION:

When the user's message contains input images in XML format like:
<input_images></input_images>
You MUST:
1. Parse the XML to extract image_url attributes from <image> tags
2. Use tools that support images_urls parameter when images are present

# 规则

- 图像类型分为本地图像和网络图像, 本地图像格式为 img_2b2de312310745118d54672b80e218f1.png 类似的格式, 仅存有文件名, 工具会自行拼接. 传入工具时使用本地图像或网络图像url
"""

model = ChatOpenAI(
    model="doubao-seed-1-6-vision-250815",
    api_key=settings.providers.ark.api_key,
    base_url=settings.providers.ark.base_url,
    use_responses_api=False,
)


def build_creative_assistant(checkpointer):
    agent: CompiledStateGraph = create_agent(
        model=model,
        tools=[image_create_with_seedream],
        middleware=[],
        system_prompt=creative_system_prompt,
        state_schema=CreativeAssistantState,  # noqa F401
        # context_schema=RednoteContext,
        checkpointer=checkpointer,
    )
    return agent


if __name__ == "__main__":
    # rednote_agent = build_rednote_agent()

    creative_assistant = build_creative_assistant(memory_checkpointer)
    resp = creative_assistant.invoke(
        input=CreativeAssistantState(messages=HumanMessage("你好"), aspect_ratio="1:1"),
        config={"configurable": {"thread_id": "2"}},
    )
    print(resp["messages"][-1].content)
    resp = creative_assistant.invoke(
        input=CreativeAssistantState(
            messages=HumanMessage("你支持哪些分辨率"), aspect_ratio="1:1"
        ),
        config={"configurable": {"thread_id": "2"}},
    )
    print(resp["messages"][-1].content)
    resp = creative_assistant.invoke(
        input=CreativeAssistantState(
            messages=HumanMessage("帮我生成一碗牛肉面, 分辨率3:4"), aspect_ratio="1:1"
        ),
        config={"configurable": {"thread_id": "2"}},
    )
    print(resp["messages"][-3].content)
    print(resp["messages"][-2].content)
    print(resp["messages"][-1].content)

    pass
