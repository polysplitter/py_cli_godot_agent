from abc import ABC, abstractmethod
from typing import TypedDict


class Message(TypedDict):
    role: str
    content: str


class LLMProvider(ABC):

    @abstractmethod
    def chat(self, messages: list[Message]) -> str:
        """Send a prompt to the LLM and return its response."""
        ...