import uuid
from io import BytesIO
from typing import Literal, Optional

import requests
from google import genai
from langchain_core.tools import tool
from PIL import Image
from pydantic import BaseModel, Field

from lib import settings, upload_image
from tools.images import image_create_with_gemini as image_create_with_gemini_tool

api_key = settings.providers.gemini.api_key
http_options = genai.types.HttpOptions(
    client_args={"proxy": settings.proxy_url},
    async_client_args={"proxy": settings.proxy_url},
)

client = genai.Client(api_key=api_key, http_options=http_options)


class GeminiArgs(BaseModel):
    image_urls: list[str] | str | None = Field(
        None,
        description="image_urls, optional, when multiple image urls passed,  split them with commas.",
    )
    prompt: str = Field(
        description="Required. The prompt for image generation. If you want to edit an image, please describe what you want to edit in the prompt."
    )
    aspect_ratio: Optional[str] = Field(
        None,
        description="""Optional. Aspect ratio of the generated images. Supported values are
      "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", and "21:9".""",
    )
    image_size: Literal["1K", "2K", "4K"] = Field(
        None,
        description="""Optional. Specifies the size of generated images. Supported
      values are `1K`, `2K`, `4K`. If not specified, the model will use default
      value `1K`.""",
    )


@tool(
    "image_create_with_gemini",
    description="Image Creation tool, generate or edit image With Google Gemini(aka Nano Banana) model using prompt and  image_urls. pass prompt with simple and specific instruction text, pass image with image_urls. Use this model for high-quality image modification.",
    args_schema=GeminiArgs,
)
def image_create_with_gemini(
    prompt: str,
    image_urls: str | None = None,
    aspect_ratio: str | None = None,
    image_size: Literal["1K", "2K", "4K"] | None = "1K",
) -> str:
    return image_create_with_gemini_tool(
        prompt, image_urls=image_urls, aspect_ratio=aspect_ratio, image_size=image_size
    )


def magic_generate_with_gemini(*, prompt: str | None = None, image_url: str) -> list[dict]:
    if not prompt:
        prompt = "理解图片上的视觉指令并生图"

    if image_url.startswith("http"):
        image_bytes = requests.get(image_url).content
        pil_image = Image.open(BytesIO(image_bytes))
    else:
        base_image_path = settings.data_dir.joinpath("files")
        image = base_image_path.joinpath(image_url)
        pil_image = Image.open(image)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[prompt, pil_image],
    )
    image_urls = []
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image_bytes = part.inline_data.data
            ext = part.inline_data.mime_type.split("/")[-1].replace("jpeg", "jpg")
            filename = f"{str(uuid.uuid4())}.{ext}"
            url = upload_image(filename, data=image_bytes, prefix="creative", rename=False)

            image = Image.open(BytesIO(part.inline_data.data))
            width, height = image.size
            image_urls.append(
                dict(
                    image_url=url,
                    mime_type=part.inline_data.mime_type,
                    width=width,
                    height=height,
                )
            )
            # save_path = settings.temp_dir / "generated_image2.png"
            #
            # image.save(save_path)
            # image.show()
            print(f"Image saved to {url}")
    return image_urls


if __name__ == "__main__":
    magic_generate_with_gemini(image_url="unknown.png")
