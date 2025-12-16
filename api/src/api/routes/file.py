import os
from io import BytesIO
from mimetypes import guess_type

from fastapi import APIRouter, File, HTTPException, UploadFile, Body
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from lib.utils import generate_file_id
import base64
import re
from PIL import Image
import httpx

from lib import settings

router = APIRouter()
files_dir = settings.data_dir / "files"
FILES_DIR = str(files_dir)
os.makedirs(FILES_DIR, exist_ok=True)


# 上传图片接口，支持表单提交
@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...), max_size_mb: float = 3.0):
    print("🦄upload_image file", file.filename)
    # 生成文件 ID 和文件名
    file_id = generate_file_id()
    filename = file.filename or ""

    # Read the file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")
    original_size_mb = len(content) / (1024 * 1024)  # Convert to MB

    # Open the image from bytes to get its dimensions
    with Image.open(BytesIO(content)) as img:
        width, height = img.size

        # Check if compression is needed
        if original_size_mb > max_size_mb:
            print(f"🦄 Image size ({original_size_mb:.2f}MB) exceeds limit ({max_size_mb}MB), compressing...")

            # Convert to RGB if necessary (for JPEG compression)
            if img.mode in ("RGBA", "LA", "P"):
                # Create a white background for transparent images
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Compress the image
            compressed_content = compress_image(img, max_size_mb)

            # Save compressed image using Image.save
            extension = "jpg"  # Force JPEG for compressed images
            file_path = os.path.join(FILES_DIR, f"{file_id}.{extension}")

            # Create new image from compressed content and save
            with Image.open(BytesIO(compressed_content)) as compressed_img:
                width, height = compressed_img.size
                await run_in_threadpool(
                    compressed_img.save,
                    file_path,
                    format="JPEG",
                    quality=95,
                    optimize=True,
                )
                # compressed_img.save(file_path, format='JPEG', quality=95, optimize=True)

            final_size_mb = len(compressed_content) / (1024 * 1024)
            print(f"🦄 Compressed from {original_size_mb:.2f}MB to {final_size_mb:.2f}MB")
        else:
            # Determine the file extension from original file
            mime_type, _ = guess_type(filename)
            if mime_type and mime_type.startswith("image/"):
                extension = mime_type.split("/")[-1]
                # Handle common image format mappings
                if extension == "jpeg":
                    extension = "jpg"
            else:
                extension = "jpg"  # Default to jpg for unknown types

            # Save original image using Image.save
            file_path = os.path.join(FILES_DIR, f"{file_id}.{extension}")

            # Determine save format based on extension
            save_format = "JPEG" if extension.lower() in ["jpg", "jpeg"] else extension.upper()
            if save_format == "JPEG":
                img = img.convert("RGB")

            # img.save(file_path, format=save_format)
            await run_in_threadpool(img.save, file_path, format=save_format)

    # 返回文件信息
    print("🦄upload_image file_path", file_path)
    return {
        "file_id": f"{file_id}.{extension}",
        "url": f"http://localhost:{settings.api_port}/api/file/{file_id}.{extension}",
        "width": width,
        "height": height,
    }


@router.post("/upload_image_from_url")
async def upload_image_from_url(base64_image: str = Body(..., embed=True)):
    print("🦄upload_image_from_url (base64) length:", len(base64_image))

    try:
        # 1. Handle Data URL prefix (e.g., "data:image/png;base64,...")
        if "," in base64_image:
            header, base64_data = base64_image.split(",", 1)
        else:
            base64_data = base64_image

        # 2. Decode Base64 string
        try:
            image_data = base64.b64decode(base64_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 string: {e}")

        file_id = generate_file_id()

        # 3. Open image to get dimensions and validate
        with Image.open(BytesIO(image_data)) as img:
            width, height = img.size

            # Determine extension from format or default to jpg
            # If we had the header, we could guess from mime type, but PIL knows the format too.
            original_format = img.format  # e.g., 'PNG', 'JPEG'
            if original_format:
                extension = original_format.lower()
                if extension == "jpeg":
                    extension = "jpg"
            else:
                extension = "jpg"

            # Save image
            file_path = os.path.join(FILES_DIR, f"{file_id}.{extension}")
            save_format = "JPEG" if extension.lower() in ["jpg", "jpeg"] else extension.upper()

            if save_format == "JPEG" and img.mode != "RGB":
                img = img.convert("RGB")

            await run_in_threadpool(img.save, file_path, format=save_format)

            return {
                "file_id": f"{file_id}.{extension}",
                "url": f"http://localhost:{settings.api_port}/api/file/{file_id}.{extension}",
                "width": width,
                "height": height,
            }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing base64 image: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")


def compress_image(img: Image.Image, max_size_mb: float) -> bytes:
    """
    Compress an image to be under the specified size limit.
    """
    # Start with high quality
    quality = 95

    while quality > 10:
        # Save to bytes buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)

        # Check size
        size_mb = len(buffer.getvalue()) / (1024 * 1024)

        if size_mb <= max_size_mb:
            return buffer.getvalue()

        # Reduce quality for next iteration
        quality -= 10

    # If still too large, try reducing dimensions
    original_width, original_height = img.size
    scale_factor = 0.8

    while scale_factor > 0.3:
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Try with moderate quality
        buffer = BytesIO()
        resized_img.save(buffer, format="JPEG", quality=70, optimize=True)

        size_mb = len(buffer.getvalue()) / (1024 * 1024)

        if size_mb <= max_size_mb:
            return buffer.getvalue()

        scale_factor -= 0.1

    # Last resort: very low quality
    buffer = BytesIO()
    resized_img.save(buffer, format="JPEG", quality=30, optimize=True)
    return buffer.getvalue()


# 文件下载接口
@router.get("/file/{file_id}")
async def get_file(file_id: str):
    file_path = os.path.join(FILES_DIR, f"{file_id}")
    print("🦄get_file file_path", file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
