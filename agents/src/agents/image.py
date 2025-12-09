from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from tools.images import image_create_with_seedream

from lib import get_current_date

supervisor_prompt = f"""
你是一名图像设计agent. 支持调用seedream工具, 创建或编辑图像

当前时间:{get_current_date()}

"""
model = init_chat_model("gpt-4.1-mini")
supervisor_agent = create_agent(
    model,
    tools=[image_create_with_seedream],
    system_prompt=supervisor_prompt,
    # checkpointer=InMemorySaver(),
)
messages = [HumanMessage(content="帮我创建一张日出风景图, 宽高比3:4")]


resp = supervisor_agent.invoke(HumanMessage(content="帮我创建一张日出风景图, 宽高比3:4"))
print(resp)
