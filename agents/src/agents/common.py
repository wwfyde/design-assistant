import httpx
from pydantic import SecretStr
from google.genai import types
from langgraph_tools import image_create_with_gemini
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI

from lib import settings
from lib.config import LLMConfig
from api.domain.model import ModelInfo

openai_model_config = settings.providers.openai
http_options = types.HttpOptions(
    client_args={"proxy": settings.proxy_url},
    async_client_args={"proxy": settings.proxy_url},
)

# TODO  需要代理支持
google_model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=1,
    timeout=None,
    max_retries=2,
    google_api_key=settings.providers.gemini.api_key,
    # http_options=http_options,
    client_args={"proxy": settings.proxy_url},
    # other params...
)


def get_text_model(model: ModelInfo) -> ChatOpenAI | ChatGoogleGenerativeAI | ChatDeepSeek:
    provider: LLMConfig = getattr(settings.providers, model.provider)
    print(f"当前使用的文本模型: {provider.model}")
    if model.provider == "gemini":
        return google_model
    if model.provider == "deepseek":
        return ChatDeepSeek(
            model=provider.model,
            api_key=SecretStr(provider.api_key),
            api_base=provider.base_url,
            extra_body={"reasoning": {"enabled": True}} if provider.model == "deepseek-reasoner" else None,
        )
    return ChatOpenAI(
        model=provider.model,
        # openai_api_key=provider.api_key,  # type: ignore
        # openai_api_base=provider.base_url,
        api_key=SecretStr(provider.api_key),
        base_url=provider.base_url,
        max_retries=2,
        temperature=provider.temperature or 0,
        # max_tokens=max_tokens, # TODO: 暂时注释掉有问题的参数
        http_client=httpx.Client(proxy=settings.proxy_url or "http://127.0.0.1:7890"),
        http_async_client=httpx.AsyncClient(proxy=settings.proxy_url or "http://127.0.0.1:7890"),
    )


if __name__ == "__main__":
    # provider = settings.providers.ark
    model_info = ModelInfo(provider="gemini", model="11", url="1", type="text", display_name="火山引擎")
    text_model_instance = get_text_model(model_info)
    response = text_model_instance.invoke([
        {
            "role": "user",
            "content": "1+1=?",
        }
    ])
    print(response)

    # messages = [
    #     (
    #         "system",
    #         "You are a helpful assistant that translates English to Chinese. Translate the user sentence.",
    #     ),
    #     ("human", "I love programming."),
    # ]
    # model_with_search = google_model.bind_tools([{"google_search": {}}])
    #
    # ai_msg = model_with_search.invoke(messages)
    # print(ai_msg)

    pass
