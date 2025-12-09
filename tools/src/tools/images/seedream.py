import json
import math
from io import BytesIO

import httpx
import uuid_utils as uuid
from PIL import Image

from lib import settings
from lib.image import upload_image


def image_create_with_seedream(
    *,
    prompt: str,
    image_urls: list[str] | str | None = None,
    aspect_ratio: str | None = None,
) -> str:
    """

    Args:
        image_urls: Search terms to look for
        prompt: Required. The prompt for image generation. If you want to edit an image, please describe what you want to edit in the prompt.
        aspect_ratio:
    """

    # aspect_ratio: str | None = tool_parameters.get("aspect_ratio", None)
    # size: Literal["1K", "2K", "4K"] = tool_parameters.get("size", "2K")
    # seed: int | None = tool_parameters.get("seed", -1)
    # TODO: 考虑使用字符串逗号隔开, 还是list
    if aspect_ratio:
        width, height = [
            int(item) for item in aspect_ratio.replace(":", "×").split("×")
        ]
        size = "2K"
        base = 2
        match size:
            case "1K":
                base = 1
            case "2K":
                base = 2
            case "4K":
                base = 4
            case _:
                base = 2

        if int(width) == 1 and int(height) == 1:
            width, height = 1024 * base, 1024 * base
        elif int(width) == 16 and int(height) == 9:
            width, height = 1280 * base, 720 * base
        elif int(width) == 9 and int(height) == 16:
            width, height = 720 * base, 1280 * base
        elif int(width) == 4 and int(height) == 3:
            width, height = 1125 * base, 864 * base
        elif int(width) == 3 and int(height) == 4:
            width, height = 864 * base, 1125 * base
        elif int(width) == 3 and int(height) == 2:
            width, height = 1248 * base, 832 * base
        elif int(width) == 2 and int(height) == 3:
            width, height = 832 * base, 1248 * base
        elif int(width) == 21 and int(height) == 9:
            width, height = 1512 * base, 648 * base
        elif int(width) > 128 and int(height) > 500:
            width, height = min(int(width), 4096), min(int(height), 4096)
        elif width * height < 921600:
            base = math.ceil(math.sqrt(921600 // (width * height)))
            width, height = int(width) * base, int(height) * base
        else:
            width, height = int(width), int(height)  # 默认值
    else:
        width, height = 864 * 2, 1125 * 2  # 默认值
    # seed = random.randrange(-1, 2**31 -1)
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

    base_url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    api_key = settings.providers.ark.api_key
    use_stream = False
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": "doubao-seedream-4-0-250828",
        "prompt": prompt,
        "image": image_list,
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {"max_images": 5},
        "response_format": "url",
        # "size": "2K",
        "size": f"{width}x{height}",
        "stream": use_stream,
        # 优化prompt
        "optimize_prompt_options": {
            "mode": "standard"
        },  # support standard and fast mode
        # "seed": seed or -1,
        "watermark": False,
    }
    if not image_list:
        data.pop("image")
    if not aspect_ratio:
        data["size"] = "2K"

    try:
        if use_stream:
            with httpx.Client() as client:
                with client.stream(
                    "POST", base_url, json=data, headers=headers, timeout=180
                ) as response:
                    for line in response.iter_lines():
                        if line:
                            # print(line)
                            pass
            return ""
        else:
            response = httpx.post(base_url, headers=headers, json=data, timeout=360)
            if response.status_code == 200:
                result = response.json()
                images: list[dict] = result.get("data", [])

                uploaded_urls = []
                for index, image in enumerate(images):
                    response = httpx.get(image.get("url"), timeout=180)

                    content = response.content
                    pil = Image.open(BytesIO(content))
                    img_format = pil.format.lower().replace("jpeg", "jpg") or "png"
                    filename = f"{str(uuid.uuid7())}.{img_format}"
                    image_url = upload_image(filename, data=content, prefix="seedream")
                    # metadata = {"mime_type": f"image/{img_format}"}

                    uploaded_urls.append(
                        {
                            "index": index + 1,
                            "url": image_url,
                            "size": image.get("size", f"{width}x{height}"),
                            "mine_type": f"image/{img_format}",
                            "content": f"![images][{image_url}]",
                        }
                    )
                # markdown_str = "\n".join(
                #     [f"![images]({image['url']})" for image in uploaded_urls]
                # )
                if len(uploaded_urls) == 1:
                    return json.dumps(uploaded_urls[0], ensure_ascii=False)

                return json.dumps(uploaded_urls, ensure_ascii=False)
                return f"{markdown_str}\n图像生成完成, 共生成{len(uploaded_urls)}张图像, 图像信息:{uploaded_urls}"
            else:
                error = response.json().get("error", {}).get("message", "未知错误")
                return f"图像生成失败, 错误信息: {error}"

    except Exception as exc:
        return f"工具调用失败, 无生成图像, 错误提示: {exc}"


if __name__ == "__main__":
    resp = image_create_with_seedream(prompt="生成一只可爱的猫咪", aspect_ratio="3:4")
    print(resp)
