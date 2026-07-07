import trafilatura


class ContentExtractionService:
    """
    Extracts clean textual content from web pages.
    """

    def extract(self, url: str) -> str:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        content = trafilatura.extract(downloaded)

        return content or ""


content_extraction_service = ContentExtractionService()