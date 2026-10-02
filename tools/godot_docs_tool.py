from tools.godot_docs import GodotDocsClient

class GodotDocsTool:
    def __init__(self) -> None:
        self.docs = GodotDocsClient()

    def get_class_docs(self, class_name: str, max_chars: int = 12_000) -> str:
        """
        Retrieve documentation for a Godot class.
        """

        text = self.docs.get_class(class_name)
        return text[:max_chars]


if __name__ == "__main__":
    tool = GodotDocsTool()

    result = tool.get_class_docs("Timer")

    print(result)