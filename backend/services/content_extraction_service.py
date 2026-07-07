import trafilatura
from trafilatura.settings import use_config

# A slow/unresponsive source shouldn't be able to stall the whole research
# phase -- fail fast and move on to the next result instead of trafilatura's
# generous default timeout.
_CONFIG = use_config()
_CONFIG.set("DEFAULT", "DOWNLOAD_TIMEOUT", "8")


class ContentExtractionService:
    """
    Extracts clean textual content from web pages.
    """

    def extract(self, url: str) -> str:
        downloaded = trafilatura.fetch_url(url, config=_CONFIG)

        if not downloaded:
            return ""

        content = trafilatura.extract(downloaded)

        return content or ""


content_extraction_service = ContentExtractionService()