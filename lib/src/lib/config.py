import uuid
from pathlib import Path
from typing import Any, Literal, Tuple, Type

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr, computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class MidjourneyConfig(BaseModel):
    user_token: str
    bot_token: str
    guild_id: str
    channel_id: str
    user_agent: str | None = None
    prompt_prefix: str = "<&"
    prompt_suffix: str = ">"
    app_name: str = "midjourney_simple_api"
    rate_limit: int | float = 1 / 4
    interaction_url: str = "https://discord.com/api/v9/interactions"

    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int | None = 0
    password: SecretStr | None = ""


class PostgresConfig(BaseModel):
    host: str
    port: int
    username: str
    password: SecretStr
    database: str
    pool_size: int = 30


class AliyunOssConfig(BaseModel):
    endpoint: str
    access_key_id: str
    access_key_secret: str
    bucket_name: str
    domain: str
    path_prefix: str = "midjourney_simple_api"


class LLMConfig(BaseModel):
    base_url: str
    api_key: str
    model: str | None = None
    models: list[dict] | list[str] = []
    max_tokens: int | None = None
    temperature: float | None = None

    model_config = ConfigDict(
        extra="allow",
    )


class LLMProvider(BaseModel):
    dashscope: LLMConfig | None = None
    ark: LLMConfig | None = None
    openai: LLMConfig | None = None
    gemini: LLMConfig | None = None
    deepseek: LLMConfig | None = None


class JimengConfig(BaseModel):
    base_url: str
    access_key: str
    secret_key: str


class SolutionConfig(BaseModel):
    jimeng: JimengConfig | None = None
    kontext: Any | None = None


class Settings(BaseSettings):
    app_name: str = "ai-tools"
    project_name: str = "AiMark Design Agent"
    repo_type: Literal["in-memory", "postgres", "mongodb", "mysql", "redis"] = (
        "in-memory"
    )
    api_port: int = 8013
    api_key_header: str = "fastapi"
    httpx_timeout: int = 60
    wait_max_seconds: int = 60 * 2
    project_dir: Path = Path(__file__).parent.parent.parent.parent
    base_dir: Path = Path.cwd()
    data_dir: Path = base_dir.joinpath("data")
    temp_dir: Path = base_dir.joinpath("temp")
    static_dir: Path = base_dir.joinpath("web", "dist")
    oss: AliyunOssConfig | None = None
    api_prefix: str | None = ""
    proxy_url: str | None = "http://127.0.0.1:7890"
    redis: RedisConfig | None = None
    redis_expire_time: int = 60 * 60 * 24 * 30
    providers: LLMProvider | None = Field(None, title="LLM提供商配置")
    solutions: SolutionConfig | None = Field(None, title="解决方案配置")
    apps: Any | None = Field(None, title="多应用配置")
    tools: Any | None = Field(None, title="私有化部署工具")
    infras: Any | None = Field(None, title="基础设施配置")

    postgres: PostgresConfig = None

    # ark: ArkConfig = None

    @computed_field
    @property
    def redis_dsn(self) -> str:
        return (
            f"redis://:{self.redis.password.get_secret_value() or ''}@{self.redis.host}:{self.redis.port}/"
            f"{self.redis.db}?health_check_interval=2"
        )

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=[".env"],
        env_file_encoding="utf-8",
        validate_assignment=True,  # 允许赋值时验证
        env_nested_delimiter="__",
        toml_file=[
            "config.toml",
            "config.dev.toml",
            "config.staging.toml",
            "config.prod.toml",
            "config.local.toml",
            "config.dev.local.toml",
            "config.staging.local.toml",
            "config.prod.local.toml",
        ],
        # yaml_file=[
        #     "config.yml",
        #     "config.dev.yml",
        #     "config.staging.yml",
        #     "config.prod.yml",
        #     "config.local.yml",
        #     "config.dev.local.yml",
        #     "config.staging.local.yml",
        #     "config.prod.local.yml",
        # ],
        # yaml_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # The order of the returned callables decides the priority of inputs; first item is the highest priority.
        # 第一个优先级最高
        return (
            env_settings,
            dotenv_settings,
            # YamlConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
        )

    @computed_field
    @property
    def http_client(self) -> httpx.Client:
        return httpx.Client(proxy=self.proxy_url or "http://127.0.0.1:7890")

    @computed_field
    @property
    def http_client_async(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(proxy=self.proxy_url or "http://127.0.0.1:7890")

    @computed_field
    @property
    def postgres_dsn(self) -> str:
        # return f"postgresql+psycopg://{self.postgres.username}:{self.postgres.password.get_secret_value()}@{self.postgres.host}:{self.postgres.port}/{self.postgres.database}"
        return f"postgresql+psycopg://{self.postgres.username}:{self.postgres.password.get_secret_value()}@{self.postgres.host}:{self.postgres.port}/{self.postgres.database}"

    @computed_field
    @property
    def postgres_dsn_sync(self) -> str:
        # return f"postgresql+psycopg://{self.postgres.username}:{self.postgres.password.get_secret_value()}@{self.postgres.host}:{self.postgres.port}/{self.postgres.database}"
        # return f"postgresql+psycopg_async://{self.postgres.username}:{self.postgres.password.get_secret_value()}@{self.postgres.host}:{self.postgres.port}/{self.postgres.database}"
        return f"postgresql+psycopg://{self.postgres.username}:{self.postgres.password.get_secret_value()}@{self.postgres.host}:{self.postgres.port}/{self.postgres.database}"


settings = Settings()

if __name__ == "__main__":
    print(settings.redis_dsn)
    print(settings.providers.ark.image_model)
    print(settings.providers.ark.api_key)
    print(project_dir := settings.project_dir)
    print(settings.proxy_url)
    print(getattr(settings.providers, "ark").base_url)
