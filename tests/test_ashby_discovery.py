import httpx
import pytest

from app.models.ats import ATSCandidate
from app.services.ashby_discovery import AshbyDiscoveryProvider
from app.services.search_queries import SearchQuery


@pytest.mark.anyio
async def test_discovers_matching_ashby_jobs() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "title": "Machine Learning Intern",
                        "jobUrl": (
                            "https://jobs.ashbyhq.com/"
                            "acme/job-123"
                        ),
                    },
                    {
                        "title": "Product Designer",
                        "jobUrl": (
                            "https://jobs.ashbyhq.com/"
                            "acme/job-456"
                        ),
                    },
                ]
            },
        )

    candidate = ATSCandidate(
        provider="ashby",
        board_url="https://jobs.ashbyhq.com/acme",
        slug="acme",
    )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        provider = AshbyDiscoveryProvider(
            candidate=candidate,
            client=client,
        )

        results = await provider.discover(
            queries=[
                SearchQuery(
                    purpose="role_requirements",
                    query='"Acme" "Machine Learning Intern" jobs requirements',
                )
            ]
        )

    assert len(results) == 1
    assert results[0].title == "Machine Learning Intern"
    assert results[0].purpose == "role_requirements"
    assert results[0].provider == "ashby"
    assert str(results[0].url) == (
        "https://jobs.ashbyhq.com/acme/job-123"
    )


@pytest.mark.anyio
async def test_ignores_non_role_queries() -> None:
    requests_made = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests_made
        requests_made += 1

        return httpx.Response(
            200,
            json={"jobs": []},
        )

    candidate = ATSCandidate(
        provider="ashby",
        board_url="https://jobs.ashbyhq.com/acme",
        slug="acme",
    )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        provider = AshbyDiscoveryProvider(
            candidate=candidate,
            client=client,
        )

        results = await provider.discover(
            queries=[
                SearchQuery(
                    purpose="interview_experience",
                    query='"Acme" "Software Engineer" interview experience',
                )
            ]
        )

    assert results == []
    assert requests_made == 0


@pytest.mark.anyio
async def test_collects_ashby_job_evidence_from_api_content() -> None:
    requests_made = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests_made
        requests_made += 1

        return httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "title": "Software Engineer",
                        "jobUrl": (
                            "https://jobs.ashbyhq.com/"
                            "acme/job-123"
                        ),
                        "descriptionPlain": (
                            "Acme is hiring a Software Engineer. "
                            "Requirements include Python, APIs, "
                            "distributed systems, and PostgreSQL."
                        ),
                    },
                    {
                        "title": "Product Designer",
                        "jobUrl": (
                            "https://jobs.ashbyhq.com/"
                            "acme/job-456"
                        ),
                        "descriptionPlain": (
                            "Design product experiences."
                        ),
                    },
                ]
            },
        )

    candidate = ATSCandidate(
        provider="ashby",
        board_url="https://jobs.ashbyhq.com/acme",
        slug="acme",
    )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        provider = AshbyDiscoveryProvider(
            candidate=candidate,
            client=client,
        )

        evidence = await provider.collect_evidence(
            queries=[
                SearchQuery(
                    purpose="role_requirements",
                    query=(
                        '"Acme" "Software Engineer" '
                        "jobs requirements"
                    ),
                )
            ]
        )

    assert requests_made == 1
    assert len(evidence) == 1

    item = evidence[0]

    assert item.purpose == "role_requirements"
    assert item.provider == "ashby"
    assert item.result.source == "ashby"
    assert item.result.title == "Software Engineer"
    assert str(item.result.url) == (
        "https://jobs.ashbyhq.com/acme/job-123"
    )
    assert "distributed systems" in item.result.content
    assert "PostgreSQL" in item.result.content
