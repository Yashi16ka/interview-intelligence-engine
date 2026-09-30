import httpx
import pytest

from app.models.ats import ATSCandidate
from app.services.lever_discovery import LeverDiscoveryProvider
from app.services.search_queries import SearchQuery


@pytest.mark.anyio
async def test_lever_discovers_matching_role() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "text": "Machine Learning Intern",
                    "hostedUrl": "https://jobs.lever.co/example/123",
                    "descriptionPlain": (
                        "Build machine learning systems with Python."
                    ),
                },
                {
                    "text": "Product Designer",
                    "hostedUrl": "https://jobs.lever.co/example/456",
                    "descriptionPlain": "Design product experiences.",
                },
            ],
        )

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )

    candidate = ATSCandidate(
        provider="lever",
        board_url="https://jobs.lever.co/example",
        slug="example",
    )

    provider = LeverDiscoveryProvider(
        candidate=candidate,
        client=client,
    )

    try:
        results = await provider.discover(
            queries=[
                SearchQuery(
                    purpose="role_requirements",
                    query='"Example" "Machine Learning Intern" jobs requirements',
                )
            ]
        )
    finally:
        await client.aclose()

    assert len(results) == 1
    assert results[0].title == "Machine Learning Intern"
    assert (
        str(results[0].url)
        == "https://jobs.lever.co/example/123"
    )
    assert results[0].purpose == "role_requirements"
    assert results[0].provider == "lever"


@pytest.mark.anyio
async def test_lever_ignores_non_role_queries() -> None:
    candidate = ATSCandidate(
        provider="lever",
        board_url="https://jobs.lever.co/example",
        slug="example",
    )

    provider = LeverDiscoveryProvider(
        candidate=candidate,
    )

    results = await provider.discover(
        queries=[
            SearchQuery(
                purpose="interview_experience",
                query='"Example" interview experience',
            )
        ]
    )

    assert results == []


@pytest.mark.anyio
async def test_collects_lever_job_evidence_from_api_content() -> None:
    requests_made = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests_made
        requests_made += 1

        return httpx.Response(
            200,
            json=[
                {
                    "text": "Software Engineer",
                    "hostedUrl": (
                        "https://jobs.lever.co/"
                        "example/123"
                    ),
                    "descriptionPlain": (
                        "Example is hiring a Software Engineer. "
                        "Requirements include Python, REST APIs, "
                        "distributed systems, and PostgreSQL."
                    ),
                },
                {
                    "text": "Product Designer",
                    "hostedUrl": (
                        "https://jobs.lever.co/"
                        "example/456"
                    ),
                    "descriptionPlain": (
                        "Design product experiences."
                    ),
                },
            ],
        )

    candidate = ATSCandidate(
        provider="lever",
        board_url="https://jobs.lever.co/example",
        slug="example",
    )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        provider = LeverDiscoveryProvider(
            candidate=candidate,
            client=client,
        )

        evidence = await provider.collect_evidence(
            queries=[
                SearchQuery(
                    purpose="role_requirements",
                    query=(
                        '"Example" "Software Engineer" '
                        "jobs requirements"
                    ),
                )
            ]
        )

    assert requests_made == 1
    assert len(evidence) == 1

    item = evidence[0]

    assert item.purpose == "role_requirements"
    assert item.provider == "lever"
    assert item.result.source == "lever"
    assert item.result.title == "Software Engineer"
    assert str(item.result.url) == (
        "https://jobs.lever.co/example/123"
    )
    assert "distributed systems" in item.result.content
    assert "PostgreSQL" in item.result.content
