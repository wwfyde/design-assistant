import asyncio
import json

from api.deps import (
    get_canvas_service,
    get_chat_service,
    handle_chat,
)
from api.schemas.canvas import CanvasCreate
from api.services.canvas import CanvasService
from api.services.chat import ChatService
from fastapi import APIRouter
from fastapi.params import Depends
from starlette.requests import Request

router = APIRouter()


@router.get("/list")
async def list_canvases(
    canvas_service: CanvasService = Depends(get_canvas_service),
):
    return await canvas_service.get_canvases()


@router.post("/create")
async def create_canvas(
    canvas: CanvasCreate,
    canvas_service: CanvasService = Depends(get_canvas_service),
    chat_service: ChatService = Depends(get_chat_service),
    # checkpointer = Depends(get_checkpointer_async),
):
    # canvas = ChatRequest.model_validate(canvas_create)
    # asyncio.create_task(handle_chat(canvas, chat_service))
    asyncio.create_task(handle_chat(canvas, chat_service))
    await canvas_service.create_canvas(canvas)
    return {"id": canvas.canvas_id}


@router.get("/{id}")
async def get_canvas(
    id: str, canvas_service: CanvasService = Depends(get_canvas_service)
):
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
