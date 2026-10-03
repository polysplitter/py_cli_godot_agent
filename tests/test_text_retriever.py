from tools.text_retriever import TextRetriever

def test_search_returns_relevant_chunk():
    retriever = TextRetriever()

    text = """
    Timer is a countdown timmer.

    The timeout signal is emitted when the timer reaches zero.

    The start method starts the timer.
    """

    results = retriever.search(
        text=text,
        query="What signal does the timer emit?"
    )

    assert len(results) > 0
    assert "timeout signal" in results[0].text


def test_search_limits_results():
    retriever = TextRetriever()

    text = "\n".join(
        f"Timer information {number}"
        for number in range(100)
    )

    results = retriever.search(
        text=text,
        query="Timer",
        max_results=2,
    )

    assert len(results) <= 2