import uuid
from io import BytesIO
from typing import Literal

import requests
from google import genai
from google.genai import types
from PIL import Image

from lib import settings, upload_image
from lib.image import parse_data_url_to_bytes

api_key = settings.providers.gemini.api_key

http_options = genai.types.HttpOptions(
    client_args={"proxy": settings.proxy_url},
    async_client_args={"proxy": settings.proxy_url},
)
client = genai.Client(api_key=api_key, http_options=http_options)


def image_create_with_gemini(
    prompt: str,
    *,
    image_urls: str | list | None = None,
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", "21:9"]
    | None = None,
    image_size: Literal["1K", "2K", "4K"] | None = "2K",
):
    if isinstance(image_urls, str):
        image_list = [
            i.strip() for i in image_urls.replace("，", ",").split(",") if i.strip()
        ]
    elif image_urls is None:
        image_list = []
    else:
        image_list = image_urls

    new_urls: list[bytes] = []
    for item in image_list:
        # 处理本地文件
        if item.startswith("data:") and "base64;" in item:
            image_bytes = parse_data_url_to_bytes(item)
            new_urls.append(image_bytes)
        elif item.startswith("http"):
            content = requests.get(item).content
            new_urls.append(content)
        # 绝对路径
        elif item.startswith("/"):
            pass
        else:
            filename = item
            local_file_path = settings.data_dir / "files" / filename
            content = local_file_path.read_bytes()

            # new = upload_image(filename, content, prefix="files", rename=False)
            new_urls.append(content)

    image_list = new_urls

    client = genai.Client(api_key=api_key)
    try:
        image_pils = []
        for image in image_list:
            image_bytes = BytesIO(image)
            image_pil = Image.open(image_bytes)
            image_pils.append(image_pil)

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[prompt, *image_pils],
            config=types.GenerateContentConfig(
                # response_modalities=["IMAGE"],
                response_modalities=["Text", "Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,  # "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", and "21:9"
                    image_size=image_size,  # Literal["1K", "2K", "4K"]
                    # number_of_images=4,
                    # output_mime_type=
                ),
            ),
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

            return f"![image]({image_url})"

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
        # model="gemini-3-pro-image-preview",
        model="gemini-2.5-flash-image-preview",
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
    # magic_generate_with_gemini(image_url="unknown.png")
    result = image_create_with_gemini("将图片改成写实风格", image_urls="img.png", aspect_ratio="2:3")
    print(result)
