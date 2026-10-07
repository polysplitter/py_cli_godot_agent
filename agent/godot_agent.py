from pathlib import Path

from providers.base import LLMProvider, Message
from agent.tool_router import parse_tool_request
from tools.godot_docs_tool import GodotDocsTool
from tools.godot_docs import GodotDocsError
from tools.godot_project_tool import GodotProjectTool


PROMPT_PATH = (
    Path(__file__).parent.parent
    / "prompts"
    / "system_prompt.txt"
)

TOOL_SELECTION_PROMPT = (
    Path(__file__).parent.parent
    / "prompts"
    / "tool_selection.txt"
)

class GodotAgent:

    def __init__(
            self, 
            provider: LLMProvider,
            docs_tool: GodotDocsTool,
            project_tool: GodotProjectTool | None = None,
            ) -> None:
        self.provider = provider
        self.docs_tool = docs_tool
        self.project_tool = project_tool

        system_prompt = PROMPT_PATH.read_text(
            encoding="utf-8"
        ).strip()

        self.tool_selection_prompt = TOOL_SELECTION_PROMPT.read_text(
            encoding="utf-8"
        ).strip()

        self.messages: list[Message] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

    def _select_tool(self):
        tool_messages: list[Message] = [
            {
                "role": "system",
                "content": self.tool_selection_prompt,
            },
            *self.messages[1:],
        ]

        response = self.provider.chat(tool_messages)

        return parse_tool_request(response)

    def _execute_tool(
            self,
            request,
            prompt: str,
    ) -> str | None:
        if request is None:
            return None

        if request.tool == "godot_docs":
            if not request.class_names:
                return None

            results: list[str] = []

            for class_name in request.class_names:
                try:
                    docs = self.docs_tool.search_class_docs(
                        class_name=class_name,
                        query=prompt,
                    )
                except GodotDocsError:
                    continue

                if docs:
                    results.append(
                        f"Godot class: {class_name}\n\n{docs}"
                    )

            if not results:
                return None

            return "\n\n=========\n\n".join(results)

        if request.tool == "godot_project":
            if self.project_tool is None:
                return None

            if request.action == "search_files":
                if not request.query:
                    return None

                matches = self.project_tool.search_files(
                    request.query
                )

                if not matches:
                    return None

                return "\n".join(matches)

        return None

    def ask(self, prompt: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        tool_request = self._select_tool()
        tool_context = self._execute_tool(tool_request, prompt)

        if tool_context:
            context_message: Message = {
                "role": "system",
                "content": (
                    "Use the following official Godot documentation "
                    "to help answer the user's latest question.\n\n"
                    f"{tool_context}"
                )
            }

            response_messages = [
                self.messages[0],
                context_message,
                *self.messages[1:],
            ]

            response = self.provider.chat(
                response_messages
            )
        else:
            response = self.provider.chat(
                self.messages
            )

        self.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        return response