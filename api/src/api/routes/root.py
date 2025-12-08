from fastapi import APIRouter
from fastapi.params import Depends

from api.deps import get_chat_service

# services
from api.domain.model import ModelInfo
from api.domain.tool import ToolInfo
from api.services.chat import ChatService

# from services.config_service import config_service
# from services.db_service import db_service

router = APIRouter()


# List all LLM models
@router.get("/list_models")
async def get_models() -> list[ModelInfo]:
    return [
        ModelInfo(
            provider="openai", model="gpt-4.1-mini", url="https://api.openai.com/v1", type="text", display_name="GPT"
        ),
        ModelInfo(provider="ark", model="seed-1.6", url="https://api.openai.com/v1", type="text", display_name="豆包"),
        ModelInfo(
            provider="deepseek",
            model="deepseek-v3.2",
            url="https://deepseek.com",
            type="text",
            display_name="DeepSeek",
        ),
        # ModelInfo(
        #     provider="gemini",
        #     model="gemini-3-pro-preview",
        #     url="https://api.openai.com/v1",
        #     type="text",
        #     display_name="Gemini",
        # ),
        ModelInfo(
            provider="dashscope",
            model="qwen-plus",
            url="https://api.openai.com/v1",
            type="text",
            display_name="千问",
        ),
    ]


@router.get("/list_tools")
async def list_tools() -> list[ToolInfo]:
    # TODO 动态获取工具列表
    return [
        ToolInfo(
            provider="seedream",
            id="image_create_with_seedream",
            type="image",
            display_name="即梦4.0",
        ),
        ToolInfo(
            provider="seedream",
            id="image_create_with_seedream4_5",
            type="image",
            display_name="即梦4.5",
        ),
        ToolInfo(
            provider="gemini",
            id="image_create_with_gemini",
            type="image",
            display_name="Nano Banana",
        ),
        # ToolInfo(
        #     provider="openai",
        #     id="gpt",
        #     type="image",
        #     display_name="GPT-1",
        # ),
        # ToolInfo(
        #     provider="qwen",
        #     id="gpt1",
        #     type="image",
        #     display_name="千问Image",
        # ),
        # ToolInfo(
        #     provider="flux",
        #     id="gpt3",
        #     type="image",
        #     display_name="Flux Kontext",
        # ),
    ]


@router.get("/list_chat_sessions/{canvas_id}")
async def list_chat_sessions(
    canvas_id: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.get_sessions(canvas_id=canvas_id)


@router.get("/chat_session/{session_id}")
async def get_chat_session(session_id: str, chat_service: ChatService = Depends(get_chat_service)):
    """
    获取指定会话的聊天历史记录

    """
    return await chat_service.get_chat_history(session_id=session_id)
