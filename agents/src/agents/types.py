from typing import TypeVar

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

Messages = TypeVar(name="Messages", bound=HumanMessage | AIMessage | ToolMessage | SystemMessage)
