import logging
from contextlib import asynccontextmanager

from agents.rednote_agent import build_rednote_agent
from api.services.websocket import broadcast_init_done
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

from lib import settings


async def initialize():
    print("Initializing config_service")
    print("Initializing broadcast_init_done")
    await broadcast_init_done()


@asynccontextmanager
async def lifespan(app):
    print("开机")
    logging.info("startup")
    print(f"当前数据仓储类型: {settings.repo_type=}")
    # init broadcast service
    await initialize()

    # 使用app.state 存储全局状态, 而不是使用 global 声明
    if settings.repo_type == "in-memory":
        checkpointer = InMemorySaver()
        app.state.rednote_agent = build_rednote_agent(checkpointer)
    else:
        DB_URI = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"

        with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
            app.state.rednote_agent = build_rednote_agent(checkpointer)

    # 异步任务 适合添加长循环与定时器
    # app.state.listen_task = asyncio.create_task(listen_service())
    # app.state.listen_task.add_done_callback(lambda task : logging.info("listen_service task done"))

    # 全局请求计数
    app.state.request_count = 0

    # 如何访问全局state? api 中通过 request.app.state.xxx 访问

    # 真全局共享状态, 需要依赖redis等外部存储机制

    yield
    # 优雅关闭
    print("关机")
    logging.info("shutdown")
    del app.state.rednote_agent

    # app.state.listen_task.cancel()
    # 关闭全局资源
