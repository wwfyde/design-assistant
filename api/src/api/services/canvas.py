import json
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from lib import get_current_date
from api.models import ChatSession as ChatSessionModel
from api.core.memory import AppStore
from api.domain.chat import ChatSession
from api.domain.canvas import Canvas
from api.models.canvas import Canvas as CanvasModel
from api.schemas.canvas import CanvasCreate


class CanvasRepo(ABC):
    @abstractmethod
    async def create_canvas(self, canvas: CanvasCreate) -> Canvas:
        pass

    @abstractmethod
    async def get_canvas_by_id(self, id: str | UUID) -> Canvas | None:
        pass

    @abstractmethod
    async def get_canvas_data(self, id: str | UUID) -> dict | None:
        pass

    @abstractmethod
    async def get_canvases(self):
        pass

    async def save_canvas_data(self, id: str | UUID, data: str, thumbnail: str):
        pass

    @abstractmethod
    async def delete_canvas(self, id: str | UUID) -> bool:
        pass


class InMemoryCanvasRepo(CanvasRepo):
    def __init__(self, store: AppStore):
        self.store = store

        self.next_id = 1

    async def create_canvas(self, canvas: CanvasCreate) -> Canvas:
        async with self.store.lock:
            self.store.canvas[canvas.canvas_id] = Canvas(
                id=canvas.canvas_id,
                name=canvas.name,
                canvas_id=canvas.canvas_id,
                session_id=canvas.session_id,
                messages=canvas.messages,
            )
            return self.store.canvas[canvas.canvas_id]

    async def get_canvas_by_id(self, id: str | UUID) -> Canvas | None:
        canvas = self.store.canvas.get(id, None)
        return canvas

    async def get_canvas_data(self, id: str | UUID) -> dict | None:
        canvas = self.store.canvas.get(id, None)
        print(canvas)
        print(self.store.canvas)
        if canvas:
            sessions = [item for item in self.store.chat_session.values() if item.canvas_id == id]

            data = {
                "data": canvas.data,
                "name": canvas.name,
                "sessions": sessions,
            }
            return data
        return None

    async def get_canvases(self) -> list[Canvas] | None:
        if len(self.store.canvas.items()) == 0:
            return None
        canvases = sorted(
            [canvas for canvas in self.store.canvas.values() if canvas],
            key=lambda m: m.id,
        )
        return canvases

    async def delete_canvas(self, id: str | UUID) -> bool:
        async with self.store.lock:
            self.store.canvas.pop(id)
        return True

    async def save_canvas_data(self, id: str | UUID, data: str, thumbnail: str) -> Canvas | None:
        async with self.store.lock:
            raw = await self.get_canvas_by_id(id)
            if raw:
                raw.data = data
                raw.thumbnail = thumbnail
                raw.updated_at = get_current_date()

            print(raw)

            # 显式修改 数据
            self.store.canvas[id] = raw
        pass

    async def rename_canvas(self, id: str | UUID, name: str) -> Canvas:
        canvas = self.store.canvas.get(id)
        if canvas:
            canvas.name = name
        return canvas


