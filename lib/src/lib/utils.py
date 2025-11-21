import hashlib
import secrets
import uuid
from datetime import datetime
from typing import Literal


def get_current_date() -> str:
    """
    获取当前时间的 ISO 格式字符串
    """
    return datetime.now().astimezone().isoformat(timespec="seconds")


def generate_file_id(
    method: Literal["uuid", "timestamp", "hash"] = "uuid", prefix: str = "img_"
) -> str:
    """
    生成带有 img_ 前缀的 image file id

    Args:
        method: 生成方法，可选 "uuid", "timestamp", "random", "hash"
        prefix: id前缀

    Returns:
        str: 格式为 img_xxxxx 的唯一ID
    """

    if method == "uuid":
        # 使用 UUID4 生成唯一ID
        unique_id = str(uuid.uuid4()).replace("-", "")
        return f"{prefix}{unique_id}"

    elif method == "timestamp":
        # 使用时间戳 + 随机数
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        random_suffix = secrets.token_hex(4)
        return f"{prefix}{timestamp}_{random_suffix}"

    elif method == "random":
        # 使用安全的随机字符串
        random_id = secrets.token_urlsafe(16)
        return f"{prefix}{random_id}"

    elif method == "hash":
        # 使用时间戳的哈希值
        timestamp = str(datetime.utcnow().timestamp()).encode()
        random_bytes = secrets.token_bytes(8)
        hash_id = hashlib.sha256(timestamp + random_bytes).hexdigest()[:24]
        return f"{prefix}{hash_id}"

    else:
        raise ValueError(f"Unknown method: {method}")


if __name__ == "__main__":
    print(get_current_date())
    print(generate_file_id())
