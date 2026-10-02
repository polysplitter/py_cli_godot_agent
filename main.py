from agent.godot_agent import GodotAgent
from providers.ollama_provider import OllamaProvider
from tools.godot_docs_tool import GodotDocsTool

MODEL = "gemma4"


def main() -> None:
    provider = OllamaProvider(model=MODEL)
    docs_tool = GodotDocsTool()

    agent = GodotAgent(
        provider=provider,
        docs_tool=docs_tool,
    )

    print(f"Godot Agent ({MODEL})")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        prompt = input("\nYou > ").strip()

        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not prompt:
            continue

        try:
            response = agent.ask(prompt)
            print(f"\nAgent > {response}")
        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()