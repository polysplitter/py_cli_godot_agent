from providers.base import Message

from unittest.mock import Mock, call
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
            '{"tool":"godot_docs","class_names":["Timer"]}',
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

def test_agent_uses_multiple_godot_docs():
    prompt = (
        "How do I start a Timer when "
        "the player enters an Area2D?"
    )

    provider = FakeProvider(
        responses=[
            (
                '{"tool":"godot_docs",'
                '"class_names":["Area2D","Timer"]}'
            ),
            "Connect body_entered to start the Timer.",
        ]
    )

    docs_tool = Mock(spec=GodotDocsTool)

    docs_tool.search_class_docs.side_effect = [
        "Official Area2D documentation",
        "Official Timer documentation",
    ]

    agent = GodotAgent(
        provider=provider,
        docs_tool=docs_tool,
    )

    response = agent.ask(prompt)

    assert response == (
        "Connect body_entered to start the Timer."
    )

    assert docs_tool.search_class_docs.call_count == 2

    docs_tool.search_class_docs.assert_has_calls(
        [
            call(
                class_name="Area2D",
                query=prompt,
            ),
            call(
                class_name="Timer",
                query=prompt,
            ),
        ]
    )

    assert len(provider.calls) == 2

    answer_messages = provider.calls[1]

    assert any(
        "Official Area2D documentation"
        in message["content"]
        for message in answer_messages
    )

    assert any(
        "Official Timer documentation"
        in message["content"]
        for message in answer_messages
    )