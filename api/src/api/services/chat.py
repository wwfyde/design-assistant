import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import uuid_utils as uuid
from api.core.memory import AppStore
from api.domain.chat import Chat, ChatMessage, ChatSession
from api.models import (
    Chat as ChatModel,
)
from api.models import (
    ChatMessage as ChatMessageModel,
)
from api.models import (
    ChatSession as ChatSessionModel,
)
from api.schemas.chat import ChatCreate, MagicCreate, SessionCreate
from api.services.stream import add_stream_task, remove_stream_task
from api.services.websocket import broadcast_session_update, send_to_websocket
from lib.image import parse_data_url
from sqlalchemy import Insert, delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from tools.images.gemini import magic_generate_with_gemini


class ChatRepo(ABC):
    @abstractmethod
    async def create_chat(self, id: int, name: str):
        pass

    @abstractmethod
    def create_chat(self, id: int, name: str):
        pass

    @abstractmethod
    def create_message(
        self,
        session_id: str,
        role: str,
        message: str,
        message_id: str = None,
        lc_id: str = None,
    ):
        pass

    @abstractmethod
    async def create_message_async(self, message: ChatCreate):
        pass

    @abstractmethod
    def chat_message(self, message: ChatCreate):
        pass

    @abstractmethod
    async def get_chat_history(self, session_id: str):
        pass

    @abstractmethod
    async def save_chat(self, chat: Chat) -> Chat:
        pass

    @abstractmethod
    async def delete_chat(self, id: int) -> bool:
        pass

    @abstractmethod
    async def get_sessions(self, canvas_id: str):
        pass

    @abstractmethod
    async def create_chat_session(self, session_create: SessionCreate) -> ChatSession:
        pass

    @abstractmethod
    def get_latest_chat_message(self):
        pass


class InMemoryChatRepo(ChatRepo):
    def __init__(self, store: AppStore):
        self.chat: dict[int, Chat] = store.chat
        self.chat_session: dict[str, ChatSession] = store.chat_session
        self.chat_message: dict[str, ChatMessage] = store.chat_message
        self.next_id = 1

    async def create_chat(self, id: int, name: str) -> Chat:
        self.chat[id] = Chat(id=id, name=name)
        return self.chat[id]

    async def chat_message(self, message: ChatCreate):
        chat = self.chat.get(message.chat_id)
        if chat:
            chat.messages.append(message)
        return chat

    async def get_chat_history(self, session_id: str) -> list[dict]:
        messages = []

        matched_messages = [
            message
            for message in self.chat_message.values()
            if message.session_id == session_id
        ]
        messages_raw = sorted(matched_messages, key=lambda m: str(m.created_at))
        for chat_message in messages_raw:
            if chat_message.message:
                try:
                    msg = json.loads(chat_message.message)
                    messages.append(msg)
                except:
                    pass
        return messages

    async def save_chat(self, chat: Chat) -> Chat:
        self.chat[chat.id] = chat
        return chat

    async def delete_chat(self, id: int) -> bool:
        if id in self.chat:
            del self.chat[id]
            return True
        return False

    async def get_sessions(self, canvas_id: str) -> list[ChatSession]:
        return [
            session
            for session in self.chat_session.values()
            if session.canvas_id == canvas_id
        ]
        pass

    async def create_chat_session(self, session_create: SessionCreate) -> ChatSession:
        session_id = session_create.id
        session = ChatSession.model_validate(session_create)
        self.chat_session[session_id] = session
        return session

    async def create_message(
        self,
        session_id: str,
        role: str,
        message: str,
        message_id: str = None,
        lc_id: str = None,
    ):
        id = message_id or str(uuid.uuid4())
        chat_message = ChatMessage(
            id=id, session_id=session_id, role=role, message=message, lc_id=lc_id
        )
        self.chat_message[id] = chat_message

        return chat_message


