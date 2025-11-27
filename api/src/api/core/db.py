import asyncio
import json
from typing import Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from lib import settings

# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.ext.asyncio import create_async_engine

# from app.core.config import settings


def dumps(obj: Mapping) -> str:
    # return orjson.dumps(obj, option=orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS).decode('utf-8')
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


# asyncio_engine = create_async_engine(
#     "postgresql+psycopg_async://<user>:<pass>@localhost/<db>", connect_args={}, echo=True)
engine = create_engine(
    settings.postgres_dsn,
    connect_args={},
    # echo=True,
    json_serializer=dumps,
    pool_size=settings.postgres.pool_size,  # 连接池的大小
    max_overflow=60,  # 连接池中允许的最大溢出连接数量
    pool_recycle=3600,  # 在指定秒数后回收连接
    pool_pre_ping=True,  # 启用 pre_ping 参数
)
# engine = create_engine(str(settings.MYSQL_DSN), connect_args={}, echo=True)

# asyncio_engine = create_async_engine(settings.postgres_dsn)
async_engine = create_async_engine(
    settings.postgres_dsn,
    connect_args={},
    pool_size=settings.postgres.pool_size,  # 连接池的大小
    max_overflow=60,  # 连接池中允许的最大溢出连接数量
    pool_recycle=3600,  # 在指定秒数后回收连接
    pool_pre_ping=True,  # 启用 pre_ping 参数
    # echo=True,
    # json_serializer=dumps,
)


#  ⚠️Important 需要考虑避免线程安全问题, 不要随意传递会话到另一个线程或协程中
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

if __name__ == "__main__":

    async def main():
        async_session = async_sessionmaker(async_engine, expire_on_commit=False)
        async with async_session() as asession:
            with Session(engine) as session:
                async with asession.begin():
                    result = await asession.execute(text("select version()"))
                    version = result.scalar_one_or_none()
                    print(version)
                    pass
                result = session.execute(text("select version()"))
                print(result.scalar_one_or_none())
        await async_engine.dispose()

    asyncio.run(main())

    # async with AsyncSession(asyncio_engine) as session:
    #     async with session.begin():
    #         pass
