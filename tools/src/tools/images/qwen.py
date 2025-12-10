import http
import json
from io import BytesIO
from http import HTTPStatus
from typing import Literal

import httpx
import requests
import uuid_utils as uuid
from PIL import Image
from dashscope import ImageSynthesis, MultiModalConversation

from lib import settings, upload_image
from tools.types import ImageInfo, ImageToolResponse

api_key = settings.providers.dashscope.api_key


def image_edit_with_qwen(
    *,
    prompt: str,
    image_urls: list[str] | str | None = None,
    negative_prompt: str | None = None,
) -> ImageToolResponse:
    if isinstance(image_urls, str):
        image_list = [i.strip() for i in image_urls.split(",") if i.strip()]
    elif image_urls is None:
        image_list = []
    else:
        image_list = image_urls

    new_urls = []
    for item in image_list:
        # 处理本地文件
        if item.startswith("data:") and "base64;" in item:
            pass
        elif item.startswith("http"):
            new_urls.append(item)
        # 绝对路径
        elif item.startswith("/"):
            pass
        else:
            filename = item
            local_file_path = settings.data_dir / "files" / filename
            content = local_file_path.read_bytes()

            new = upload_image(filename, content, prefix="files", rename=False)
            new_urls.append(new)

    image_list = new_urls
    image_content = [{"image": image_url} for image_url in image_list]
    content = [{"text": prompt}, *image_content]

    messages = [
        {
            "role": "user",
            "content": content,
        }
    ]

    try:
        resp = MultiModalConversation.call(
            api_key=api_key,
            model="qwen-image-edit",
            messages=messages,
            result_format="message",
            stream=False,
            watermark=False,
            negative_prompt=negative_prompt,
        )

        if resp.status_code == http.HTTPStatus.OK:
            contents: dict = resp.output.choices[0].message.get("content", [])

            temp_image_url = contents[0].get("image", "")
            image_bytes = httpx.get(temp_image_url, timeout=60).content
            pil = Image.open(BytesIO(image_bytes))
            width, height = pil.size
            img_format = pil.format.lower() or "png"
            image_id = uuid.uuid7()
            filename = f"{image_id}.{img_format.replace('jpeg', 'jpg')}"
            image_url = upload_image(filename, data=image_bytes, prefix="creative/qwen")
            image_info = dict(url=image_url, mime_type=f"image/{img_format}")
            return ImageToolResponse(
                content=json.dumps(image_info, ensure_ascii=False),
                success=True,
                images=[
                    ImageInfo(
                        url=image_url,
                        filename=filename,
                        id=str(image_id),
                        mime_type=f"image/{img_format}",  # noqa
                        width=width,
                        height=height,
                    )
                ],
            )
        else:
            return ImageToolResponse(
                content=f"同步调用失败, status_code: {resp.status_code}, code: {resp.code}, message: {resp.message}",
                success=False,
            )

    except Exception as e:
        return ImageToolResponse(content=f"工具调用失败, 错误提示: {e}", success=False)


def image_generate_with_qwen(
    *, prompt: str, negative_prompt: str | None = None, aspect_ratio: Literal["1:1", "4:3", "3:4", "16:9"] = None
) -> ImageToolResponse:
    aspect_ratio = aspect_ratio.replace("×", ":") if aspect_ratio else None
    if aspect_ratio == "1:1":
        width = 1328
        height = 1328
    elif aspect_ratio == "4:3":
        width = 1472
        height = 1140
    elif aspect_ratio == "3:4":
        width = 1140
        height = 1472
    elif aspect_ratio == "16:9":
        width = 1664
        height = 928
    elif aspect_ratio == "9:16":
        width = 928
        height = 1664
    else:
        width = 1328
        height = 1328

    resp = ImageSynthesis.call(
        api_key=api_key,
        model="qwen-image",
        prompt=prompt,
        n=1,
        size=f"{width}*{height}",
        negative_prompt=negative_prompt,
    )
    urls = []
    images = []
    if resp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图片
        for result in resp.output.results:
            content = requests.get(result.url).content
            pil = Image.open(BytesIO(content))
            img_format = pil.format.lower()
            width, height = pil.size
            id = uuid.uuid7()
            filename = f"{id}.{img_format.replace('jpeg', 'jpg')}"
            url = upload_image(filename, content, prefix="creative/qwen", rename=False)
            urls.append(url)
            images.append(
                ImageInfo(
                    url=url,
                    id=str(id),
                    filename=filename,
                    width=width,
                    height=height,
                    mime_type=f"image/{img_format}",  # noqa
                )
            )

    else:
        return ImageToolResponse(
            content=f"同步调用失败, status_code: {resp.status_code}, code: {resp.code}, message: {resp.message}",
            success=False,
        )
    url = urls[0] if len(urls) > 0 else ""
    image_info: ImageInfo | None = images[0] if len(images) > 0 else None

    # image_info = dict(url=url, mime_type=f"image/{img_format}")
    return ImageToolResponse(
        content=json.dumps(dict(url=image_info.url, mime_type=image_info.mime_type), ensure_ascii=False),
        success=True,
        images=[image_info] if image_info else None,
    )


if __name__ == "__main__":
    resp = image_generate_with_qwen(prompt="生成一碗牛肉面")
    print(resp)
    # resp = image_edit_with_qwen(
    #     prompt="将图像改为卡通风格",
    #     image_urls=["https://cdn.fullspeed.cn/seedream/019b0122-9129-7520-b479-93dea16aea0a.jpg"],
    # )
    # print(resp)
    pass