class PostgresChatRepo(ChatRepo):
    def __init__(self, session: Session, asession: AsyncSession):
        self.session = session
        self.asession = asession

    async def create_chat(self, id: int, name: str) -> Chat:
        db_chat = ChatModel(id=id, name=name)
        self.session.add(db_chat)
        self.session.commit()
        self.session.refresh(db_chat)
        chat = Chat.model_validate(db_chat)
        return chat

    async def chat_message(self, message: ChatCreate):
        pass

    async def get_chat_history(self, session_id: str) -> list[dict]:
        stmt = (
            select(ChatMessageModel)
            .where(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.id)
        )
        result = self.session.execute(stmt)
        rows: list[ChatMessageModel] = result.scalars().all()
        messages = [json.loads(row.message) for row in rows]
        return messages
        pass

    async def save_chat(self, chat: Chat) -> Chat:
        chat_db = ChatModel(**chat.model_dump(exclude_unset=True))
        self.session.add(chat_db)
        self.session.commit()
        self.session.refresh(chat_db)
        return Chat.model_validate(chat_db)

    async def delete_chat(self, id: int) -> bool:
        select_stmt = select(ChatModel).where(ChatModel.id == id)
        result = self.session.execute(select_stmt)
        chat_db = result.scalars().one_or_none()
        if not chat_db:
            return False
        stmt = delete(ChatModel).where(ChatModel.id == id)
        self.session.execute(stmt)
        self.session.commit()
        return True
        pass

    async def get_sessions(self, canvas_id: str) -> list[ChatSession]:
        stmt = select(ChatSessionModel).where(ChatSessionModel.canvas_id == canvas_id)
        result = self.session.execute(stmt)
        sessions_raw = result.scalars().all()
        sessions = [ChatSession.model_validate(s) for s in sessions_raw]
        return sessions

    async def create_chat_session(self, session_create: SessionCreate) -> ChatSession:
        session_db = self.session.get(ChatSessionModel, session_create.id)
        if session_db:
            update_stmt = (
                update(ChatSessionModel)
                .where(ChatSessionModel.id == session_create.id)
                .values(**session_create.model_dump(exclude_unset=True))
            )
            self.session.execute(update_stmt)
        else:
            session_create.session_id = session_create.id
            session_db = ChatSessionModel(
                **session_create.model_dump(exclude_unset=True)
            )
            self.session.add(session_db)
        self.session.commit()
        self.session.refresh(session_db)
        session = ChatSession.model_validate(session_db)
        return session

        pass

    def create_message(
        self,
        session_id: str,
        role: str,
        message: str,
        message_id: str = None,
        lc_id: str = None,
    ):
        id = message_id or str(uuid.uuid7())
        # Check if message exists

        stmt: Insert = insert(ChatMessageModel).values(
            id=id, session_id=session_id, role=role, message=message, lc_id=lc_id
        )
        stmt = stmt.on_conflict_do_update(
            # constraint="id",
            index_elements=["lc_id"],
            set_={
                "session_id": session_id,
                "role": role,
                "message": message,
                "updated_at": func.now(),
            },
        )
        stmt = stmt.returning(ChatMessageModel)
        result = self.session.execute(stmt)
        row = result.scalar_one()
        self.session.commit()
        self.session.refresh(row)

        return row

        stmt = select(ChatMessageModel).where(ChatMessageModel.id == id)
        result = self.session.execute(stmt)
        existing_message = result.scalars().one_or_none()
        stmt

        if existing_message:
            # Update existing message
            existing_message.message = message
            existing_message.role = role
            # existing_message.session_id = session_id # Usually session_id doesn't change
            self.session.commit()
            self.session.refresh(existing_message)
            return ChatMessage.model_validate(existing_message)
        else:
            chat_message_db = ChatMessageModel(
                id=id, session_id=session_id, role=role, message=message
            )
            self.session.add(chat_message_db)
            self.session.commit()
            self.session.refresh(chat_message_db)
            session = ChatMessage.model_validate(chat_message_db)
            return session

    async def create_message_async(
        self, session_id: str, role: str, message: str, message_id: str = None
    ):
        id = message_id or str(uuid.uuid7())

        # Check if message exists
        stmt = select(ChatMessageModel).where(ChatMessageModel.id == id)
        result = await self.asession.execute(stmt)
        existing_message = result.scalars().one_or_none()

        if existing_message:
            # Update existing message
            existing_message.message = message
            existing_message.role = role
            await self.asession.commit()
            await self.asession.refresh(existing_message)
            return ChatMessage.model_validate(existing_message)
        else:
            chat_message_db = ChatMessageModel(
                id=id, session_id=session_id, role=role, message=message
            )
            self.asession.add(chat_message_db)
            await self.asession.commit()
            await self.asession.refresh(chat_message_db)
            session = ChatMessage.model_validate(chat_message_db)
            return session

        pass

    def get_latest_chat_message(self):
        stmt = select(ChatMessageModel).order_by(ChatMessageModel.id.desc()).limit(1)
        result = self.session.execute(stmt)
        row = result.scalars().first()
        return row


class ChatService:
    def __init__(self, repo: ChatRepo):
        self.repo = repo

    async def create_chat_session(self, session: SessionCreate):
        await self.repo.create_chat_session(session)

        pass

    def create_message(
        self,
        session_id: str,
        role: str,
        message: str,
        message_id: str = None,
        lc_id: str = None,
    ):
        """Save a chat message"""

        return self.repo.create_message(
            session_id, role, message, message_id, lc_id=lc_id
        )

    def get_latest_chat_message(self):
        return self.repo.get_latest_chat_message()

    async def get_chat_history(self, session_id: str) -> list[Chat]:
        """Get chat history for a session"""
        return await self.repo.get_chat_history(session_id)

    async def get_sessions(self, canvas_id: str) -> list[ChatSession]:
        """List all chat sessions"""
        return await self.repo.get_sessions(canvas_id)

    async def create_message_async(
        self, session_id: str, role: str, message: str, message_id: str = None
    ):
        """Save a chat message"""

        return await self.repo.create_message_async(
            session_id, role, message, message_id
        )


