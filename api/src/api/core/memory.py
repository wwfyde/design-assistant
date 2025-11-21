import asyncio
from uuid import UUID

from api.domain.canvas import Canvas
from api.domain.chat import Chat, ChatMessage, ChatSession
from langgraph.checkpoint.memory import InMemorySaver

memory_checkpointer = InMemorySaver()


class AppStore:
    def __init__(self):
        self.canvas: dict[str | UUID, Canvas] = {}
        self.chat_session: dict[str | UUID, ChatSession] = {}
        self.chat: dict[str | UUID, Chat] = {}
        self.chat_message: dict[str | UUID, ChatMessage] = {}

        self.lock = asyncio.Lock()


memory_store = AppStore()
