import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

from backend.models.search_result import SearchResult
from backend.search.providers.base_provider import BaseSearchProvider


class WikipediaProvider(BaseSearchProvider):

    def search(
        self,
        query: str,
        max_results: int = 1,
    ) -> list[SearchResult]:

        try:
            titles = wikipedia.search(query, results=max_results)

            print(f"\nSearch Query: {query}")
            print(f"Titles Found: {titles}")

            if not titles:
                return []

            page = wikipedia.page(titles[0])

            print(f"Resolved Page: {page.title}")

            return [
                SearchResult(
                    title=page.title,
                    url=page.url,
                    content=page.summary,
                    source="wikipedia",
                )
            ]

        except Exception as e:
            print(f"\nWikipedia Error: {e}")
            return []