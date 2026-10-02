from agent.godot_agent import GodotAgent
from providers.base import LLMProvider, Message
from unittest.mock import Mock

from tools.godot_docs_tool import GodotDocsTool

class FakeProvider(LLMProvider):

    def chat(self, messages: list[Message]) -> str:
        return "Fake Godot response"

def test_agent_returns_provider_response() -> None:
    provider = FakeProvider()
    docs_tool = Mock(spec=GodotDocsTool)  
    agent = GodotAgent(
        provider=provider,
        docs_tool=docs_tool,
    )

    response = agent.ask(
        "How do I create a CharacterBody2D"
    )

    assert response == "Fake Godot response"

def test_agent_remembers_conversation() -> None:
    provider = FakeProvider()
    docs_tool = Mock(spec=GodotDocsTool)  
    agent = GodotAgent(
        provider=provider,
        docs_tool=docs_tool,
    )

    agent.ask("Create a player controller.")
    agent.ask("Add jumping to it.")

    assert len(agent.messages) == 5

    assert agent.messages[1]["role"] == "user"
    assert agent.messages[1]["content"] == (
        "Create a player controller."
    )

    assert agent.messages[2]["role"] == "assistant"

    assert agent.messages[3]["role"] == "user"
    assert agent.messages[3]["content"] == (
        "Add jumping to it."
    )