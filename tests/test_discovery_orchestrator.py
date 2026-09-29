import asyncio
import time

import pytest

from app.models.discovery import DiscoveredSource
from app.services.discovery import DiscoveryProvider
from app.services.discovery_orchestrator import DiscoveryOrchestrator
from app.services.search_queries import SearchQuery


class SlowDiscoveryProvider(DiscoveryProvider):
    def __init__(
        self,
        name: str,
        delay: float,
    ) -> None:
        self._name = name
        self.delay = delay

    @property
    def name(self) -> str:
        return self._name

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        await asyncio.sleep(self.delay)

        return [
            DiscoveredSource(
                title=f"{self.name} result",
                url=f"https://example.com/{self.name}",
                purpose=queries[0].purpose,
                provider=self.name,
            )
        ]


class FailingDiscoveryProvider(DiscoveryProvider):
    @property
    def name(self) -> str:
        return "failing"

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        raise RuntimeError("Discovery unavailable")


@pytest.mark.anyio
async def test_discovery_runs_concurrently() -> None:
    orchestrator = DiscoveryOrchestrator(
        providers=[
            SlowDiscoveryProvider("first", 0.15),
            SlowDiscoveryProvider("second", 0.15),
        ]
    )

    queries = [
        SearchQuery(
            purpose="interview_experience",
            query="example query",
        )
    ]

    start = time.perf_counter()

    result = await orchestrator.discover(queries)

    elapsed = time.perf_counter() - start

    assert len(result.sources) == 2
    assert result.errors == []

    assert elapsed < 0.25


@pytest.mark.anyio
async def test_discovery_isolates_failures() -> None:
    orchestrator = DiscoveryOrchestrator(
        providers=[
            SlowDiscoveryProvider("working", 0.01),
            FailingDiscoveryProvider(),
        ]
    )

    queries = [
        SearchQuery(
            purpose="interview_questions",
            query="example query",
        )
    ]

    result = await orchestrator.discover(queries)

    assert len(result.sources) == 1
    assert result.sources[0].provider == "working"

    assert len(result.errors) == 1
    assert result.errors[0].provider == "failing"
    assert result.errors[0].error_type == "RuntimeError"
