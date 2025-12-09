from api.deps import get_chat_service, handle_chat
from api.schemas.chat import ChatRequest, MagicCreate
from api.services.chat import ChatService, handle_magic
from api.services.stream import get_stream_task
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/chat")
# @router.post("/magic/chat")
async def chat(chat: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    await handle_chat(chat, chat_service)
    return {"status": "done"}


@router.post("/cancel/{session_id}")
async def cancel_chat(session_id: str):
    """
    Endpoint to cancel an ongoing stream task for a given session_id.

    If the task exists and is not yet completed, it will be cancelled.

    Path parameter:
        session_id (str): The ID of the session whose task should be cancelled.

    Response:
        {"status": "cancelled"} if the task was cancelled.
        {"status": "not_found_or_done"} if no such task exists or it is already done.
    """
    task = get_stream_task(session_id)
    if task and not task.done():
        task.cancel()
        return {"status": "cancelled"}
    return {"status": "not_found_or_done"}


@router.post("/magic")
async def magic(
    magic: MagicCreate,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Endpoint to handle magic generation requests.

    Receives a JSON payload from the client, passes it to the magic handler,
    and returns a success status.

    Request body:
        JSON object containing magic generation data.

    Response:
        {"status": "done"}
    """
    await handle_magic(magic, chat_service)
    return {"status": "done"}


@router.post("/magic/cancel/{session_id}")
async def cancel_magic(session_id: str) -> dict[str, str]:
    """
    Endpoint to cancel an ongoing magic generation task for a given session_id.

    If the task exists and is not yet completed, it will be cancelled.

    Path parameter:
        session_id (str): The ID of the session whose task should be cancelled.

    Response:
        {"status": "cancelled"} if the task was cancelled.
        {"status": "not_found_or_done"} if no such task exists or it is already done.
    """
    task = get_stream_task(session_id)
    if task and not task.done():
        task.cancel()
        return {"status": "cancelled"}
    return {"status": "not_found_or_done"}
