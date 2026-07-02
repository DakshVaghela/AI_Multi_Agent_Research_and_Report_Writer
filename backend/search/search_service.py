from backend.models.search_result import SearchResult
from backend.search.providers.ddgs_provider import DDGSProvider
from backend.search.providers.tavily_provider import TavilyProvider


class SearchService:
    def __init__(self):
        self.providers = [
            TavilyProvider(),
            DDGSProvider(),
        ]

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        merged_results: list[SearchResult] = []

        seen_urls = set()

        for provider in self.providers:
            try:
                results = provider.search(
                    query=query,
                    max_results=max_results,
                )

                for result in results:

                    if str(result.url) in seen_urls:
                        continue

                    seen_urls.add(str(result.url))
                    merged_results.append(result)

            except Exception as e:
                print(f"{provider.__class__.__name__} failed: {e}")

        return merged_results[:max_results]


search_service = SearchService()