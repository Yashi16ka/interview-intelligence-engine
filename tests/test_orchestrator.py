import pytest

from app.models.source import SourceResult
from app.services.collectors.base import BaseCollector
from app.services.collectors.mock import MockCollector
from app.services.orchestrator import ResearchOrchestrator


class FailingCollector(BaseCollector):
    @property
    def name(self) -> str:
        return "failing"

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        raise RuntimeError("Source unavailable")


@pytest.mark.anyio
async def test_orchestrator_collects_results() -> None:
    orchestrator = ResearchOrchestrator(
        collectors=[MockCollector()]
    )

    research = await orchestrator.research(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(research.results) == 1
    assert research.errors == []

    result = research.results[0]

    assert result.source == "mock"
    assert result.title == "Software Engineer Intern at Salesforce"
    assert str(result.url) == "https://example.com/interview"
    assert "Salesforce" in result.content


@pytest.mark.anyio
async def test_orchestrator_isolates_collector_failures() -> None:
    orchestrator = ResearchOrchestrator(
        collectors=[
            MockCollector(),
            FailingCollector(),
        ]
    )

    research = await orchestrator.research(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(research.results) == 1
    assert len(research.errors) == 1

    error = research.errors[0]

    assert error.source == "failing"
    assert error.error_type == "RuntimeError"
    assert error.message == "Source unavailable"


class DelayedCollector(BaseCollector):
    def __init__(self, collector_name: str, delay: float) -> None:
        self.collector_name = collector_name
        self.delay = delay

    @property
    def name(self) -> str:
        return self.collector_name

    async def collect(
        self,
        company: str,
        role: str,
    ) -> list[SourceResult]:
        import asyncio

        await asyncio.sleep(self.delay)

        return [
            SourceResult(
                source=self.name,
                title=f"{self.name} result",
                url=f"https://example.com/{self.name}",
                content=f"Research from {self.name}",
            )
        ]


@pytest.mark.anyio
async def test_concurrent_research_collects_all_results() -> None:
    orchestrator = ResearchOrchestrator(
        collectors=[
            DelayedCollector("source-a", 0.01),
            DelayedCollector("source-b", 0.01),
            DelayedCollector("source-c", 0.01),
        ]
    )

    research = await orchestrator.research(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(research.results) == 3
    assert research.errors == []


@pytest.mark.anyio
async def test_concurrent_research_isolates_failures() -> None:
    orchestrator = ResearchOrchestrator(
        collectors=[
            MockCollector(),
            FailingCollector(),
        ]
    )

    research = await orchestrator.research(
        company="Salesforce",
        role="Software Engineer Intern",
    )

    assert len(research.results) == 1
    assert len(research.errors) == 1
    assert research.errors[0].source == "failing"
