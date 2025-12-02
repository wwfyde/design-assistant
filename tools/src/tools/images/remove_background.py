import tempfile
from pathlib import Path

import httpx
import uuid_utils as uuid
from rembg import remove

from lib import upload_image


def rembg_with_url(image_url: str) -> str | None:
    image_content = httpx.get(image_url, timeout=60).content
    suffix = Path(httpx.URL(image_url).path).suffix
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=suffix, delete=False) as tmp:
        tmp.write(image_content)
        tmp.flush()
        image_path = tmp.name

    with open(image_path, "rb") as i:
        input = i.read()
        output = remove(input, force_return_bytes=True)
        filename = str(uuid.uuid7())
        url = upload_image(
            f"{filename}.png", output, prefix="tmp", rename=False, domain=None
        )

        return url


if __name__ == "__main__":
    url = rembg_with_url(
        "https://dms-upload.oss-cn-hangzhou.aliyuncs.com/seedream/b3736283-44b7-414d-acf0-6920a877942d.jpeg"
    )
    print(url)
