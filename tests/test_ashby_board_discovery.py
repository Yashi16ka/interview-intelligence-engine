import httpx
import pytest

from app.services.ashby_board_discovery import discover_ashby_board


@pytest.mark.anyio
async def test_discovers_valid_ashby_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        slug = request.url.path.rsplit("/", 1)[-1]

        if slug == "acme-ai":
            return httpx.Response(
                200,
                json={
                    "jobs": [
                        {
                            "title": "Software Engineer",
                            "jobUrl": (
                                "https://jobs.ashbyhq.com/"
                                "acme-ai/job-123"
                            ),
                        }
                    ]
                },
            )

        return httpx.Response(404)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_ashby_board(
            company="Acme AI",
            client=client,
        )

    assert candidate is not None
    assert candidate.provider == "ashby"
    assert candidate.slug == "acme-ai"
    assert str(candidate.board_url) == (
        "https://jobs.ashbyhq.com/acme-ai"
    )


@pytest.mark.anyio
async def test_returns_none_when_no_ashby_board_exists() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_ashby_board(
            company="Missing Company",
            client=client,
        )

    assert candidate is None


@pytest.mark.anyio
async def test_rejects_empty_ashby_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"jobs": []},
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_ashby_board(
            company="Empty Company",
            client=client,
        )

    assert candidate is None


@pytest.mark.anyio
async def test_rejects_board_with_mismatched_job_urls() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "title": "Software Engineer",
                        "jobUrl": (
                            "https://jobs.ashbyhq.com/"
                            "different-company/job-123"
                        ),
                    }
                ]
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_ashby_board(
            company="Example",
            client=client,
        )

    assert candidate is None
