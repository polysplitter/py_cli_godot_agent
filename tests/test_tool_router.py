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


def test_parse_project_search_request():
    response = """
    {
        "tool": "godot_project",
        "action": "search_files",
        "query": "jump"
    }
    """

    request = parse_tool_request(response)

    assert request is not None
    assert request.tool == "godot_project"
    assert request.action == "search_files"
    assert request.query == "jump"
    assert request.path is None
    assert request.class_names == []

def test_parse_project_read_file_request():
    response = """
    {
        "tool": "godot_project",
        "action": "read_file",
        "path": "scripts/player.gd"
    }
    """

    request = parse_tool_request(response)

    assert request is not None
    assert request.tool == "godot_project"
    assert request.action == "read_file"
    assert request.path == "scripts/player.gd"
    assert request.query is None
    assert request.class_names == []