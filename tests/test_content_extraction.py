from backend.services.content_extraction_service import (
    content_extraction_service,
)


def test_content_extraction():

    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

    content = content_extraction_service.extract(url)

    assert len(content) > 100

    print("\nFirst 500 characters:\n")
    print(content[:500])