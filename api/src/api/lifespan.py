import logging
from contextlib import asynccontextmanager

from v2.nacos import NacosNamingService, ClientConfigBuilder, RegisterInstanceParam, DeregisterInstanceParam
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

from lib import settings
from agents.rednote_agent import build_rednote_agent
from api.services.websocket import broadcast_init_done


async def initialize():
    print("Initializing config_service")
    print("Initializing broadcast_init_done")
    await broadcast_init_done()


async def create_nacos_client():
    nacos_config = (
        ClientConfigBuilder()
        .username(settings.nacos.username)
        .password(settings.nacos.password)
        .server_address(settings.nacos.server_address)
        .namespace_id(settings.nacos.namespace_id)
        .build()
    )

    nacos_client = await NacosNamingService.create_naming_service(nacos_config)

    return nacos_client


@asynccontextmanager
async def lifespan(app):
    print("开机")
    logging.info("startup")
    print(f"当前数据仓储类型: {settings.repo_type=}")
    # init broadcast service
    await initialize()

    # 异步任务 适合添加长循环与定时器
    # app.state.listen_task = asyncio.create_task(listen_service())
    # app.state.listen_task.add_done_callback(lambda task : logging.info("listen_service task done"))

    # 如何访问全局state? api 中通过 request.app.state.xxx 访问

    # 真全局共享状态, 需要依赖redis等外部存储机制
    nacos_client = await create_nacos_client()
    print("开始注册服务到nacos")
    success = await nacos_client.register_instance(
        request=RegisterInstanceParam(
            service_name=settings.nacos.service_name,
            ip=settings.nacos.ip,
            port=settings.nacos.port,
            metadata={"env": "prod"},
        )
    )
    print(success)

    yield
    # 优雅关闭
    print("关机")
    logging.info("shutdown")

    # 注销nacos
    await nacos_client.deregister_instance(
        DeregisterInstanceParam(
            service_name=settings.nacos.service_name,
            group_name=settings.nacos.group_name,
            ip=settings.nacos.ip,
            port=settings.nacos.port,
        )
    )

    # app.state.listen_task.cancel()
    # 关闭全局资源
