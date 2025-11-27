from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from lib import settings


async def init_postgres_saver():
    db_uri = f"postgresql://{settings.postgres.username}:{settings.postgres.password.get_secret_value()}@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.database}"
            # db_uri = settings.postgres_dsn

    async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
        await checkpointer.setup()
        print("PostgresSaver initialized successfully.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_postgres_saver())