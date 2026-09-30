from app.services.ats_discovery import discover_ats_candidates


def test_discovers_ats_from_page_links() -> None:
    links = [
        "https://example.com/about",
        "https://jobs.lever.co/integrate",
        "https://example.com/contact",
    ]

    candidates = discover_ats_candidates(links)

    assert len(candidates) == 1
    assert candidates[0].provider == "lever"
    assert candidates[0].slug == "integrate"


def test_deduplicates_multiple_jobs_from_same_board() -> None:
    links = [
        "https://jobs.lever.co/integrate/job-123",
        "https://jobs.lever.co/integrate/job-456",
        "https://jobs.lever.co/integrate",
    ]

    candidates = discover_ats_candidates(links)

    assert len(candidates) == 1
    assert candidates[0].slug == "integrate"


def test_returns_empty_when_no_supported_ats_exists() -> None:
    links = [
        "https://example.com/about",
        "https://example.com/careers",
    ]

    candidates = discover_ats_candidates(links)

    assert candidates == []

import pytest

from app.services.ats_discovery import discover_ats_from_page


@pytest.mark.anyio
async def test_discovers_ats_from_browser_page() -> None:
    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="https://jobs.lever.co/example">
                View open positions
            </a>
        </body>
    </html>
    """

    candidates = await discover_ats_from_page(
        page_url="https://example.com/careers",
        html=html,
    )

    assert len(candidates) == 1
    assert candidates[0].provider == "lever"
    assert candidates[0].slug == "example"
