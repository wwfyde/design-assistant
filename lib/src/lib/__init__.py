from .config import settings
from .image import upload_image
from .utils import get_current_date


def hello() -> str:
    return "Hello from lib!"


__all__ = ["settings", "hello", "get_current_date", "upload_image"]
