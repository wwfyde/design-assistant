from api.deps import get_db_async
from api.models.prompt import Prompt as PromptModel
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("")
async def get_prompts(offset: int = 1, limit: int = 10, asession: AsyncSession = Depends(get_db_async)):
    stmt = select(PromptModel).offset(offset).limit(limit).order_by(PromptModel.id)

    result = await asession.execute(stmt)
    prompts = result.scalars().all()

    return prompts
