from agent.tool_router import parse_tool_request


def test_parse_godot_docs_request():
    response = """
{
    "tool": "godot_docs",
    "class_names": ["Timer"]
}
"""

    request = parse_tool_request(response)

    assert request is not None
    assert request.tool == "godot_docs"
    assert request.class_names == ["Timer"]


def test_parse_multiple_godot_docs_classes():
    response = """
    {
        "tool": "godot_docs",
        "class_names": ["Area2D", "Timer"]
    }
    """

    request = parse_tool_request(response)

    assert request is not None
    assert request.tool == "godot_docs"
    assert request.class_names == [
        "Area2D",
        "Timer",
    ]


def test_parse_none_request():
    response = """
    {
        "tool": "none"
    }
    """

    request = parse_tool_request(response)

    assert request is not None
    assert request.tool == "none"
    assert request.class_names == []


def test_invalid_json_returns_none():
    response = "this is not json"

    request = parse_tool_request(response)

    assert request is None