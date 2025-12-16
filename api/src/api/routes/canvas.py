import json
import asyncio
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Header, Depends
from starlette.requests import Request

from lib import settings
from api.deps import handle_chat, get_chat_service, get_canvas_service
from api.services.chat import ChatService
from api.schemas.canvas import CanvasCreate, CanvasResponse
from api.services.canvas import CanvasService

router = APIRouter()


@router.get("/list", response_model=list[CanvasResponse])
async def list_canvases(
    canvas_service: CanvasService = Depends(get_canvas_service),
):
    return await canvas_service.get_canvases()


@router.get("/by/user_id/{user_id}", response_model=list[CanvasResponse])
async def get_canvas_by_user_id(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    user_id_header: str | None = Header(alias="User-Code", default=None),
    canvas_service: CanvasService = Depends(get_canvas_service),  # noqa: B008
):
    # 管理员
    if user_id_header in settings.admin_users:
        return await canvas_service.get_canvases(page=page, page_size=page_size)
    return await canvas_service.get_canvases(user_id=user_id_header, page=page, page_size=page_size)


@router.post("/create")
async def create_canvas(
    canvas: CanvasCreate,
    user_id: Annotated[str | None, Header(alias="User-Code")] = None,
    canvas_service: CanvasService = Depends(get_canvas_service),
    chat_service: ChatService = Depends(get_chat_service),
    # checkpointer = Depends(get_checkpointer_async),
):
    # canvas = ChatRequest.model_validate(canvas_create)
    # asyncio.create_task(handle_chat(canvas, chat_service))
    canvas.user_id = user_id
    asyncio.create_task(handle_chat(canvas, chat_service))
    await canvas_service.create_canvas(canvas)
    return {"id": canvas.canvas_id}


@router.get("/{id}")
async def get_canvas(id: str, canvas_service: CanvasService = Depends(get_canvas_service)):
    canvas = await canvas_service.get_canvas_data(id)
    return canvas


@router.post("/{id}/save")
async def save_canvas(
    id: str,
    request: Request,
    canvas_service: CanvasService = Depends(get_canvas_service),
):
    payload = await request.json()
    data_str = json.dumps(payload["data"])
    await canvas_service.save_canvas_data(id, data_str, payload["thumbnail"])
    return {"id": id}


@router.post("/{id}/rename")
async def rename_canvas(
    id: str,
    request: Request,
    canvas_service: CanvasService = Depends(get_canvas_service),
):
    data = await request.json()
    name = data.get("name")
    await canvas_service.rename_canvas(id, name)
    return {"id": id}


@router.delete("/{id}/delete")
async def delete_canvas(
    id: str,
    canvas_service: CanvasService = Depends(get_canvas_service),
):
    await canvas_service.delete_canvas(id)
    return {"id": id}
