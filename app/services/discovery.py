from abc import ABC, abstractmethod

from app.models.discovery import DiscoveredSource
from app.services.search_queries import SearchQuery


class DiscoveryProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Identifier for this discovery provider."""
        raise NotImplementedError

    @abstractmethod
    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        """Discover candidate URLs for research queries."""
        raise NotImplementedError