# services/magic_service.py

# Import necessary modules


# Import service modules


async def handle_magic(magic: MagicCreate, chat_service: ChatService) -> None:
    """
    Handle an incoming magic generation request.

    Workflow:
    - Parse incoming magic generation data.
    - Run Agents.
    - Save magic session and messages to the database.
    - Notify frontend via WebSocket.

    Args:
        data (dict): Magic generation request data containing:
            - messages: list of message dicts
            - session_id: unique session identifier
            - canvas_id: canvas identifier (contextual use)
            - text_model: text model configuration
            - tool_list: list of tool model configurations (images/videos)
    """
    # Extract fields from incoming data
    messages: List[Dict[str, Any]] = magic.messages
    session_id: str = magic.session_id
    canvas_id: str = magic.canvas_id

    # print('✨ magic_service 接收到数据:', {
    #     'session_id': session_id,
    #     'canvas_id': canvas_id,
    #     'messages_count': len(messages),
    # })

    # If there is only one message, create a new magic session
    if len(messages) == 1:
        # create new session
        prompt = messages[0].get("content", "")
        title = prompt[:200] if isinstance(prompt, str) else ""
        magic.title = title
        session = SessionCreate.model_validate(magic)
        session.id = session_id
        # TODO: 配置 magic model 和  magic provider
        session.model = "gpt-4.1-mini"
        session.provider = "openai"
        await chat_service.create_chat_session(session)

    # Save user message to database
    if len(messages) > 0:
        chat_service.create_message(
            session_id,
            messages[-1].get("role", "user"),
            json.dumps(messages[-1], ensure_ascii=False),
            messages[-1].get("id"),
            messages[-1].get("id"),
        )

    # Create and start magic generation task

    task = asyncio.create_task(magic_generation(magic, chat_service))

    # Register the task in stream_tasks (for possible cancellation)
    add_stream_task(session_id, task)
    try:
        # Await completion of the magic generation task
        await task
    except asyncio.exceptions.CancelledError:
        print(f"🛑Magic generation session {session_id} cancelled")
    finally:
        # Always remove the task from stream_tasks after completion/cancellation
        remove_stream_task(session_id)
        # Notify frontend WebSocket that magic generation is done
        await send_to_websocket(session_id, {"type": "done"})

    print("✨ magic_service 处理完成")


async def magic_generation(magic: MagicCreate, chat_service: ChatService):
    # Save AI response to database
    try:
        user_message = magic.messages[-1]
        image_content: str = ""
        ai_response = None
        prompt = None

        if isinstance(user_message.get("content"), list):
            for content_item in user_message["content"]:
                if content_item.get("type") == "image_url":
                    image_content = content_item.get("image_url", {}).get("url", "")
                if content_item.get("type") == "text":
                    prompt = content_item.get("text", None)
        # print(f"{image_content}")
        # print(f"{type(image_content)}")
        if not image_content:
            ai_response = {
                "role": "assistant",
                "content": [{"type": "text", "text": "✨ not found input image"}],
            }
        else:
            # 使用 seedream 工具魔法生图
            # 理解草图/涂鸦和手绘, 辅助线的视觉, 生成prompt
            magic_prompt = """
            理解视觉意图. 基于我绘制的草图, 然后基于理解到的意图, 并逐步创作 
            """
            magic_prompt = """
            理解视觉意图或视觉指令. 理解图像中的草图,涂鸦或视觉指令并生成图像
            """
            if prompt:
                magic_prompt = f"{magic_prompt}\n{prompt}"
            url = parse_data_url(image_content)
            image_info = magic_generate_with_gemini(
                # prompt=magic_prompt,
                # prompt=magic_prompt,
                image_url=url,
            )

            # Broadcast image generation message to frontend
            # TODO
            image_info = image_info[0]["image_url"]
            await broadcast_session_update(
                magic.session_id,
                magic.canvas_id,
                {
                    "type": "image_generated",
                    "element": "",
                    "file": "",
                    "image_url": image_info,
                },
            )

            ai_response = {
                "role": "assistant",
                "content": f"图像生成完成 ![image]({image_info})",
            }
    except Exception as exc:
        ai_response = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": f"✨ Magic Generation Error: {str(exc)}"}
            ],
        }
    message_id = str(uuid.uuid7())
    chat_service.create_message(
        magic.session_id,
        "assistant",
        json.dumps(ai_response, ensure_ascii=False),
        message_id,
        message_id,
    )

    # Send messages to frontend immediately
    all_messages = magic.messages + [ai_response]
    await send_to_websocket(
        magic.session_id, {"type": "all_messages", "messages": all_messages}
    )
