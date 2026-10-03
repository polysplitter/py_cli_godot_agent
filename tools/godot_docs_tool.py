from tools.godot_docs import GodotDocsClient
from tools.text_retriever import TextRetriever

class GodotDocsTool:
    def __init__(self) -> None:
        self.docs = GodotDocsClient()
        self.retriever = TextRetriever()

    def get_class_docs(self, class_name: str, max_chars: int = 12_000) -> str:
        """
        Retrieve documentation for a Godot class.
        """

        text = self.docs.get_class(class_name)
        return text[:max_chars]


    def search_class_docs(
            self,
            class_name: str,
            query:str,
            max_results: int = 5,
    ) -> str:

        text = self.docs.get_class(class_name)

        results = self.retriever.search(
            text=text,
            query=query,
            max_results=max_results,
        )

        return "\n\n---\n\n".join(
            result.text
            for result in results
        )


if __name__ == "__main__":
    tool = GodotDocsTool()

    result = tool.search_class_docs(
        class_name="CharacterBody2D",
        query="how does move_and_slide work?",
    )

    print(result)