class PostgresCanvasRepo(CanvasRepo):
    def __init__(self, session: Session):
        self.session = session

    async def create_canvas(self, canvas: CanvasCreate) -> Canvas:
        messages = json.dumps(canvas.messages, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        canvas_db = CanvasModel(
            id=canvas.canvas_id,
            name=canvas.name,
            canvas_id=canvas.canvas_id,
            session_id=canvas.session_id,
            messages=messages,
        )
        self.session.add(canvas_db)
        self.session.commit()
        self.session.refresh(canvas_db)

        return Canvas.model_validate(canvas_db)

    async def get_canvas_by_id(self, id: str | UUID) -> Canvas | None:
        stmt = select(CanvasModel).where(CanvasModel.id == str(id))
        result = self.session.execute(stmt)
        canvas = result.scalar_one_or_none()
        if canvas:
            return Canvas.model_validate(canvas)
        return None

    async def get_canvas_data(self, id: str | UUID) -> dict | None:
        canvas = await self.get_canvas_by_id(id)

        if canvas:
            stmt = select(ChatSessionModel).where(ChatSessionModel.canvas_id == str(id))
            result = self.session.execute(stmt)
            chat_sessions = result.scalars().all()
            sessions = [ChatSession.model_validate(session) for session in chat_sessions]

            data = {
                "data": canvas.data,
                "name": canvas.name,
                "sessions": sessions,
            }
            return data
        return None

    async def get_canvases(self) -> list[Canvas] | None:
        stmt = select(CanvasModel).order_by(CanvasModel.created_at.desc()).limit(20)
        result = self.session.execute(stmt)
        canvas_models = result.scalars().all()
        if not canvas_models:
            return None
        canvases = [Canvas.model_validate(canvas) for canvas in canvas_models]
        return canvases[:10]

    async def delete_canvas(self, id: str | UUID) -> bool:
        stmt = delete(CanvasModel).where(CanvasModel.id == str(id))
        result = self.session.execute(stmt)
        self.session.commit()
        return True

    async def save_canvas_data(self, id: str | UUID, data: str, thumbnail: str) -> Canvas | None:
        stmt = select(CanvasModel).where(CanvasModel.id == str(id))
        result = self.session.execute(stmt)
        canvas_db = result.scalar_one_or_none()
        if canvas_db:
            stmt = (
                update(CanvasModel)
                .where(CanvasModel.id == str(id))
                .values(data=data, thumbnail=thumbnail, updated_at=get_current_date())
            )
            self.session.execute(stmt)
            self.session.commit()
            self.session.refresh(canvas_db)
            return Canvas.model_validate(canvas_db)
        return None

        pass

    async def rename_canvas(self, id: str | UUID, name: str) -> Canvas:
        stmt = select(CanvasModel).where(CanvasModel.id == str(id))
        result = self.session.execute(stmt)
        canvas_db = result.scalar_one_or_none()
        if canvas_db:
            stmt = update(CanvasModel).where(CanvasModel.id == str(id)).values(name=name, updated_at=get_current_date())
            self.session.execute(stmt)
            self.session.commit()
            self.session.refresh(canvas_db)
            return Canvas.model_validate(canvas_db)
        return None

        pass


class CanvasService:
    def __init__(self, repo: CanvasRepo):
        self.repo = repo
        # elif settings.repo_type in ("in-memory", "in_memory"):
        #     self.repo = InMemoryCanvasRepo(store)
        # else:
        #     self.repo = InMemoryCanvasRepo(store)

    async def create_canvas(self, canvas: CanvasCreate):
        return await self.repo.create_canvas(canvas)

    async def get_canvases(self):
        return await self.repo.get_canvases()

    async def get_canvas_by_id(self, id: str | UUID) -> Canvas | None:
        return await self.repo.get_canvas_by_id(id)

    async def get_canvas_data(self, id: str | UUID) -> Canvas | None:
        return await self.repo.get_canvas_data(id)

    async def save_canvas(self, id: str | UUID, data: str, thumbnail: str):
        canvas = await self.repo.get_canvas_by_id(id)
        if canvas:
            canvas.data = data
            canvas.thumbnail = thumbnail
            return await self.repo.save_canvas(canvas)
        return None

    async def save_canvas_data(self, id: str | UUID, data: str, thumbnail: str):
        return await self.repo.save_canvas_data(id, data, thumbnail)

    async def delete_canvas(self, id: str | UUID) -> bool:
        return await self.repo.delete_canvas(id)

    async def rename_canvas(self, id: str | UUID, name: str) -> Canvas | None:
        return await self.repo.rename_canvas(id, name)


# active_canvas_locks = set()
#
#
# @contextmanager
# def canvas_lock(canvas_id: str):
#     acquired = False
#     with threading.Lock():
#         if id not in active_canvas_locks:
#             active_canvas_locks.add(canvas_id)
#             acquired = True
#     try:
#         if acquired:
#             yield
#         else:
#             raise Exception("Canvas is already locked")
#     finally:
#         if acquired:
#             with threading.Lock():
#                 active_canvas_locks.remove(canvas_id)


async def find_next_best_element_position(canvas_data, max_num_per_row=4, spacing=20):
    """
    Calculates the next best position for a new element on the canvas.
    This final version uses a robust row detection algorithm to handle complex layouts.
    """
    elements = canvas_data.get("elements", [])

    media_elements = [
        e for e in elements if e.get("type") in ["image", "embeddable", "video"] and not e.get("isDeleted")
    ]

    if not media_elements:
        return 0, 0

    # Sort elements by their top-left corner
    media_elements.sort(key=lambda e: (e.get("y", 0), e.get("x", 0)))

    # Group elements into rows based on vertical overlap
    rows = []
    for element in media_elements:
        y, height = element.get("y", 0), element.get("height", 0)
        placed = False
        for row in rows:
            # Check if the element vertically overlaps with any element in the row
            if any(max(y, r.get("y", 0)) < min(y + height, r.get("y", 0) + r.get("height", 0)) for r in row):
                row.append(element)
                placed = True
                break
        if not placed:
            rows.append([element])

    # Sort rows by their average y-coordinate
    rows.sort(key=lambda row: sum(e.get("y", 0) for e in row) / len(row))

    if not rows:
        return 0, 0

    last_row = rows[-1]
    last_row.sort(key=lambda e: e.get("x", 0))

    if len(last_row) < max_num_per_row:
        # Add to the last row
        rightmost_element = last_row[-1]
        new_x = rightmost_element.get("x", 0) + rightmost_element.get("width", 0) + spacing
        # Align with the top of the last row for consistency
        new_y = min(e.get("y", 0) for e in last_row)
    else:
        # Start a new row
        new_x = 0
        # Position below the entire last row
        bottom_of_last_row = max(e.get("y", 0) + e.get("height", 0) for e in last_row)
        new_y = bottom_of_last_row + spacing

    return new_x, new_y
