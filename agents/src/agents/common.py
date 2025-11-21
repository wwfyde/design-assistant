from langchain_google_genai import ChatGoogleGenerativeAI

from lib import settings

openai_model_config = settings.providers.openai


google_model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=0.5,
    timeout=None,
    max_retries=2,
    google_api_key=settings.providers.google.api_key,
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

ai_msg = model_with_search.invoke(messages)
print(ai_msg)
