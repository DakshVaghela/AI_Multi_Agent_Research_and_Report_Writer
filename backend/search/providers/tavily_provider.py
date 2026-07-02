from tavily import TavilyClient

from backend.config.settings import settings
from backend.models.search_result import SearchResult
from backend.search.providers.base_provider import BaseSearchProvider


class TavilyProvider(BaseSearchProvider):
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        response = self.client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
        )

        results: list[SearchResult] = []

        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    source="tavily",
                )
            )

        return results