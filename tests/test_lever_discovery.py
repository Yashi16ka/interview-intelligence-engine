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
