from backend.search.providers.tavily_provider import TavilyProvider


def test_tavily_search():

    provider = TavilyProvider()

    results = provider.search(
        query="Impact of AI in Healthcare Diagnostics",
        max_results=3,
    )

    assert len(results) > 0

    for result in results:
        print("\n-----------------------------")
        print("Title :", result.title)
        print("URL   :", result.url)
        print("Source:", result.source)
        print("Content:")
        print(result.content[:250])


if __name__ == "__main__":
    test_tavily_search()