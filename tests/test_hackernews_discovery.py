import httpx
import pytest

from app.services.hackernews_discovery import (
    HackerNewsDiscoveryProvider,
)
from app.services.search_queries import SearchQuery


@pytest.mark.anyio
async def test_hackernews_discovery_preserves_query_purpose() -> None:
    async def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        query = request.url.params["query"]

        return httpx.Response(
            200,
            json={
                "hits": [
                    {
                        "objectID": "123",
                        "title": f"Result for {query}",
                        "url": "https://example.com/interview",
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as client:
        provider = HackerNewsDiscoveryProvider(
            client=client,
        )

        results = await provider.discover(
            [
                SearchQuery(
                    purpose="interview_experience",
                    query='"Example" interview experience',
                ),
                SearchQuery(
                    purpose="technical_interview",
                    query='"Example" technical interview',
                ),
            ]
        )

    assert len(results) == 2

    assert {
        result.purpose
        for result in results
    } == {
        "interview_experience",
        "technical_interview",
    }

    assert all(
        result.provider == "hackernews"
        for result in results
    )


@pytest.mark.anyio
async def test_hackernews_discovery_uses_hn_url_when_external_url_missing(
) -> None:
    async def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "hits": [
                    {
                        "objectID": "456",
                        "title": "Interview discussion",
                        "url": None,
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as client:
        provider = HackerNewsDiscoveryProvider(
            client=client,
        )

        results = await provider.discover(
            [
                SearchQuery(
                    purpose="interview_questions",
                    query='"Example" interview questions',
                )
            ]
        )

    assert len(results) == 1
    assert str(results[0].url) == (
        "https://news.ycombinator.com/item?id=456"
    )


@pytest.mark.anyio
async def test_hackernews_discovery_uses_provider_specific_queries() -> None:
    requested_queries: list[str] = []

    async def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        requested_queries.append(
            request.url.params["query"]
        )

        return httpx.Response(
            200,
            json={"hits": []},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as client:
        provider = HackerNewsDiscoveryProvider(
            client=client,
        )

        await provider.discover(
            [
                SearchQuery(
                    purpose="interview_experience",
                    query=(
                        '"Microsoft" "Software Engineer Intern" '
                        "interview experience"
                    ),
                    company="Microsoft",
                    role="Software Engineer Intern",
                ),
                SearchQuery(
                    purpose="interview_questions",
                    query=(
                        '"Microsoft" "Software Engineer Intern" '
                        "interview questions"
                    ),
                    company="Microsoft",
                    role="Software Engineer Intern",
                ),
                SearchQuery(
                    purpose="technical_interview",
                    query=(
                        '"Microsoft" "Software Engineer Intern" '
                        "technical interview"
                    ),
                    company="Microsoft",
                    role="Software Engineer Intern",
                ),
                SearchQuery(
                    purpose="company_engineering",
                    query='"Microsoft" engineering technology',
                    company="Microsoft",
                    role="Software Engineer Intern",
                ),
            ]
        )

    assert requested_queries == [
        "Microsoft interview",
        "Microsoft interview questions",
        "Microsoft Software Engineer Intern interview",
        "Microsoft engineering",
    ]


@pytest.mark.anyio
async def test_hackernews_discovery_skips_role_requirements() -> None:
    request_count = 0

    async def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            200,
            json={"hits": []},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as client:
        provider = HackerNewsDiscoveryProvider(
            client=client,
        )

        results = await provider.discover(
            [
                SearchQuery(
                    purpose="role_requirements",
                    query=(
                        '"Microsoft" "Software Engineer Intern" '
                        "jobs requirements"
                    ),
                    company="Microsoft",
                    role="Software Engineer Intern",
                )
            ]
        )

    assert results == []
    assert request_count == 0


@pytest.mark.anyio
async def test_hackernews_discovery_filters_hits_without_company_signal(
) -> None:
    async def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "hits": [
                    {
                        "objectID": "100",
                        "title": (
                            "How to Integrate Infosec and DevOps "
                            "Using Chaos Engineering"
                        ),
                        "story_text": None,
                        "url": "https://example.com/false-positive",
                    },
                    {
                        "objectID": "200",
                        "title": "Integrate engineering architecture",
                        "story_text": (
                            "Engineers at Integrate discuss "
                            "their platform architecture."
                        ),
                        "url": "https://example.com/integrate",
                    },
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as client:
        provider = HackerNewsDiscoveryProvider(
            client=client,
        )

        results = await provider.discover(
            [
                SearchQuery(
                    purpose="company_engineering",
                    query='"Integrate" engineering technology',
                    company="Integrate",
                    role="Software Engineer",
                )
            ]
        )

    assert len(results) == 1
    assert results[0].title == (
        "Integrate engineering architecture"
    )
    assert str(results[0].url) == (
        "https://example.com/integrate"
    )
