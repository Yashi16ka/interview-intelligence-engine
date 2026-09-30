import httpx
import pytest

from app.services.lever_board_discovery import (
    discover_lever_board,
)


@pytest.mark.anyio
async def test_discovers_valid_lever_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        slug = request.url.path.split("/")[-1]

        if slug == "acme-ai":
            return httpx.Response(
                200,
                json=[
                    {
                        "text": "Software Engineer",
                        "hostedUrl": (
                            "https://jobs.lever.co/acme-ai/job-123"
                        ),
                    }
                ],
            )

        return httpx.Response(404)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_lever_board(
            company="Acme AI",
            client=client,
        )

    assert candidate is not None
    assert candidate.provider == "lever"
    assert candidate.slug == "acme-ai"
    assert str(candidate.board_url) == (
        "https://jobs.lever.co/acme-ai"
    )


@pytest.mark.anyio
async def test_returns_none_when_no_board_exists() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_lever_board(
            company="No Such Company",
            client=client,
        )

    assert candidate is None


@pytest.mark.anyio
async def test_rejects_empty_lever_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[],
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_lever_board(
            company="Empty Company",
            client=client,
        )

    assert candidate is None


@pytest.mark.anyio
async def test_rejects_board_with_mismatched_posting_urls() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "text": "Software Engineer",
                    "hostedUrl": (
                        "https://jobs.lever.co/"
                        "different-company/job-123"
                    ),
                }
            ],
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        candidate = await discover_lever_board(
            company="Example",
            client=client,
        )

    assert candidate is None
