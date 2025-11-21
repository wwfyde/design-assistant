from fastapi import APIRouter
from pydantic import BaseModel
from tools.images.seedream import image_create_with_seedream

router = APIRouter()


@router.get("/")
async def get_tools():
    pass


class SeedreamRequest(BaseModel):
    prompt: str
    image_urls: list[str] | str | None = None
    aspect_ratio: str | None = None


@router.post("/image_create_with_seedream")
async def call_image_create_with_seedream(seedream: SeedreamRequest):
    resp = image_create_with_seedream(
        prompt=seedream.prompt,
        image_urls=seedream.image_urls,
        aspect_ratio=seedream.aspect_ratio,
    )
    return resp


@router.get("/{id}")
async def get_tool_by_id(id: str):
    pass
