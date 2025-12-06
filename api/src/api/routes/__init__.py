from fastapi import APIRouter, Depends

from api.deps import verify_header_token

from . import (  # noqa F401
    agent,
    canvas,
    chat,
    config,
    file,
    prompt,
    root,
    tool,
    websocket,
    workspace,
)

router = APIRouter(dependencies=[Depends(verify_header_token)])

router.include_router(canvas.router, prefix="/canvas", tags=["canvas"])
router.include_router(chat.router, tags=["chat"])
router.include_router(workspace.router, tags=["workspace"])
router.include_router(config.router, prefix="/config", tags=["settings"])
router.include_router(root.router, tags=["default"])
router.include_router(tool.router, prefix="/tools", tags=["tool"])
router.include_router(agent.router, prefix="/agents", tags=["agents"])
router.include_router(file.router, prefix="", tags=["file"])
router.include_router(prompt.router, prefix="/prompts", tags=["prompt"])
