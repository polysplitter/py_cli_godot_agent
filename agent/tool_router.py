import json
from dataclasses import dataclass


@dataclass
class ToolRequest:
    tool: str
    class_names: list[str]


def parse_tool_request(response: str) -> ToolRequest | None:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return None

    tool = data.get("tool")

    if not tool:
        return None

    class_names = data.get("class_names", [])

    if not isinstance(class_names, list):
        return None

    return ToolRequest(
        tool=tool,
        class_names=class_names,
    )