from unittest.mock import Mock

from tools.godot_docs_tool import GodotDocsTool


def test_get_class_docs():
    tool = GodotDocsTool()

    tool.docs.get_class = Mock(return_value="Timer documentation")

    result = tool.get_class_docs("Timer")

    assert result == "Timer documentation"

    tool.docs.get_class.assert_called_once_with("Timer")


def test_get_class_docs_truncates_result():
    tool = GodotDocsTool()

    tool.docs.get_class = Mock(return_value="1234567890")

    result = tool.get_class_docs("Timer", max_chars=5,)

    assert result == "12345"