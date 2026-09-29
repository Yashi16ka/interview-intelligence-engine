from abc import ABC, abstractmethod

from app.models.source import SourceResult


class BaseCollector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this collector."""
        raise NotImplementedError

    @abstractmethod
    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        """Collect relevant source material for a company and role."""
        raise NotImplementedError
