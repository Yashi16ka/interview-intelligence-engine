import asyncio
from urllib.parse import urlsplit

import httpx

from app.models.ats import ATSCandidate
from app.services.ats_slugs import build_company_slugs


BASE_URL = "https://api.lever.co/v0/postings"


def _posting_matches_slug(
    hosted_url: str,
    slug: str,
) -> bool:
    parsed = urlsplit(hosted_url)

    if (parsed.hostname or "").lower() != "jobs.lever.co":
        return False

    path_parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if not path_parts:
        return False

    return path_parts[0].lower() == slug.lower()


async def _probe_slug(
    slug: str,
    client: httpx.AsyncClient,
) -> ATSCandidate | None:
    response = await client.get(
        f"{BASE_URL}/{slug}",
        params={"mode": "json"},
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or not data:
        return None

    has_matching_posting = any(
        isinstance(job, dict)
        and isinstance(job.get("hostedUrl"), str)
        and _posting_matches_slug(
            hosted_url=job["hostedUrl"],
            slug=slug,
        )
        for job in data
    )

    if not has_matching_posting:
        return None

    return ATSCandidate(
        provider="lever",
        board_url=f"https://jobs.lever.co/{slug}",
        slug=slug,
    )


async def discover_lever_board(
    company: str,
    client: httpx.AsyncClient | None = None,
) -> ATSCandidate | None:
    slugs = build_company_slugs(company)

    if not slugs:
        return None

    owns_client = client is None

    http_client = client or httpx.AsyncClient(
        timeout=10.0,
        follow_redirects=True,
    )

    try:
        tasks = [
            _probe_slug(
                slug=slug,
                client=http_client,
            )
            for slug in slugs
        ]

        candidates = await asyncio.gather(*tasks)

        for candidate in candidates:
            if candidate is not None:
                return candidate

        return None
    finally:
        if owns_client:
            await http_client.aclose()
