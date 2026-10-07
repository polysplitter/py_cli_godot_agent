import json
from dataclasses import dataclass, field


@dataclass
class ToolRequest:
    tool: str
    class_names: list[str] = field(default_factory=list)
    action: str | None = None
    query: str | None = None
    path: str | None = None


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

    action = data.get("action")
    query = data.get("query")
    path = data.get("path")

    return ToolRequest(
        tool=tool,
        class_names=class_names,
        action=action,
        query=query,
        path=path,
    )