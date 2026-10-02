from agent.godot_agent import GodotAgent
from providers.ollama_provider import OllamaProvider

MODEL = "gemma4"


def main() -> None:
    provider = OllamaProvider(model=MODEL)
    agent = GodotAgent(provider)

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