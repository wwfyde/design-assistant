import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from api.domain.model import ModelInfo
from lib import settings
from lib.config import LLMConfig

openai_model_config = settings.providers.openai


# TODO  需要代理支持
google_model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=0.5,
    timeout=None,
    max_retries=2,
    google_api_key=settings.providers.gemini.api_key,
    # other params...
)


messages = [
    (
        "system",
        "You are a helpful assistant that translates English to Chinese. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
model_with_search = google_model.bind_tools([{"google_search": {}}])

# ai_msg = model_with_search.invoke(messages)
# print(ai_msg)


def get_text_model(model: ModelInfo) -> ChatOpenAI:
    provider: LLMConfig = getattr(settings.providers, model.provider)
    print(f"当前使用的文本模型: {provider.model}")
    return ChatOpenAI(
        model=provider.model,
        openai_api_key=provider.api_key,  # type: ignore
        openai_api_base=provider.base_url,
        max_retries=2,
        temperature=provider.temperature or 0,
        # max_tokens=max_tokens, # TODO: 暂时注释掉有问题的参数
        http_client=httpx.Client(proxy=settings.proxy_url or "http://127.0.0.1:7890"),
        http_async_client=httpx.AsyncClient(proxy=settings.proxy_url or "http://127.0.0.1:7890"),
    )


if __name__ == "__main__":
    model_info = ModelInfo(provider="ark", model="gpt-4", url="1", type="text")
    text_model_instance = get_text_model(model_info)
    response = text_model_instance.invoke(
        [
            {
                "role": "user",
                "content": "1+1=?",
            }
        ]
    )
    print(response)
