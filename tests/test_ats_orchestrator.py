import pytest

from app.models.ats import ATSCandidate
from app.models.discovery import DiscoveredSource
from app.models.evidence import EvidenceItem
from app.models.source import SourceResult
from app.services.ats_orchestrator import ATSOrchestrator
from app.services.search_queries import SearchQuery


async def fake_lever_board(company: str):
    if company == "Lever Company":
        return ATSCandidate(
            provider="lever",
            board_url="https://jobs.lever.co/lever-company",
            slug="lever-company",
        )

    return None


async def fake_ashby_board(company: str):
    if company == "Ashby Company":
        return ATSCandidate(
            provider="ashby",
            board_url="https://jobs.ashbyhq.com/ashby-company",
            slug="ashby-company",
        )

    return None


class FakeProvider:
    def __init__(
        self,
        candidate: ATSCandidate,
    ) -> None:
        self.candidate = candidate

    async def discover(
        self,
        queries: list[SearchQuery],
    ) -> list[DiscoveredSource]:
        return [
            DiscoveredSource(
                title="Software Engineer",
                url=f"{self.candidate.board_url}/job-123",
                purpose="role_requirements",
                provider=self.candidate.provider,
            )
        ]

    async def collect_evidence(
        self,
        queries: list[SearchQuery],
    ) -> list[EvidenceItem]:
        return [
            EvidenceItem(
                result=SourceResult(
                    source=self.candidate.provider,
                    title="Software Engineer",
                    url=(
                        f"{self.candidate.board_url}/job-123"
                    ),
                    content=(
                        "Software Engineer requirements include "
                        "Python, APIs, and distributed systems."
                    ),
                ),
                purpose="role_requirements",
                provider=self.candidate.provider,
            )
        ]


def fake_provider_factory(
    candidate: ATSCandidate,
) -> FakeProvider:
    return FakeProvider(candidate)


@pytest.mark.anyio
async def test_discovers_from_lever() -> None:
    orchestrator = ATSOrchestrator(
        board_discoverers=[
            fake_lever_board,
            fake_ashby_board,
        ],
        provider_factory=fake_provider_factory,
    )

    results = await orchestrator.discover(
        company="Lever Company",
        queries=[
            SearchQuery(
                purpose="role_requirements",
                query=(
                    '"Lever Company" '
                    '"Software Engineer" jobs requirements'
                ),
            )
        ],
    )

    assert len(results) == 1
    assert results[0].provider == "lever"


@pytest.mark.anyio
async def test_discovers_from_ashby() -> None:
    orchestrator = ATSOrchestrator(
        board_discoverers=[
            fake_lever_board,
            fake_ashby_board,
        ],
        provider_factory=fake_provider_factory,
    )

    results = await orchestrator.discover(
        company="Ashby Company",
        queries=[
            SearchQuery(
                purpose="role_requirements",
                query=(
                    '"Ashby Company" '
                    '"Software Engineer" jobs requirements'
                ),
            )
        ],
    )

    assert len(results) == 1
    assert results[0].provider == "ashby"


@pytest.mark.anyio
async def test_returns_empty_when_no_supported_board_exists() -> None:
    orchestrator = ATSOrchestrator(
        board_discoverers=[
            fake_lever_board,
            fake_ashby_board,
        ],
        provider_factory=fake_provider_factory,
    )

    results = await orchestrator.discover(
        company="Unknown Company",
        queries=[],
    )

    assert results == []


def test_builds_default_ats_orchestrator() -> None:
    from app.services.ats_orchestrator import (
        build_ats_orchestrator,
    )

    orchestrator = build_ats_orchestrator()

    assert len(orchestrator.board_discoverers) == 2


@pytest.mark.anyio
async def test_collects_evidence_from_detected_ats() -> None:
    orchestrator = ATSOrchestrator(
        board_discoverers=[
            fake_lever_board,
            fake_ashby_board,
        ],
        provider_factory=fake_provider_factory,
    )

    evidence = await orchestrator.collect_evidence(
        company="Ashby Company",
        queries=[
            SearchQuery(
                purpose="role_requirements",
                query=(
                    '"Ashby Company" '
                    '"Software Engineer" jobs requirements'
                ),
            )
        ],
    )

    assert len(evidence) == 1

    item = evidence[0]

    assert item.provider == "ashby"
    assert item.purpose == "role_requirements"
    assert item.result.source == "ashby"
    assert item.result.title == "Software Engineer"
    assert "distributed systems" in item.result.content
