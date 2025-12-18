import uuid
from typing import Literal

from pydantic import Field, BaseModel


class ToolResponse(BaseModel):
    content: str = Field


class ImageInfo(BaseModel):
    # index: int = 1
    url: str
    id: uuid.UUID | str
    filename: str
    original_filename: str | None = None
    file_size: int | None = None
    mime_type: Literal["image/png", "image/jpeg", "image/webp"]
    image_format: Literal["png", "jpg", "webp"] | None = None
    width: int | None = None
    height: int | None = None
    content: str | None = None
    storage_key: str | None = None
    sha256: str | None = None

    @property
    def size(self) -> tuple[int, int]:
        """Python 代码中使用的便捷属性"""
        return self.width, self.height


class ImageToolResponse(BaseModel):
    content: str = Field()
    success: bool = True
    error: str | None = None
    images: list[ImageInfo] | None = None
