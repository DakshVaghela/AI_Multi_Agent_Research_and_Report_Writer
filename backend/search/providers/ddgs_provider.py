from ddgs import DDGS

from backend.models.search_result import SearchResult
from backend.search.providers.base_provider import BaseSearchProvider


class DDGSProvider(BaseSearchProvider):

    def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        results = []

        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results,
            )

            for item in search_results:
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("href", ""),
                        content=item.get("body", ""),
                        source="ddgs",
                    )
                )

        return results