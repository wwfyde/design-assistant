from agents.creative_assitant import build_creative_assistant
from api.core.memory import memory_checkpointer
from api.core.StreamProcessor import StreamProcessor
from api.domain.model import ModelInfo
from api.domain.tool import ToolInfo
from api.services.websocket import send_to_websocket

from lib import settings

supervisor_prompt = """You are a supervisor managing two agents"""


import traceback
from typing import Any, Dict, List, Set, TypedDict, cast

from langchain_openai import ChatOpenAI

# from services.websocket_service import send_to_websocket  # type: ignore


class ContextInfo(TypedDict):
    """Context information passed to tools"""

    canvas_id: str
    session_id: str
    model_info: Dict[str, List[ModelInfo]]


def _fix_chat_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """修复聊天历史中不完整的工具调用

    根据LangGraph文档建议，移除没有对应ToolMessage的tool_calls
    参考: https://langchain-ai.github.io/langgraph/troubleshooting/errors/INVALID_CHAT_HISTORY/
    """
    if not messages:
        return messages

    fixed_messages: List[Dict[str, Any]] = []
    tool_call_ids: Set[str] = set()

    # 第一遍：收集所有ToolMessage的tool_call_id
    for msg in messages:
        if msg.get("role") == "tool" and msg.get("tool_call_id"):
            tool_call_id = msg.get("tool_call_id")
            if tool_call_id:
                tool_call_ids.add(tool_call_id)

    # 第二遍：修复AIMessage中的tool_calls
    for msg in messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            # 过滤掉没有对应ToolMessage的tool_calls
            valid_tool_calls: List[Dict[str, Any]] = []
            removed_calls: List[str] = []

            for tool_call in msg.get("tool_calls", []):
                tool_call_id = tool_call.get("id")
                if tool_call_id in tool_call_ids:
                    valid_tool_calls.append(tool_call)
                elif tool_call_id:
                    removed_calls.append(tool_call_id)

            # 记录修复信息
            if removed_calls:
                print(
                    f"🔧 修复消息历史：移除了 {len(removed_calls)} 个不完整的工具调用: {removed_calls}"
                )

            # 更新消息
            if valid_tool_calls:
                msg_copy = msg.copy()
                msg_copy["tool_calls"] = valid_tool_calls
                fixed_messages.append(msg_copy)
            elif msg.get("content"):  # 如果没有有效的tool_calls但有content，保留消息
                msg_copy = msg.copy()
                msg_copy.pop("tool_calls", None)  # 移除空的tool_calls
                fixed_messages.append(msg_copy)
            # 如果既没有有效tool_calls也没有content，跳过这条消息
        else:
            # 非assistant消息或没有tool_calls的消息直接保留
            fixed_messages.append(msg)

    return fixed_messages


async def langgraph_supervisor_agent(
    messages: List[Dict[str, Any]],
    canvas_id: str,
    session_id: str,
    tool_list: list[ToolInfo | dict],
) -> None:
    """多智能体处理函数

    Args:
        messages: 消息历史
        canvas_id: 画布ID
        session_id: 会话ID
        text_model: 文本模型配置
        tool_list: 工具模型配置列表（图像或视频模型）
        system_prompt: 系统提示词
    """
    try:
        # 0. 修复消息历史
        # fixed_messages = _fix_chat_history(messages)

        # 2. 文本模型
        # text_model_instance = _create_text_model(text_model)

        # 3. 创建智能体
        # agents = AgentManager.create_agents(
        #     text_model_instance,
        #     tool_list,  # 传入所有注册的工具
        #     system_prompt or ""
        # )
        # agent_names = [agent.name for agent in agents]
        # print('👇agent_names', agent_names)
        # last_agent = AgentManager.get_last_active_agent(
        #     fixed_messages, agent_names)
        #
        # print('👇last_agent', last_agent)

        # 4. 创建智能体群组
        # swarm = create_swarm(
        #     agents=agents,  # type: ignore
        #     default_active_agent=last_agent if last_agent else agent_names[0]
        # )

        # 5. 创建上下文
        context = {
            "canvas_id": canvas_id,
            "session_id": session_id,
            "configurable": {"thread_id": session_id},
            "tool_list": tool_list,
        }

        # TODO 创建智能体
        if settings.repo_type == "postgres":

            db_uri = f"postgresql://{settings.postgres.username}:{settings.postgres.password.get_secret_value()}@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.database}"
            # db_uri = settings.postgres_dsn
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
                agent = build_creative_assistant(checkpointer=checkpointer)
                # 6. 流处理
                processor = StreamProcessor(session_id, send_to_websocket)  # type: ignore
                await processor.process_stream(
                    agent,
                    messages,
                    context,
                )
        else:
            agent = build_creative_assistant(checkpointer=memory_checkpointer)
            # 6. 流处理
            processor = StreamProcessor(session_id, send_to_websocket)  # type: ignore
            await processor.process_stream(
                agent,
                messages,
                context,
            )

    except Exception as e:
        await _handle_error(e, session_id)


def _create_text_model(text_model: ModelInfo) -> Any:
    """创建语言模型实例"""
    model = text_model.get("model")
    provider = text_model.get("provider")
    url = text_model.get("url")
    api_key = settings.providers.openai.api_key

    # TODO: Verify if max token is working
    # max_tokens = text_model.get('max_tokens', 8148)

    if provider == "ollama":
        pass

    else:
        # Create httpx client with SSL configuration for ChatOpenAI
        print(url)
        print(api_key)
        return ChatOpenAI(
            model=model,
            api_key=api_key,  # type: ignore
            timeout=300,
            base_url=url,
            temperature=0,
            # max_tokens=max_tokens, # TODO: 暂时注释掉有问题的参数
        )


async def _handle_error(error: Exception, session_id: str) -> None:
    """处理错误"""
    print("Error in langgraph_agent", error)
    tb_str = traceback.format_exc()
    print(f"Full traceback:\n{tb_str}")
    traceback.print_exc()

    await send_to_websocket(
        session_id, cast(Dict[str, Any], {"type": "error", "error": str(error)})
    )
