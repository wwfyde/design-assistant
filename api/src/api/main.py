import logging
import os
from contextlib import asynccontextmanager
from time import sleep
from typing import Callable

import socketio
from api.routes import router
from api.services.websocket import broadcast_init_done
from api.states import sio
from fastapi import FastAPI, Header, Request
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from uvicorn import run

from lib import settings

root_path = os.getenv("ROOT_PATH", "") or settings.api_prefix



async def initialize():
    print("Initializing config_service")
    print("Initializing broadcast_init_done")
    await broadcast_init_done()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("开机")
    logging.info("startup")
    print(f"当前数据仓储类型: {settings.repo_type=}")
    # init broadcast service
    await initialize()
    yield


async def verify_custom_token(token: str = Header(None)):
    if not token or token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return token


async def log_requests():
    logging.info("Request received")
    return "logged"


def create_app(lifespan: Callable = lifespan):
    """
    通过工厂函数创建app
    :return:
    """

    app = FastAPI(
        title=settings.project_name,
        # root_path=root_path,  # 这种写法不对
        # openapi_url="/openapi.json",
        lifespan=lifespan,
        openapi_tags=[],
        openapi_prefix="",
        # dependencies=[Depends(log_requests)],  # Depends(verify_custom_token),
    )

    # @app.middleware("http")
    # async def add_process_time_header(request: Request, call_next):
    #     start_time = time.perf_counter()
    #     response = await call_next(request)
    #     process_time = time.perf_counter() - start_time
    #     response.headers["X-Process-Time"] = str(process_time)
    #     log.debug(f"Process time: {process_time * 1000}ms")
    #     return response

    app.add_middleware(
        CORSMiddleware,
        # allow_origins=settings.CORS_ORIGINS,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_middleware(HeaderMiddleware)

    # register exception_handler
    # @app.exception_handler(RequestValidationError)
    # async def validation_exception_handler(_, exc: RequestValidationError):
    #     return JSONResponse(
    #         status_code=400,
    #         content={"code": 400, "message": f"request params error: {exc.body}"},
    #     )

    # 解决未开启魔法时无法访问问题
    @app.get("/docs2")
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title="API Docs",
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    # @app.get("/")
    # async def root():
    #     return RedirectResponse("/docs")

    @app.get("/hello")
    @app.get("/demo")
    async def hello(request: Request):
        s: str = "世界"

        print(request.app.state.demo)

        return {"message": f"Hello, {s}!", "data": f"hello, {s}!"}

    app.include_router(router, prefix="/api")

    # registering logfire
    # import logfire
    #
    # logfire.configure()
    # logfire.instrument_fastapi(app)
    # logfire.info(f"{app.__doc__}")

    # 绑定静态文件
    static_dir = settings.static_dir

    @app.get("/")
    async def serve_react_app():
        response = FileResponse(settings.static_dir / "index.html")
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app


app = create_app()
sleep(2)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/socket.io")


# app.mount('/outer', api2.app)


def main():
    print("api imported!")
    _bypass = {"127.0.0.1", "localhost", "::1"}
    current = set(os.environ.get("no_proxy", "").split(",")) | set(
        os.environ.get("NO_PROXY", "").split(",")
    )
    os.environ["no_proxy"] = os.environ["NO_PROXY"] = ",".join(
        sorted(_bypass | current - {""})
    )
    run(app="main:socket_app", reload=True, port=8013, loop='asyncio')
    # run(socket_app, host="127.0.0.1", port=8013)


if __name__ == "__main__":
    main()
