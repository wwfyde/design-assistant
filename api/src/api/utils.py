import json
import time
from typing import Any, Dict, cast

from api.services.websocket import broadcast_session_update
from lib.utils import generate_file_id


async def save_image_to_canvas(
    session_id: str,
    canvas_id: str,
    filename: str,
    mime_type: str,
    width: int,
    height: int,
) -> str:
    """Save image to canvas with proper locking and positioning"""
    # Use lock to ensure atomicity of the save process
    async with canvas_lock_manager.lock_canvas(canvas_id):
        # Fetch canvas data once inside the lock
        canvas: Optional[Dict[str, Any]] = await db_service.get_canvas_data(canvas_id)
        if canvas is None:
            canvas = {"data": {}}
        canvas_data: Dict[str, Any] = canvas.get("data", {})

        # Ensure 'elements' and 'files' keys exist
        if "elements" not in canvas_data:
            canvas_data["elements"] = []
        if "files" not in canvas_data:
            canvas_data["files"] = {}

        file_id = generate_file_id()
        url = f"/api/file/{filename}"

        file_data: Dict[str, Any] = {
            "mimeType": mime_type,
            "id": file_id,
            "dataURL": url,
            "created": int(time.time() * 1000),
        }

        new_image_element: Dict[str, Any] = await generate_new_image_element(
            canvas_id,
            file_id,
            {
                "width": width,
                "height": height,
            },
            canvas_data,
        )

        # Update the canvas data with the new element and file info
        elements_list = cast(List[Dict[str, Any]], canvas_data["elements"])
        elements_list.append(new_image_element)
        canvas_data["files"][file_id] = file_data

        image_url = f"/api/file/{filename}"

        # Save the updated canvas data back to the database
        await db_service.save_canvas_data(canvas_id, json.dumps(canvas_data))

        # Broadcast image generation message to frontend
        await broadcast_session_update(
            session_id,
            canvas_id,
            {
                "type": "image_generated",
                "element": new_image_element,
                "file": file_data,
                "image_url": image_url,
            },
        )

        return image_url
