from urllib.parse import urlsplit

from app.models.ats import ATSCandidate


def detect_ats_candidate(
    url: str,
) -> ATSCandidate | None:
    parsed = urlsplit(url)

    hostname = (parsed.hostname or "").lower()

    if hostname == "jobs.lever.co":
        path_parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if not path_parts:
            return None

        slug = path_parts[0]

        return ATSCandidate(
            provider="lever",
            board_url=f"https://jobs.lever.co/{slug}",
            slug=slug,
        )

    return None
