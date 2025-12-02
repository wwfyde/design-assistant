import json

import httpx
import uuid_utils as uuid
from api.core.db import SessionLocal
from api.models import Prompt
from sqlalchemy.dialects.postgresql import insert

from lib import settings, upload_image


def load_prompts_from_file() -> list[dict]:
    file = settings.data_dir / "prompts.json"

    if not file.exists():
        print(f"Prompts file {file} does not exist.")
        return []
    file_dict: list[dict] = json.loads(file.read_text(encoding="utf-8"))
    new_dicts = []
    for item in file_dict:
        id = str(uuid.uuid7())
        image: str | None = item.get("images", [])[0] if item.get("images") else None
        uploaded_image = None
        if image:
            filename = id + "." + image.split(".")[-1]
            try:
                with httpx.Client(proxy=settings.proxy_url, timeout=60) as client:
                    image_bytes = client.get(image).content
                    uploaded_image = upload_image(
                        filename,
                        image_bytes,
                        prefix="agent/image_prompt_url",
                        rename=False,
                        domain=None,
                    )
            except:
                print(f"Failed to upload image from URL: {image}")
                uploaded_image = None

        new_dict = {
            "id": id,
            "tags": item.get("tags", []),
            "title": item.get("title", None),
            "image": uploaded_image,
            "source": item.get("source", {}).get("name", None)
            if item.get("source")
            else None,
            "prompt_en": item.get("prompt_en", None),
            "prompt_zh": item.get("prompt_zh", None),
            "source_url": item.get("source", {}).get("url", None)
            if item.get("source")
            else None,
        }
        new_dicts.append(new_dict)
    return new_dicts


def write_to_db(prompts: list[dict]):
    with SessionLocal() as session:
        stmt = insert(Prompt).returning(Prompt)
        result = session.execute(stmt, prompts)
        session.commit()
        items = result.scalars().all()
        print(items)
        return items
        pass


if __name__ == "__main__":
    prompts = load_prompts_from_file()
    print(prompts)
    write_to_db(prompts)
    pass
