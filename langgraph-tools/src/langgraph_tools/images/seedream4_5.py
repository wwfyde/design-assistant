from typing import Literal, Optional

from pydantic import Field, BaseModel
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool

from api.services.websocket import broadcast_session_update
from tools.images.seedream4_5 import (
    image_create_with_seedream4_5 as image_create_with_seedream_tool,
)


class SeedreamArgs(BaseModel):
    image_urls: list[str] | str | None = Field(
        None,
        description="image_urls or image file name, optional, when multiple image urls passed,  split them with commas. 网络图片传入图片url, 本地文件传入文件. 如果只有文件名默认当做本地文件.",
    )
    prompt: str = Field(
        description="Required. The prompt for image generation. If you want to edit an image, please describe what you want to edit in the prompt."
    )
    aspect_ratio: str | None = Field(
        None,
        description="Optional. Aspect ratio of the image, only these values are allowed: 1:1, 16:9, 4:3, 3:4, 2:3, 3:2 9:16, 21:9. 支持传入传入自定义比例, 比如 1:3, 1024×3072 ",
    )
    image_size: Literal["2K", "4K", "2k", "4k"] | None = Field(
        "2K", description="Optional. 图像分辨率, 默认2K, 支持设置为4K"
    )


@tool(
    "image_create_with_seedream4_5",
    description="Image Creation, Generate or Edit Image with ByteDance Seedream model using  prompt , image_urls, aspect_ratio. image_urls may be local file, input it with filename(img_xx.png). Response multiple images. Use this model for: 1. adding or removing elements, 2. Inpainting (Semantic masking), 3. Style transfer, 4. Generate images. Supports output multiple images.",
    args_schema=SeedreamArgs,
)
async def image_create_with_seedream4_5(
    runtime: ToolRuntime,
    prompt: str,
    image_urls: list[str] | str | None = None,
    aspect_ratio: str | None = None,
    image_size: Literal["2K", "4K", "2k", "4k"] | None = "2K",
) -> str:

    image_tool_response = image_create_with_seedream_tool(
        image_urls=image_urls,
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        image_size=image_size.upper() if image_size else None,
    )
    if image_tool_response.images:
        for image in image_tool_response.images:
            await broadcast_session_update(
                runtime.context.session_id,
                runtime.context.canvas_id,
                {
                    "type": "image_generated",
                    "element": "",
                    "file": "",
                    "image_url": image.url,
                },
            )
    return image_tool_response.content


if __name__ == "__main__":
    pass
