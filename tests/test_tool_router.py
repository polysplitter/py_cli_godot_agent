from agent.tool_router import parse_tool_request


def test_parse_godot_docs_request():
    response = """
{
    "tool": "godot_docs",
    "class_name": "Timer",
}
"""

    request = parse_tool_request(response)

    assert request is not None
    assert request.tool == "godot_docs"
    assert request.class_name == "Timer"
