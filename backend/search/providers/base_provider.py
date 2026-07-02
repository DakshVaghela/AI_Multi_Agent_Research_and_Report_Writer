from abc import ABC, abstractmethod

from backend.models.search_result import SearchResult


class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """
        Search for a query and return standardized search results.
        """
        pass