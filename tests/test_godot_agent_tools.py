from providers.base import Message

from unittest.mock import Mock
from agent.godot_agent import GodotAgent
from tools.godot_docs_tool import GodotDocsTool


class FakeProvider:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls: list[list[Message]] = []

    def chat(
            self,
            messages: list[Message]
    ) -> str:
        self.calls.append(messages.copy())

        return self.responses.pop(0)


def test_agent_uses_godot_docs():
    provider = FakeProvider(
        responses=[
            '{"tool":"godot_docs","class_name":"Timer"}',
            "Use the timeout signal.",
        ]
    )

    docs_tool = Mock(spec=GodotDocsTool)

    docs_tool.search_class_docs.return_value = (
        "Official Timer documentation"
    )

    agent = GodotAgent(
        provider=provider,
        docs_tool=docs_tool
    )

    response = agent.ask(
        "How do I know when a Timer finishes?"
    )

    assert response == "Use the timeout signal."

    docs_tool.search_class_docs.assert_called_once_with(
        class_name="Timer",
        query="How do I know when a Timer finishes?",
    )

    assert len(provider.calls) == 2

    answer_messages = provider.calls[1]

    assert any(
        "Official Timer documentation"
        in message["content"]
        for message in answer_messages
    )