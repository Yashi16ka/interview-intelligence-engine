import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol

from app.models.ats import ATSCandidate
from app.models.discovery import DiscoveredSource
from app.services.search_queries import SearchQuery


BoardDiscoverer = Callable[
    [str],
    Awaitable[ATSCandidate | None],
]


class ATSProvider(Protocol):
    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        ...


ProviderFactory = Callable[
    [ATSCandidate],
    ATSProvider,
]


class ATSOrchestrator:
    def __init__(
        self,
        board_discoverers: list[BoardDiscoverer],
        provider_factory: ProviderFactory,
    ) -> None:
        self.board_discoverers = board_discoverers
        self.provider_factory = provider_factory

    async def discover(
        self,
        company: str,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        board_results = await asyncio.gather(
            *[
                discover(company)
                for discover in self.board_discoverers
            ],
            return_exceptions=True,
        )

        candidates = [
            result
            for result in board_results
            if isinstance(result, ATSCandidate)
        ]

        if not candidates:
            return []

        provider_results = await asyncio.gather(
            *[
                self.provider_factory(
                    candidate
                ).discover(queries)
                for candidate in candidates
            ],
            return_exceptions=True,
        )

        discovered: list[DiscoveredSource] = []

        for result in provider_results:
            if isinstance(result, Exception):
                continue

            discovered.extend(result)

        return discovered


def build_ats_orchestrator() -> ATSOrchestrator:
    from app.services.ashby_board_discovery import (
        discover_ashby_board,
    )
    from app.services.ashby_discovery import (
        AshbyDiscoveryProvider,
    )
    from app.services.lever_board_discovery import (
        discover_lever_board,
    )
    from app.services.lever_discovery import (
        LeverDiscoveryProvider,
    )

    def provider_factory(
        candidate: ATSCandidate,
    ) -> ATSProvider:
        if candidate.provider == "lever":
            return LeverDiscoveryProvider(
                candidate=candidate,
            )

        if candidate.provider == "ashby":
            return AshbyDiscoveryProvider(
                candidate=candidate,
            )

        raise ValueError(
            f"Unsupported ATS provider: {candidate.provider}"
        )

    return ATSOrchestrator(
        board_discoverers=[
            discover_lever_board,
            discover_ashby_board,
        ],
        provider_factory=provider_factory,
    )
