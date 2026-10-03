import re
from dataclasses import dataclass

@dataclass
class SearchResult:
    text: str
    score: int


class TextRetriever:

    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "does",
        "for",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "the",
        "to",
        "what",
        "when",
        "with",
        "work",
    }

    def _score(
            self,
            chunk: str,
            query: str,
    ) -> int:

        query_terms = self._tokenize(query)
        chunk_terms = self._tokenize(chunk)

        score = 0

        for term in query_terms:
            if term in chunk_terms:
                score += 1

        chunk_lower = chunk.lower()

        for term in query_terms:
            if "_" in term and term in chunk_lower:
                score += 5

        return score


    def search(
            self,
            text: str,
            query: str,
            max_results: int = 5,
    ) -> list[SearchResult]:

        chunks = self._chunk_text(text)

        results: list[SearchResult] = []

        for chunk in chunks:

            score = self._score(
                chunk=chunk,
                query=query,
            )

            if score > 0:
                results.append(
                    SearchResult(
                        text=chunk,
                        score=score,
                    )
                )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:max_results]

    def _chunk_text(
            self,
            text: str,
            chunk_size: int = 1200,
    ) -> list[str]:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for line in lines:
            line_length = len(line) + 1

            if (
                current_chunk
                and current_length + line_length > chunk_size
            ):

                chunks.append(
                    " ".join(current_chunk)
                )

                current_chunk = []
                current_length = 0

            current_chunk.append(line)
            current_length += line_length

        if current_chunk:
            chunks.append(
                " ".join(current_chunk)
            )

        return chunks

    def _tokenize(self, text: str) -> set[str]:
        terms = set(
            re.findall(
                r"\b[a-zA-Z0-9_]+\b",
                text.lower(),
            )
        )

        return terms - self.STOP_WORDS