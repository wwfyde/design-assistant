import uuid
from io import BytesIO
from typing import Optional

import requests
from google import genai
from langchain_core.tools import tool
from PIL import Image
from pydantic import BaseModel, Field

from lib import settings, upload_image

api_key = settings.providers.gemini.api_key

client = genai.Client(api_key=api_key)


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
        description="Required. Aspect ratio of the image, only these values are allowed: 1:1, 16:9, 4:3, 3:4, 9:16. Choose the best fitting aspect ratio according to the prompt. Best ratio for posters is 3:4",
    )


@tool(
    "image_create_with_gemini",
    description="Image Creation tool, generate or edit image With Google Gemini(aka Nano Banana) model using prompt and  image_urls. pass prompt with simple and specific instruction text, pass image with image_urls. Use this model for high-quality image modification.",
    args_schema=GeminiArgs,
)
def image_create_with_gemini(prompt: str, image_urls: str):
    if image_urls:
        # image_list = [ i.strip() for i in image_urls.split(",")]
        image_list = [
            i.strip() for i in image_urls.replace("，", ",").split(",") if i.strip()
        ]
    else:
        image_list = []

    client = genai.Client(api_key=api_key)
    try:
        image_pils = []
        for image in image_list:
            image_bytes = BytesIO(requests.get(image).content)
            image_pil = Image.open(image_bytes)
            image_pils.append(image_pil)

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt, *image_pils],
        )
        image_parts = [
            (part.inline_data.data, part.inline_data.mime_type)
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]
        if image_parts:
            content, mime_type = image_parts[0]
            extension = mime_type.split("/")[-1].replace("jpeg", "jpg")
            # print(f"Image format: {format}")
            image_url = upload_image(f"{str(uuid.uuid4())}.{extension}", content)

            return image_url

        else:
            return None

    except Exception as e:
        return f"工具调用失败, 错误提示: {e}"


def magic_generate_with_gemini(
    *, prompt: str | None = None, image_url: str
) -> list[dict]:
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
            url = upload_image(
                filename, data=image_bytes, prefix="creative", rename=False
            )

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
