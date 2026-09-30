from urllib.parse import urlsplit

from app.models.ats import ATSCandidate


SUPPORTED_ATS_HOSTS = {
    "jobs.lever.co": "lever",
    "jobs.ashbyhq.com": "ashby",
}


def detect_ats_candidate(
    url: str,
) -> ATSCandidate | None:
    parsed = urlsplit(url)

    hostname = (parsed.hostname or "").lower()
    provider = SUPPORTED_ATS_HOSTS.get(hostname)

    if provider is None:
        return None

    path_parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if not path_parts:
        return None

    slug = path_parts[0]

    return ATSCandidate(
        provider=provider,
        board_url=f"{parsed.scheme}://{hostname}/{slug}",
        slug=slug,
    )
