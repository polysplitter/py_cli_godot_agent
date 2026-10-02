import ollama

from providers.base import LLMProvider, Message


class OllamaProvider(LLMProvider):

    def __init__(self, model: str) -> None:
        self.model = model

    def chat(self, messages: list[Message]) -> str:

        response = ollama.chat(
            model=self.model,
            messages=messages,
        )

        return response.message.content