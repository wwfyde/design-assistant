import base64

import oss2
import uuid_utils as uuid

from lib import settings


def upload_image(
    filename: str,
    data: str | bytes,
    prefix: str = "tmp",
    rename: bool = False,
    domain: str = None,
) -> str | None:
    """
    上传图片到OSS
    :param filename: 文件名
    :param data: 文件内容, 二进制数据或字符串
    :param prefix: OSS路径前缀 上传到OSS的路径
    :param rename: 是否重命名, 默认为True
    :param domain: OSS域名, 默认为None时使用bucket_name+endpoint
    """
    oss = settings.oss
    endpoint = oss.endpoint

    auth = oss2.Auth(oss.access_key_id, oss.access_key_secret)
    bucket_name = oss.bucket_name
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    if rename:
        uid = uuid.uuid7()
        upload_file_name = f"{prefix}/{uid}.{filename.split('.')[-1]}"
    else:
        upload_file_name = f"{prefix}/{filename}"
    if prefix is None:
        # 临时文件, 使用OSS生命周期自动删除
        upload_file_name = f"tmp/{upload_file_name}"

    result = bucket.put_object(upload_file_name, data)
    domain = domain or oss.domain
    if domain:
        image_link = f"https://{domain}/{upload_file_name}"
    else:
        image_link = f"https://{bucket_name}.{endpoint}/{upload_file_name}"
    if result.status == 200:
        return image_link
    else:
        return None


def parse_data_url_to_bytes(data_url: str) -> bytes:
    # pattern = r"^data:(.*?);(base64),(.*)$"
    # match = re.match(pattern, data_url, re.DOTALL)
    if not data_url.startswith("data:"):
        raise ValueError("Invalid Data URL: must start with 'data:'")

    header, data = data_url[5:].split(",")

    mime_type, charset = header.split(";") if ";" in header else [header, ""]
    mime_type = "text/plain" if mime_type == "" else mime_type

    is_base64 = True if charset.lower() == "base64" else False

    data_bytes = base64.b64decode(data) if is_base64 else data

    return data_bytes


def parse_data_url(data_url: str) -> str:
    # pattern = r"^data:(.*?);(base64),(.*)$"
    # match = re.match(pattern, data_url, re.DOTALL)
    if not data_url.startswith("data:"):
        raise ValueError("Invalid Data URL: must start with 'data:'")

    header, data = data_url[5:].split(",")

    mime_type, charset = header.split(";") if ";" in header else [header, ""]
    mime_type = "text/plain" if mime_type == "" else mime_type

    is_base64 = True if charset.lower() == "base64" else False

    data_bytes = base64.b64decode(data) if is_base64 else data

    filename = str(uuid.uuid4()) + "." + mime_type.split("/")[-1]

    url = upload_image(filename, data_bytes, prefix="design", rename=False)

    return url


def calculate_image_width(original_width, original_height, max_width: int = 350) -> tuple[int, int]:
    """
    最大宽度, 一般设计为 350 , 240-320 400 等典型值

    """
    scale = min(max_width / original_width, max_width / original_height, 1.0)

    return round(original_width * scale), round(original_height * scale)


if __name__ == "__main__":
    # file = Path(__file__).parent.parent.joinpath("img.png")
    #
    # id = f"{str(uuid.uuid4())}{file.suffix}"
    # image_bytes = file.read_bytes()
    # url = upload_image(id, image_bytes, prefix="test", rename=False, domain=None)
    # print(url)

    # url = parse_data_url(
    #     "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAsQAAAFgCAYAAAC8MG/mAAAQAElEQVR4AeydgbncKLZu67uJOI3pSDoNTyQzaXQknjQcyXtetnc3RwckpEISoHW/2S0ECDYLwf4L16n7f//P/5OABCQgAQlIQAISkMCDCfzfy/+TgAQk8AgCDlICEpCABCSQJ6AgznMxVwISkIAEJCABCYxJQK93E1AQ70bmAxKQgAQkIAEJSEACMxFQEM80m47lSQQcqwQkIAEJSEACjQgoiBuBtBkJSEACEpCABM4gYJsSOJ+Agvh8xvYgA"
    # )
    # print(url)
    print(calculate_image_width(1500, 2300))
    print(calculate_image_width(1500, 1500))
    print(calculate_image_width(4000, 1500))
    pass
