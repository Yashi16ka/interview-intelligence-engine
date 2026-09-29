import asyncio

from app.models.discovery import (
    DiscoveryError,
    DiscoveryResults,
)
from app.services.discovery import DiscoveryProvider
from app.services.search_queries import SearchQuery


class DiscoveryOrchestrator:
    def __init__(
        self,
        providers: list[DiscoveryProvider],
    ) -> None:
        self.providers = providers

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> DiscoveryResults:
        tasks = [
            provider.discover(queries)
            for provider in self.providers
        ]

        outcomes = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        sources = []
        errors = []

        for provider, outcome in zip(
            self.providers,
            outcomes,
            strict=True,
        ):
            if isinstance(outcome, BaseException):
                errors.append(
                    DiscoveryError(
                        provider=provider.name,
                        error_type=type(outcome).__name__,
                        message=str(outcome),
                    )
                )
            else:
                sources.extend(outcome)

        return DiscoveryResults(
            sources=sources,
            errors=errors,
        )
