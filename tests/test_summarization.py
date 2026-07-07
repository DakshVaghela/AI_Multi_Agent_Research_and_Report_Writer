from backend.services.summarization_service import summarization_service


def test_summarization():

    article = """
Artificial Intelligence is transforming healthcare diagnostics.
Machine learning models help radiologists detect diseases earlier.
AI also improves workflow efficiency and supports clinical decision making.
"""

    result = summarization_service.summarize(article)

    print("\nSummary:\n")
    print(result.summary)

    print("\nKey Points:")
    for point in result.key_points:
        print("-", point)

    assert len(result.summary) > 20