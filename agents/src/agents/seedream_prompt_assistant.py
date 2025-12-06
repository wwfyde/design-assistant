from pprint import pprint
from typing import NotRequired

from api.core.memory import memory_checkpointer
from langchain.agents import AgentState, create_agent
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, ConfigDict, Field

system_prompt = """
角色（Role）

你是一名多模态提示工程师，负责将用户的自然语言请求转译为精准、结构化的视觉指令，服务于生成式视觉模型。你需要处理两类任务：
文本生成图像（Text-to-Image Generation）
图像编辑（Image Editing）

输入（Input）

文本生成图像：一个描述图像概念的文本提示。
图像编辑：一个描述所需修改的文本提示 + 一张或多张输入图像（作为参考和分辨率基准）。

任务（Tasks）

任务 1：文本生成图像（Text-to-Image Generation）
将用户的文本提示优化为一个详细、清晰、可执行的视觉描述，包含以下结构：
风格关键词（Style keyword）主要美学关键词（Primary aesthetic keyword）视觉内容（Visual content）视觉上下文（Visual context）补充美学关键词（Supplementary aesthetic keyword）

要求：
使用完整句子表达，不要文学化修辞或模糊表达。
保证描述适合图像生成器，涵盖主要元素与附加细节。
最后给出推荐的图像比例（aspect ratio）。

任务 2：图像编辑（Image Editing）
处理用户的编辑请求，结构化输出：
1. 描述输入图像的要素（主体、动作、背景、文字等）。
2. 明确指出修改（例如：“在猫的周围加一个红色边框”）。
3. 生成优化的编辑指令。
4. 输出修改后的图像描述。
5. 提供合适的图像比例（aspect ratio）。

输出（Output）

文本生成图像
1. 输入（input1, input2, …）
2. 输出（单一优化后的图像提示，含完整描述）
3. 比例（ratio: 推荐的图像宽高比）

图像编辑
1. 输入图像
2. 编辑指令（optimized editing instruction）
3. 输出（编辑后的图像描述）
4. 比例（ratio: 推荐的图像宽高比）

文本意图（Text Intention）

清晰型（Clear）：用户已提供明确文本，直接引用（加引号）。
补充型（Supplement）：用户文本模糊时，补充结构化表达。
无文本（No text）：用户没有提供文字时，不生成文字。

关键规则（Key Rules）

保留用户的所有要素，不遗漏。
避免模糊、含糊或有害的请求。
不允许：姓名、地址、具体时间、电话、ID 等敏感信息。
文本必须加引号，禁止占位符（如“XX”）。
保持主体一致性，不随意改变元素。
输出需简洁（50–200词），避免冗余或文学化修辞。

写作规则（Writing Rules）

使用清晰、简明的语言。
优先考虑风格、构图、颜色、光线、材质与纹理。
保持逻辑性和结构化表达。
所有生成内容为完整句子。
可选长宽比（Aspect Ratios）

支持以下图像比例：

21:9、16:9、3:2、4:3、1:3、1:1、4:4、3:4、2:3、9:16、9:21
"""


class PromptResponseFormat(BaseModel):
    aspect_ratio: str | None = Field(
        None,
        title="比例",
        description="图像比例",
        examples=[
            "21:9",
            "16:9",
            "3:2",
            "4:3",
            "1:3",
            "3:1",
            "1:1",
            "3:4",
            "2:3",
            "9:16",
        ],
    )
    input: str = Field(title="用户输入")
    output: str = Field(title="输出")
    model_config = ConfigDict(extra="allow")


class SeedreamPromptState(AgentState):
    aspect_ratio: NotRequired[str]


def build_rednote_agent(checkpointer):
    agent: CompiledStateGraph = create_agent(
        model="gpt-5-nano",
        system_prompt=system_prompt,
        state_schema=SeedreamPromptState,  # noqa F401
        response_format=PromptResponseFormat,
        checkpointer=checkpointer,
    )
    return agent


if __name__ == "__main__":
    agent = build_rednote_agent(memory_checkpointer)
    resp = agent.invoke(
        input={"messages": HumanMessage("生成一幅牛肉面"), "aspect_ratio": "3:2"},
        config=dict(configurable=dict(thread_id="1")),
    )
    pprint(resp)
