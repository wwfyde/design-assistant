from typing import Callable

from langgraph_tools.images import (
    image_create_with_gemini,
    image_create_with_seedream,
    image_create_with_seedream4_5,
)


def get_langgraph_tools(tools: list[str]) -> list[Callable]:
    tool_instances = []
    for tool in tools:
        if tool == "image_create_with_seedream":
            tool_instances.append(image_create_with_seedream)
        elif tool == "image_create_with_gemini":
            tool_instances.append(image_create_with_gemini)
        elif tool == "image_create_with_seedream4_5":
            tool_instances.append(image_create_with_seedream4_5)
        # elif tool.name == "web_search":
        #     tool_instances.append(web_search_tool)
        # elif tool.name ==
    return tool_instances


def main() -> None:
    print("Hello from langgraph-tools!")
