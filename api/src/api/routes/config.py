from fastapi import APIRouter, Request

from lib import settings

# from services.config_service import config_service

# from tools.video_models_dynamic import register_video_models  # Disabled video models
# from services.tool_service import tool_service

router = APIRouter()


@router.get("/exists")
async def config_exists():
    return {"exists": True}


@router.get("")
async def get_config():
    return settings.model_dump(
        exclude={"secret_key", "providers", "oss", "midjourney"},
        exclude_computed_fields=True,
    )


@router.post("")
async def update_config(request: Request):
    data = await request.json()
    # res = await config_service.update_config(data)
    # TODO:  热加载settings

    # 每次更新配置后，重新初始化工具
    # await tool_service.initialize()
    return data
