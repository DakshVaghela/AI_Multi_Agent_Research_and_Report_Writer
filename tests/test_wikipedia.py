from backend.search.providers.wikipedia_provider import WikipediaProvider


def test_wikipedia_provider():

    provider = WikipediaProvider()

    results = provider.search(
        "Artificial Intelligence in Healthcare"
    )

    assert len(results) == 1

    result = results[0]

    print("\nTitle :", result.title)
    print("URL   :", result.url)
    print("\nSummary:\n")
    print(result.content[:500])