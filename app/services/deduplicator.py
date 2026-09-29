import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.models.source import SourceResult


TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)

    query_parameters = [
        (key, value)
        for key, value in parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_PARAMETERS
    ]

    path = parts.path.rstrip("/") or "/"

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            urlencode(query_parameters),
            "",
        )
    )


def title_key(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    title = re.sub(r"\s+", " ", title)

    return title.strip()


def deduplicate_sources(
    results: list[SourceResult],
) -> list[SourceResult]:
    unique_results: list[SourceResult] = []

    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for result in results:
        url_key = canonicalize_url(str(result.url))
        normalized_title = title_key(result.title)

        if url_key in seen_urls:
            continue

        if normalized_title and normalized_title in seen_titles:
            continue

        seen_urls.add(url_key)

        if normalized_title:
            seen_titles.add(normalized_title)

        unique_results.append(result)

    return unique_results
