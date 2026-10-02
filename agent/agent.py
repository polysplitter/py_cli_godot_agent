from pathlib import Path
from providers.base import LLMProvider, Message

PROMPT_PATH = (
    Path(__file__).parent.parent
    / "prompts"
    / "system_prompt.txt"
)

class GodotAgent:

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

        system_prompt = PROMPT_PATH.read_text(
            encoding="utf-8"
        ).strip()

        self.messages: list[Message] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

    def ask(self, prompt: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response =  self.provider.chat(self.messages)

        self.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        return response