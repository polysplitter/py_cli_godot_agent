import json
from dataclasses import dataclass


@dataclass
class ToolRequest:
    tool: str
    class_name: str | None = None


def parse_tool_request(response: str) -> ToolRequest | None:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return None

    tool = data.get("tool")

    if not tool:
        return None

    return ToolRequest(
        tool=tool,
        class_name=data.get("class_name"),
    )