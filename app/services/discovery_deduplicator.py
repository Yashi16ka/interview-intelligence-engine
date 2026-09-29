from app.models.discovery import DiscoveredSource
from app.services.deduplicator import canonicalize_url


def deduplicate_discovered_sources(
    sources: list[DiscoveredSource],
) -> list[DiscoveredSource]:
    unique_sources: list[DiscoveredSource] = []
    seen_urls: set[str] = set()

    for source in sources:
        url_key = canonicalize_url(str(source.url))

        if url_key in seen_urls:
            continue

        seen_urls.add(url_key)
        unique_sources.append(source)

    return unique_sources
