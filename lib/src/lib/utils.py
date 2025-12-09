import hashlib
import secrets
from datetime import datetime, timezone
from typing import Literal

import uuid_utils as uuid


def get_current_date(
    *,
    utc: bool = False,
    timespec: Literal["seconds", "milliseconds"] = "milliseconds",
) -> str:
    """
    获取当前时间的 ISO 格式字符串
    """
    dt = datetime.now(timezone.utc) if utc else datetime.now().astimezone()
    iso_str = dt.isoformat(timespec=timespec).replace("+00:00", "Z")
    return iso_str
    if utc:
        return datetime.now().astimezone(tz=timezone.utc).isoformat(timespec=timespec).replace("+00:00", "Z")
    return datetime.now().astimezone().isoformat(timespec=timespec).replace("+00:00", "Z")


def generate_file_id(mode: Literal["uuid", "timestamp", "hash", "urlsafe"] = "uuid", prefix: str = "img_") -> str:
    """
    生成带有 img_ 前缀的 image file id

    Args:
        mode: 生成方法，可选 "uuid", "timestamp", "random", "hash"
        prefix: id前缀

    Returns:
        str: 格式为 img_xxxxx 的唯一ID
    """

    if mode == "uuid":
        # 使用 UUID4 生成唯一ID
        unique_id = str(uuid.uuid7()).replace("-", "")
        return f"{prefix}{unique_id}"

    elif mode == "timestamp":
        # 使用时间戳 + 随机数
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        random_suffix = secrets.token_hex(4)
        return f"{prefix}{timestamp}_{random_suffix}"

    elif mode == "random":
        # 使用安全的随机字符串
        random_id = secrets.token_urlsafe(16)
        return f"{prefix}{random_id}"

    elif mode == "hash":
        # 使用时间戳的哈希值
        timestamp = str(datetime.utcnow().timestamp()).encode()
        random_bytes = secrets.token_bytes(8)
        hash_id = hashlib.sha256(timestamp + random_bytes).hexdigest()[:24]
        return f"{prefix}{hash_id}"

    else:
        raise ValueError(f"Unknown method: {mode}")


if __name__ == "__main__":
    print(get_current_date(utc=True))
    print(get_current_date(utc=False))
    print(get_current_date(utc=False, timespec="seconds"))
    print(generate_file_id())
