from agent.agent import GodotAgent
from providers.base import LLMProvider, Message

class FakeProvider(LLMProvider):

    def chat(self, messages: list[Message]) -> str:
        return "Fake Godot response"

def test_agent_returns_provider_response() -> None:
    provider = FakeProvider()
    agent = GodotAgent(provider)

    response = agent.ask(
        "How do I create a CharacterBody2D"
    )

    assert response == "Fake Godot response"

def test_agent_remembers_conversation() -> None:
    provider = FakeProvider()
    agent = GodotAgent(provider)

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