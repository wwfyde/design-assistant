import asyncio
import json
from typing import Annotated, Any, AsyncGenerator, Generator, Optional

import uuid_utils as uuid
from agents.rednote_agent import (
    build_rednote_agent,
)
from agents.supervisor_agent import langgraph_supervisor_agent
from api.core.db import async_session, engine
from api.core.memory import memory_checkpointer, memory_store
from api.domain.model import ModelInfo
from api.domain.tool import ToolInfo
from api.schemas.chat import ChatRequest, SessionCreate
from api.services.canvas import CanvasService, InMemoryCanvasRepo, PostgresCanvasRepo
from api.services.chat import ChatService, InMemoryChatRepo, PostgresChatRepo
from api.services.stream import add_stream_task, remove_stream_task
from api.services.websocket import send_to_websocket
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from lib import settings

# canvas_service = CanvasService(store=memory_store)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
        # session 关闭 归还给连接池, 而不是真的关闭连接


def get_canvas_service(
    session: Annotated[Session, Depends(get_db)],
    asession: Annotated[AsyncSession, Depends(get_db_async)],
) -> CanvasService:
    if settings.repo_type == "in-memory":
        return CanvasService(InMemoryCanvasRepo(memory_store))
    elif settings.repo_type == "postgres":
        # pass the async_sessionmaker so the repo creates fresh AsyncSession per operation
        return CanvasService(PostgresCanvasRepo(session=session))
    else:
        return CanvasService(InMemoryCanvasRepo(memory_store))


# 使用类实例的不要使用Annotated
# CanvasServiceDep = Annotated[CanvasService, Depends(get_canvas_service)]


def get_chat_service(
    session: Annotated[Session, Depends(get_db)],
    asession: Annotated[AsyncSession, Depends(get_db_async)],
) -> ChatService:
    if settings.repo_type == "in-memory":
        return ChatService(InMemoryChatRepo(memory_store))
    elif settings.repo_type == "postgres":
        return ChatService(PostgresChatRepo(session=session, asession=asession))
    else:
        return ChatService(InMemoryChatRepo(memory_store))


def get_checkpointer() -> Generator[PostgresSaver, None, None]:
    # DB_URI = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    db_uri = f"postgresql://{settings.postgres.username}:{settings.postgres.password.get_secret_value()}@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.database}"

    with PostgresSaver.from_conn_string(db_uri) as checkpointer:
        checkpointer.setup()
        yield checkpointer


async def get_checkpointer_async() -> AsyncGenerator[AsyncPostgresSaver, None]:
    db_uri = f"postgresql://{settings.postgres.username}:{settings.postgres.password.get_secret_value()}@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.database}"
    async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
        yield checkpointer


# ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


def get_in_memory_checkpointer():
    return memory_checkpointer


def get_rednote_agent(checkpointer: PostgresSaver = Depends(get_checkpointer)):
    if settings.repo_type == "in-memory":
        checkpointer = memory_checkpointer

    rednote_agent = build_rednote_agent(checkpointer)

    return rednote_agent


#
# def get_creative_agent(checkpointer: PostgresSaver = Depends(get_checkpointer)):
#     if settings.repo_type == "in-memory":
#         checkpointer = memory_checkpointer
#
#     agent = build_creative_assistant(checkpointer)
#
#     return agent


async def handle_chat(data: ChatRequest, chat_service: ChatService) -> None:
    """
    Handle an incoming chat request.

    Workflow:
    - Parse incoming chat data.
    - Optionally inject system prompt.
    - Save chat session and messages to the database.
    - Launch langgraph_agent task to process chat.
    - Manage stream task lifecycle (add, remove).
    - Notify frontend via WebSocket when stream is done.

    Args:
        data (dict): Chat request data containing:
            - messages: list of message dicts
            - session_id: unique session identifier
            - canvas_id: canvas identifier (contextual use)
            - text_model: text model configuration
            - tool_list: list of tool model configurations (images/videos)
        chat_service: ChatService instance for chat operations
    """
    # Extract fields from incoming data
    messages: list[dict[str, Any]] = data.messages
    session_id: str = data.session_id
    canvas_id: str = data.canvas_id
    text_model: ModelInfo = data.text_model
    tool_list: list[ToolInfo] = data.tool_list

    # print("👇 chat_service got tool_list", tool_list)

    # TODO: save and fetch system prompt from db or settings config
    system_prompt: Optional[str] = data.system_prompt

    # If there is only one message, create a new chat session
    if len(messages) == 1:
        # create new session
        prompt = messages[0].get("content", "")
        # TODO: Better way to determin when to create new chat session.
        await chat_service.create_chat_session(
            SessionCreate(
                id=session_id,
                model=text_model.model,
                provider=text_model.provider,
                canvas_id=canvas_id,
                title=prompt[:200] if isinstance(prompt, str) else "",
            )
        )

        # TODO 保存用户发送的消息
        message = messages[-1]

        # 推荐优先使用服务端生成uuid
        message_id = message.get("id", str(uuid.uuid7()))
        role = message.get("role", "user")

        message_data = message.copy()  # 存储消息到数据库的message字段, 移除id
        message_data.pop("id", None)
        chat_service.create_message(
            session_id,
            role,
            json.dumps(message_data, ensure_ascii=False),
            message_id,
            lc_id=message_id,
        )

    # Create and start langgraph_agent task for chat processing
    # rednote_agent = get_rednote_agent(checkpointer=memory_checkpointer)
    # TODO: 支持多agent 切换
    task = asyncio.create_task(
        langgraph_supervisor_agent(
            messages, canvas_id, session_id, tool_list=tool_list, text_model=text_model
        )
    )
    #
    # # Register the task in stream_tasks (for possible cancellation)
    add_stream_task(session_id, task)
    try:
        # Await completion of the langgraph_agent task
        await task
    except asyncio.exceptions.CancelledError:
        print(f"🛑Session {session_id} cancelled during stream")
    finally:
        # Always remove the task from stream_tasks after completion/cancellation
        remove_stream_task(session_id)
        # Notify frontend WebSocket that chat processing is done
        await send_to_websocket(session_id, {"type": "done"})


header_scheme = APIKeyHeader(name="X-Api-Key")


async def verify_header_token(token: Annotated[str, Depends(header_scheme)]) -> str:
    if token != settings.simple_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid header token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
