from backend.search.search_service import search_service


def test_search_service():

    results = search_service.search(
        query="Impact of AI in Healthcare Diagnostics",
        max_results=5,
    )

    assert len(results) > 0

    print(f"\nTotal Results: {len(results)}\n")

    for index, result in enumerate(results, start=1):
        print("=" * 70)
        print(f"Result {index}")
        print("=" * 70)
        print(f"Provider : {result.source}")
        print(f"Title    : {result.title}")
        print(f"URL      : {result.url}")
        print(f"Content  : {result.content[:200]}")
        print()