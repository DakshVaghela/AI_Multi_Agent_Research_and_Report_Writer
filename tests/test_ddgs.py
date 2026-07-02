from backend.search.providers.ddgs_provider import DDGSProvider


def test_ddgs_provider():

    provider = DDGSProvider()

    results = provider.search(
        "Artificial Intelligence in Healthcare",
        max_results=3,
    )

    assert len(results) > 0

    for result in results:
        print()
        print(result.title)
        print(result.url)