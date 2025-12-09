# type: ignore[import]
import json
import traceback
from typing import Any, Awaitable, Callable, Dict, List, Optional

from langchain_core.messages import (
    AIMessageChunk,
    ToolCall,
    ToolMessage,
    convert_to_openai_messages,
)
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.orm import Session

from api.core.db import async_session, engine
from api.core.memory import memory_store
from api.services.chat import ChatService, InMemoryChatRepo, PostgresChatRepo
from lib import settings


class StreamProcessor:
    """流式处理器 - 负责处理智能体的流式输出"""

    def __init__(
        self,
        session_id: str,
        websocket_service: Callable[[str, Dict[str, Any]], Awaitable[None]],
    ):
        self.session_id = session_id
        self.websocket_service = websocket_service
        self.tool_calls: List[ToolCall] = []
        self.last_saved_message_index = 0
        self.last_streaming_tool_call_id: Optional[str] = None

    async def process_stream(
        self,
        supervisor: CompiledStateGraph,
        messages: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> None:
        """处理整个流式响应

        Args:
            supervisor: 智能体群组
            messages: 消息列表
            context: 上下文信息
        """

        # agent = supervisor.compile()
        print(f"用户消息: {messages}")
        # print("测试")

        async for chunk in supervisor.astream(
            {"messages": messages},
            config=context,
            stream_mode=["messages", "custom", "values"],
        ):
            # print(chunk)
            await self._handle_chunk(chunk)

        # 发送完成事件
        print("发送完事件")
        await self.websocket_service(self.session_id, {"type": "done"})

    async def _handle_chunk(self, chunk: Any) -> None:
        # print('👇chunk', chunk)
        """处理单个chunk"""
        chunk_type = chunk[0]

        if chunk_type == "values":
            await self._handle_values_chunk(chunk[1])
        else:
            await self._handle_message_chunk(chunk[1][0])

    async def _handle_values_chunk(self, chunk_data: Dict[str, Any]) -> None:
        """处理 values 类型的 chunk"""

        # TODO 这里是langchain中维护的消息列表

        all_messages = chunk_data.get("messages", [])
        # print(f"{all_messages=}")
        oai_messages = convert_to_openai_messages(all_messages, include_id=False)
        # print(f"{oai_messages=}")
        # 确保 oai_messages 是列表类型
        if not isinstance(oai_messages, list):
            oai_messages = [oai_messages] if oai_messages else []

        # 发送所有消息到前端
        # print("发送: ", oai_messages)
        await self.websocket_service(self.session_id, {"type": "all_messages", "messages": oai_messages})

        # 保存新消息到数据库
        async with async_session() as asession:
            with Session(engine) as session:
                if settings.repo_type == "in-memory":
                    chat_service = ChatService(InMemoryChatRepo(memory_store))
                elif settings.repo_type == "postgres":
                    chat_service = ChatService(PostgresChatRepo(session=session, asession=asession))
                else:
                    chat_service = ChatService(InMemoryChatRepo(memory_store))

                # 获取最近保存消息的lc_id
                last_saved_index = next(
                    (i for i in range(len(oai_messages) - 1, -1, -1) if oai_messages[i]["role"] == "user"),
                    None,
                )

                for oai_message, message in zip(
                    oai_messages[last_saved_index + 1 :],
                    all_messages[last_saved_index + 1 :],
                ):
                    # print(f"assistant message {message=}")
                    chat_service.create_message(
                        self.session_id,
                        oai_message.get("role", "user"),  # message.role or "user",
                        json.dumps(oai_message, ensure_ascii=False),
                        message_id=message.id if not message.id.startswith("lc_run--") else None,
                        lc_id=message.id,
                        # getattr(all_messages[i], "id", None) if i < len(all_messages) else None,  # langchain生成的id 不规范, 或者替换lc_run---
                    )

    async def _handle_message_chunk(self, ai_message_chunk: AIMessageChunk) -> None:
        """处理消息类型的 chunk"""
        # print('👇ai_message_chunk', ai_message_chunk)
        try:
            content = ai_message_chunk.content

            if isinstance(ai_message_chunk, ToolMessage):
                # 工具调用结果之后会在 values 类型中发送到前端，这里会更快出现一些
                oai_message = convert_to_openai_messages([ai_message_chunk])[0]
                # print("👇toolcall res oai_message", oai_message)
                await self.websocket_service(
                    self.session_id,
                    {
                        "type": "tool_call_result",
                        "id": ai_message_chunk.tool_call_id,
                        "message": oai_message,
                    },
                )
            elif content:
                # 发送文本内容
                await self.websocket_service(self.session_id, {"type": "delta", "text": content})
            elif (
                hasattr(ai_message_chunk, "tool_calls")
                and ai_message_chunk.tool_calls
                and ai_message_chunk.tool_calls[0].get("name")
            ):
                # 处理工具调用
                await self._handle_tool_calls(ai_message_chunk.tool_calls)

            # 处理工具调用参数流
            if hasattr(ai_message_chunk, "tool_call_chunks"):
                await self._handle_tool_call_chunks(ai_message_chunk.tool_call_chunks)
        except Exception as e:
            print("🟠error", e)
            traceback.print_stack()

    async def _handle_tool_calls(self, tool_calls: List[ToolCall]) -> None:
        """处理工具调用"""
        self.tool_calls = [tc for tc in tool_calls if tc.get("name")]
        print("😘tool_call event", tool_calls)

        # 需要确认的工具列表
        TOOLS_REQUIRING_CONFIRMATION = {
            # 'generate_video_by_kling_v2_jaaz',
            # 'generate_video_by_seedance_v1_pro_volces',
            # 'generate_video_by_seedance_v1_lite_i2v',
            # 'generate_video_by_seedance_v1_lite_t2v',
            # 'generate_video_by_seedance_v1_jaaz',
            # 'generate_video_by_hailuo_02_jaaz',
            "generate_video_by_veo3_fast_jaaz",
        }

        for tool_call in self.tool_calls:
            tool_name = tool_call.get("name")

            # 检查是否需要确认
            if tool_name in TOOLS_REQUIRING_CONFIRMATION:
                # 对于需要确认的工具，不在这里发送事件，让工具函数自己处理
                print(f"🔄 Tool {tool_name} requires confirmation, skipping StreamProcessor event")
                continue
            else:
                await self.websocket_service(
                    self.session_id,
                    {
                        "type": "tool_call",
                        "id": tool_call.get("id"),
                        "name": tool_name,
                        "arguments": "{}",
                    },
                )

    async def _handle_tool_call_chunks(self, tool_call_chunks: List[Any]) -> None:
        """处理工具调用参数流"""
        for tool_call_chunk in tool_call_chunks:
            if tool_call_chunk.get("id"):
                # 标记新的流式工具调用参数开始
                self.last_streaming_tool_call_id = tool_call_chunk.get("id")
            else:
                if self.last_streaming_tool_call_id:
                    await self.websocket_service(
                        self.session_id,
                        {
                            "type": "tool_call_arguments",
                            "id": self.last_streaming_tool_call_id,
                            "text": tool_call_chunk.get("args"),
                        },
                    )
                else:
                    print("🟠no last_streaming_tool_call_id", tool_call_chunk)
