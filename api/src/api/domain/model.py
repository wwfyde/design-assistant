from typing import Literal

from pydantic import BaseModel


class ModelInfo(BaseModel):
    provider: str
    model: str  # For tool type, it is the function name
    url: str | None
    type: Literal["text", "image", "tool", "video"]
    display_name: str
