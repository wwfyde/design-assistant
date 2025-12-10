from typing import Literal

from pydantic import Field, BaseModel
from langgraph.prebuilt import ToolRuntime
from langchain_core.tools import tool

from tools.images import (
    image_edit_with_qwen as image_edit_with_qwen_tool,
    image_generate_with_qwen as image_generate_with_qwen_tool,
)
from api.services.websocket import broadcast_session_update


class QwenArgs(BaseModel):
    image_urls: list[str] | str | None = Field(
        None,
        description="image_urls, optional, when multiple image urls passed,  split them with commas.",
    )
    prompt: str = Field(
        description="Required. The prompt for image generation. If you want to edit an image, please describe what you want to edit in the prompt."
    )
    aspect_ratio: str | None = Field(
        None,
        description="""Optional. Aspect ratio of the generated images. Supported values are
      "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", and "21:9".""",
    )


@tool(
    "image_create_with_qwen",
    description="Image Creation tool, generate or edit image With Qwen model using prompt and  image_urls. pass prompt"
    " with simple and specific instruction text, pass image with image_urls. "
    "Use this model for high-quality image modification.",
    args_schema=QwenArgs,
)
async def image_create_with_qwen(
    runtime: ToolRuntime,
    *,
    prompt: str,
    image_urls: list[str] | str | None = None,
    aspect_ratio: str | None = None,
) -> str:

    if image_urls:
        image_tool_response = image_edit_with_qwen_tool(prompt=prompt, image_urls=image_urls)
        if image_tool_response.images:
            await broadcast_session_update(
                runtime.context.session_id,
                runtime.context.canvas_id,
                {
                    "type": "image_generated",
                    "element": "",
                    "file": "",
                    "image_url": image_tool_response.images[0].url,
                },
            )
        return image_tool_response.content
    else:
        image_tool_response = image_generate_with_qwen_tool(prompt=prompt, aspect_ratio=aspect_ratio)
        if image_tool_response.images:
            await broadcast_session_update(
                runtime.context.session_id,
                runtime.context.canvas_id,
                {
                    "type": "image_generated",
                    "element": "",
                    "file": "",
                    "image_url": image_tool_response.images[0].url,
                },
            )
        return image_tool_response.content
