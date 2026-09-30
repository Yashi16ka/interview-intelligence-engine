import asyncio
from urllib.parse import urlsplit

import httpx

from app.models.ats import ATSCandidate
from app.services.ats_slugs import build_company_slugs


BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"


def _job_matches_slug(
    job_url: str,
    slug: str,
) -> bool:
    parsed = urlsplit(job_url)

    if (parsed.hostname or "").lower() != "jobs.ashbyhq.com":
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
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        return None

    jobs = data.get("jobs")

    if not isinstance(jobs, list) or not jobs:
        return None

    has_matching_job = any(
        isinstance(job, dict)
        and isinstance(job.get("jobUrl"), str)
        and _job_matches_slug(
            job_url=job["jobUrl"],
            slug=slug,
        )
        for job in jobs
    )

    if not has_matching_job:
        return None

    return ATSCandidate(
        provider="ashby",
        board_url=f"https://jobs.ashbyhq.com/{slug}",
        slug=slug,
    )


async def discover_ashby_board(
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
