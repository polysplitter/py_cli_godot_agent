import httpx
from bs4 import BeautifulSoup

class GodotDocsClient:
    BASE_URL = "https://docs.godotengine.org/en/stable"

    def __init__(self) -> None:
        self.client = httpx.Client(
            timeout=10.0,
            follow_redirects=True,
        )

    def get_page(self, path: str) -> str:
        url = f"{self.BASE_URL}/{path.lstrip('/')}"

        response = self.client.get(url)
        response.raise_for_status()

        return response.text

    def get_page_text(self, path: str) -> str:
        html = self.get_page(path)

        soup = BeautifulSoup(html, "html.parser")

        content = (
            soup.select_one('div[itemprop="articleBody"]')
            or soup.select_one(".document")
            or soup.select_one('[role="main"]')
        )

        if content is None:
            raise ValueError(
                f"Could not find documentation content for: {path}"
            )

        return content.get_text(
            separator="\n",
            strip=True,
        )

    def get_class(self, class_name: str) -> str:
        normalized_name = class_name.strip().lower()

        path = f"classes/class_{normalized_name}.html"

        return self.get_page_text(path)


if __name__ == "__main__":
    docs = GodotDocsClient()

    page = docs.get_class("Timer")

    print(page[:3000])